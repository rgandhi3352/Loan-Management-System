from celery import shared_task
import csv
from .models import User, Transaction

@shared_task
def calculate_credit_score(aadhar_id):
    user = User.objects.get(aadhar_id=aadhar_id)
    
    # Process transactions from CSV
    process_csv('/Users/raghavgandhi/Downloads/transactions_data_backend__1_.csv', user)

    # Calculate total balance based on transaction data
    transactions = Transaction.objects.filter(user=user)
    total_balance = sum(
        transaction.amount if transaction.transaction_type == 'CREDIT' else -transaction.amount
        for transaction in transactions
    )

    # Calculate credit score logic
    if total_balance >= 1000000:
        credit_score = 900
    elif total_balance <= 100000:
        credit_score = 300
    else:
        credit_score = 300 + (total_balance - 100000) // 15000 * 10

    user.credit_score = int(credit_score)
    user.save()

def process_csv(file_path, user):
    # Read and process the CSV file
    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['user'] == user.aadhar_id:
                Transaction.objects.create(
                    user=user,
                    date=row['date'],
                    amount=row['amount'],
                    transaction_type=row['transaction_type']
                )

