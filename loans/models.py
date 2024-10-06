from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import timedelta
from django.utils import timezone
from django.http import JsonResponse
import uuid

class User(models.Model):
    aadhar_id = models.CharField(max_length=12, unique=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    annual_income = models.DecimalField(max_digits=12, decimal_places=2)
    credit_score = models.IntegerField(default=300)
    unique_user_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def __str__(self):
        return self.name

class Transaction(models.Model):
    aadhar_id = models.CharField(max_length=12)
    date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=6, choices=(('CREDIT', 'CREDIT'), ('DEBIT', 'DEBIT')))

class Loan(models.Model):
    LOAN_TYPES = (
        ('Car', 'Car'),
        ('Home', 'Home'),
        ('Education', 'Education'),
        ('Personal', 'Personal'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    loan_type = models.CharField(max_length=50, choices=LOAN_TYPES)
    loan_amount = models.DecimalField(max_digits=15, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=14.00)
    term_period = models.IntegerField()  # In months
    disbursement_date = models.DateField()
    loan_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    # status = models.CharField(max_length=20, default='Active')

    def __str__(self):
        return f"{self.loan_type} Loan for {self.user.name}"

class EMI(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE)
    due_date = models.DateField()
    emi_amount = models.DecimalField(max_digits=10, decimal_places=2)
    principal_due = models.DecimalField(max_digits=10, decimal_places=2)
    interest_due = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    payment_date = models.DateField(null=True, blank=True)
    amount_due = models.DecimalField(max_digits=12, decimal_places=2)  # Total amount due for this EMI
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"EMI for Loan ID {self.loan.id} - Due Date: {self.date} - Amount Due: {self.amount_due} - Paid: {self.is_paid}"

    @property
    def is_overdue(self):
        return not self.is_paid and self.date < timezone.now().date()

    def mark_as_paid(self):
        self.is_paid = True
        self.save()

    def record_partial_payment(self, amount):
        self.amount_paid += amount
        self.amount_due -= amount
        if self.amount_due <= 0:
            self.mark_as_paid()
        self.save()

    def remaining_balance(self):
        return self.amount_due - self.amount_paid

    def make_full_payment(self):
        self.amount_paid = self.amount_due
        self.mark_as_paid()
