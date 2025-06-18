from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal

class Loan(models.Model):
    LOAN_TERM_WEEKS = 50
    INTEREST_RATE = Decimal(0.10)  # 10% annual

    loan_id = models.CharField(max_length=50, unique=True)
    principal_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    start_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-start_date']

    @property
    def total_amount(self):
        """Total repayment amount (principal + interest)"""
        return round(self.principal_amount * (1 + self.INTEREST_RATE), 2)

    @property
    def weekly_payment(self):
        """Fixed weekly payment amount"""
        return round(self.total_amount / self.LOAN_TERM_WEEKS, 2)

    @property
    def current_week(self):
        """Calculate current week number based on start date"""
        days_passed = (timezone.now().date() - self.start_date).days
        return min((days_passed // 7) + 1, self.LOAN_TERM_WEEKS)

    def get_outstanding_balance(self):
        """Calculate remaining amount to be paid"""
        total_paid = self.payments.aggregate(
            total=models.Sum('amount')
        )['total'] or 0
        return max(self.total_amount - total_paid, 0)

    def get_next_payment_week(self):
        """Returns the next week number that needs payment"""
        last_paid_week = self.payments.aggregate(
            max_week=models.Max('week_number')
        )['max_week'] or 0

        # Find the earliest missed week (if any)
        for week in range(1, last_paid_week + 2):
            if not self.payments.filter(week_number=week).exists():
                return week

        # If all previous weeks are paid, return next in schedule
        next_week = last_paid_week + 1
        return next_week if next_week <= self.LOAN_TERM_WEEKS else None

    def __str__(self):
        return f"Loan {self.loan_id} (Rp {self.principal_amount:,})"

class Payment(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=12, decimal_places=2, editable=False)
    payment_date = models.DateTimeField(auto_now_add=True)
    week_number = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ['week_number']
        unique_together = ('loan', 'week_number')
        verbose_name = 'Repayment'

    def save(self, *args, **kwargs):
        """Auto-set payment amount to the loan's weekly payment"""
        if not self.amount:
            self.amount = self.loan.weekly_payment
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Week {self.week_number} payment for {self.loan}"

class LoanStatus(models.Model):
    loan = models.OneToOneField(
        Loan,
        on_delete=models.CASCADE,
        related_name='status'
    )
    is_delinquent = models.BooleanField(default=False)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Loan statuses'

    def check_delinquent_status(self):
        """Update delinquency status based on recent payments"""
        current_week = self.loan.current_week

        # Check if we have at least 2 weeks to evaluate
        if current_week <= 1:
            self.is_delinquent = False
        else:
            # Check if both current week and previous week are unpaid
            recent_payments = self.loan.payments.filter(
                week_number__in=[current_week, current_week - 1]
            ).values_list('week_number', flat=True)

            # Delinquent if both weeks are missing payments
            self.is_delinquent = len(recent_payments) < 2

        self.save()

    def __str__(self):
        status = "Delinquent" if self.is_delinquent else "Current"
        return f"{status} (as of {self.last_updated.date()})"
