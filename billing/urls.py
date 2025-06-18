from . import views as api_views
from django.urls import path

urlpatterns = [
    path("", api_views.index, name="index"),
    path('loans/', api_views.LoanCreateView.as_view(), name='loan-create'),
    path('loans/<str:loan_id>/schedule/', api_views.LoanScheduleView.as_view(), name='loan-schedule'),
    path('loans/<str:loan_id>/outstanding/',api_views. OutstandingBalanceView.as_view(), name='outstanding-balance'),
    path('payments/', api_views.PaymentCreateView.as_view(), name='payment-create'),
    path('loans/<str:loan_id>/status/', api_views.LoanStatusView.as_view(), name='loan-status'),
]
