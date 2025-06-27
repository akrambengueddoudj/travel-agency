from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Main pages
    path('', views.index, name='index'),
    
    # Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    
    # Password reset (optional)
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='auth/password_reset.html'
    ), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='auth/password_reset_done.html'
    ), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='auth/password_reset_confirm.html'
    ), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='auth/password_reset_complete.html'
    ), name='password_reset_complete'),
    
    # Packages
    path('packages/', views.package_list, name='package-list'),
    path('packages/<int:pk>/', views.package_detail, name='package-detail'),
    path('packages/create/', views.create_package, name='create-package'),
    
    # Reservations
    path('reservations/', views.reservation_list, name='reservation-list'),
    path('reservations/<int:pk>/', views.reservation_detail, name='reservation-detail'),
    path('packages/<int:package_id>/reserve/', views.create_reservation, name='create-reservation'),
    
    # Payment
    path('payment/', views.payment_view, name='payment'),
    
    # Profile
    path('profile/', views.profile_view, name='profile'),
    
    # Admin
    path('admin/dashboard/', views.admin_dashboard, name='admin-dashboard'),
    path('admin/assign-role/', views.assign_role_view, name='assign-role'),
    
    # API Proxy
    path('api/<str:endpoint>/', views.api_proxy, name='api-proxy'),
    
    # API endpoints that need template responses
    path('api/quotation/', views.api_proxy, name='quotation'),
    path('api/payment/initiate/', views.api_proxy, name='payment-initiate'),
    path('api/payment/show/', views.api_proxy, name='payment-show'),
]