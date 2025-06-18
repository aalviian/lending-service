from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import generics, status
from rest_framework.response import Response
from .models import Loan, Payment, LoanStatus
from .serializers import LoanSerializer, PaymentSerializer, LoanStatusSerializer, LoanScheduleSerializer
from django.utils import timezone


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

class LoanCreateView(generics.CreateAPIView):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer

    def perform_create(self, serializer):
        loan = serializer.save()
        # Create a status record for the new loan
        LoanStatus.objects.create(loan=loan)

class LoanScheduleView(generics.RetrieveAPIView):
    queryset = Loan.objects.all()
    serializer_class = LoanScheduleSerializer
    lookup_field = 'loan_id'

class OutstandingBalanceView(generics.RetrieveAPIView):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer
    lookup_field = 'loan_id'

    def retrieve(self, request, *args, **kwargs):
        loan = self.get_object()
        total_paid = sum(
            payment.amount for payment in loan.payments.all()
        )
        outstanding = loan.total_amount - total_paid
        return Response({'outstanding_balance': float(outstanding)})

class PaymentCreateView(generics.CreateAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    def create(self, request, *args, **kwargs):
        loan_id = request.data.get('loan')
        try:
            loan = Loan.objects.get(loan_id=loan_id)
        except Loan.DoesNotExist:
            return Response(
                {'error': 'Loan not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Auto-determine next payable week
        next_week = loan.get_next_payment_week()
        if not next_week:
            return Response(
                {"error": "Loan is already fully paid"},
                status=400
            )

        # Calculate current week number
        days_since_start = (timezone.now().date() - loan.start_date).days
        current_week = min((days_since_start // 7) + 1, loan.LOAN_TERM_WEEKS)

        # Check if payment already exists for this week
        if Payment.objects.filter(loan=loan, week_number=current_week).exists():
            return Response(
                {"error": f"Payment already exists for current week (Week {current_week})"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create payment
        payment = Payment.objects.create(
            loan=loan,
            amount=loan.weekly_payment,
            week_number=next_week  # Auto-assigned
        )
        # Update delinquent status
        loan.status.check_delinquent_status()

        serializer = self.get_serializer(payment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class LoanStatusView(generics.RetrieveAPIView):
    queryset = LoanStatus.objects.all()
    serializer_class = LoanStatusSerializer

    def get_object(self):
        loan_id = self.kwargs.get('loan_id')
        loan = Loan.objects.get(loan_id=loan_id)
        return loan.status