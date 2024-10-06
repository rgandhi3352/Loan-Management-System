from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User, Loan, EMI, Transaction
from .serializers import UserSerializer
from .tasks import calculate_credit_score
from django.db import transaction
from django.shortcuts import get_object_or_404
from .emi_calculator import calculate_emi

# Register User API with async credit score calculation
class RegisterUserView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            calculate_credit_score.delay(user.aadhar_id)  # Trigger Celery task
            return Response({"unique_user_id": user.unique_user_id}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Apply Loan API
class ApplyLoanView(APIView):
    def post(self, request):
        with transaction.atomic():
            loan_type = request.data.get('loan_type')
            loan_amount = request.data.get('loan_amount')
            interest_rate = request.data.get('interest_rate')
            term_period = request.data.get('term_period')  # in months
            disbursement_date = request.data.get('disbursement_date')
            user = get_object_or_404(User, unique_user_id=request.data['unique_user_id'])
            if user.credit_score < 450 or user.annual_income < 150000:
                return Response({"error": "Loan application criteria not met."}, status=status.HTTP_400_BAD_REQUEST)

            if not self.validate_loan_amount(loan_type, loan_amount):
                return Response({"error": "Loan amount not within bounds."}, status=status.HTTP_400_BAD_REQUEST)
            try:
                emi_schedule, total_interest = calculate_emi(
                    loan_amount, 
                    interest_rate, 
                    term_period, 
                    disbursement_date, 
                    user.annual_income / 12  # Monthly income
                )
            except ValueError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

            loan = Loan.objects.create(
                user=user,
                loan_type=loan_type,
                loan_amount=loan_amount,
                interest_rate=interest_rate,
                term_period=term_period,
                disbursement_date=disbursement_date,
                total_interest=total_interest
            )

            # Save EMI schedule to the database
            for emi in emi_schedule:
                EMI.objects.create(
                    loan=loan,
                    due_date=emi['Date'],
                    emi_amount=emi['EMI_Amount'],
                    principal_due = emi['Principal'],
                    interest_due = emi['Interest'],
                    amount_due = emi['EMI_Amount']
                )

            return Response({
                'Loan_id': loan.loan_id,
                'Due_dates': [
                    {
                        'Date': emi['Date'],
                        'Amount_due': emi['EMI_Amount']
                    } for emi in emi_schedule
                ]
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def validate_loan_amount(self, loan_type, amount):
        limits = {'Car': 750000, 'Home': 8500000, 'Education': 5000000, 'Personal': 1000000}
        return amount <= limits[loan_type]

class MakePaymentView(APIView):
    def post(self, request):
        loan_id = request.data.get('loan_id')
        payment_amount = request.data.get('amount')
        
        if not loan_id or not payment_amount:
            return Response({"Error": "Loan ID and Amount are required"}, status=400)
        
        try:
            loan = Loan.objects.get(id=loan_id)
        except Loan.DoesNotExist:
            return Response({"Error": "Loan does not exist"}, status=400)
        
        # Check for any previous unpaid EMIs
        # Lock the loan and associated EMIs to prevent concurrent modifications
        unpaid_emis = loan.emis.select_for_update().filter(is_paid=False).order_by('date')

        if not unpaid_emis.exists():
            return Response({"Error": "No outstanding EMIs to be paid"}, status=400)
        remaining_amount = payment_amount
        for emi in unpaid_emis:
            if remaining_amount <= 0:
                break
            if remaining_amount >= emi.amount_due:
                # Full payment for this EMI
                emi.make_full_payment()
                remaining_amount -= emi.amount_due
            else:
                # Partial payment for this EMI
                emi.record_partial_payment(remaining_amount)
                remaining_amount = 0

      ### We can update the interest due and principal due as well if we receive payments early or late, not doing this here because
      ### of limited time for the assignment

      # If there's still remaining payment, return it as excess
        response_data = {
            "Success": "Payment processed",
            "Excess_Payment": remaining_amount if remaining_amount > 0 else 0,
        }

        return Response(response_data, status=200)

class GetStatementView(APIView):
    def get(self, request):
        loan = Loan.objects.get(id=request.query_params['loan_id'])

        # Fetch past EMIs
        past_emis = EMI.objects.filter(loan=loan, is_paid=True)
        past_transactions = []
        for emi in paid_emis:
            past_transactions.append({
            'date': emi.due_date,
            'principal': emi.principal_due,
            'interest': emi.interest_due,
            'amount_paid': emi.amount_paid,
          })

        # Fetch upcoming EMIs
        upcoming_emis = EMI.objects.filter(loan=loan, is_paid=False)
        upcoming_transactions = []
        for emi in upcoming_emis:
            upcoming_transactions.append({
                'date': emi.due_date,
                'amount_due': emi.emi_amount,
            })

        # Return the past and upcoming EMI statements
        response = {
            'past_transactions': past_transactions,
            'upcoming_transactions': upcoming_transactions,
        }

        return JsonResponse(response, status=200)

