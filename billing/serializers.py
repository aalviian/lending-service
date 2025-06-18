from rest_framework import serializers
from .models import Loan, Payment, LoanStatus

class LoanSerializer(serializers.ModelSerializer):
    weekly_payment = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Loan
        fields = ['loan_id', 'principal_amount', 'start_date', 'weekly_payment', 'total_amount']

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'loan', 'amount', 'payment_date']
        read_only_fields = ['amount']

class LoanStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanStatus
        fields = ['is_delinquent', 'last_updated']

class LoanScheduleSerializer(serializers.ModelSerializer):
    schedule = serializers.SerializerMethodField()

    class Meta:
        model = Loan
        fields = ['loan_id', 'schedule']

    def get_schedule(self, obj):
        schedule = {}
        payments = {p.week_number: p for p in obj.payments.all()}

        for week in range(1, obj.LOAN_TERM_WEEKS + 1):
            schedule[f"W{week}"] = {
                "due_amount": float(obj.weekly_payment),
                "paid": week in payments,  # True if paid, False if unpaid
                "payment_date": payments[week].payment_date if week in payments else None
            }
        return schedule