from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TravelPackageViewSet, ReservationViewSet
from rest_framework_simplejwt.views import TokenRefreshView
from .views import EmailTokenObtainPairView, RegisterView, RegisterWithProfileView, CreateUserProfileView, AssignRoleView, InstantQuotationView, InitiatePaymentView, ShowTransactionView, current_user, UserListView, reservation_stats
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="Smart Travel Agency API",
        default_version='v1',
        description="API Documentation for Smart Travel Agency System",
        contact=openapi.Contact(email="group7@guiddini.dz"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

router = DefaultRouter()
router.register('packages', TravelPackageViewSet)
router.register('reservations', ReservationViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('login/', EmailTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', RegisterView.as_view(), name='register'),
    path('register_with_profile/', RegisterWithProfileView.as_view(), name='register_with_profile'),
    path('create_profile/', CreateUserProfileView.as_view(), name='create_profile'),
    path('assign_role/', AssignRoleView.as_view(), name='assign_role'),
    path('quotation/', InstantQuotationView.as_view(), name='instant_quotation'),
    path('payment/initiate/', InitiatePaymentView.as_view(), name='payment_initiate'),
    path('payment/show/', ShowTransactionView.as_view(), name='payment_show'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('users/me/', current_user, name='current-user'),
    path('users/', UserListView.as_view(), name='user-list'),
    path('reservations_stats/', reservation_stats, name='reservation-stats')
    # path('swagger.yaml', schema_view.without_ui(cache_timeout=0, renderer_classes=[openapi.renderers.OpenAPIRenderer]), name='schema-yaml'),
]
