from rest_framework import viewsets, permissions, serializers, generics, filters, status
from .models import TravelPackage, Reservation
from .serializers import TravelPackageSerializer, ReservationSerializer, EmailTokenObtainPairSerializer, RegisterSerializer, UserProfileSerializer, UserWithProfileSerializer, UserSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.models import User, Group
from .permissions import IsAdmin, IsSeller, IsManager
from django.core.mail import send_mail
from .guiddini_service import initiate_payment, show_transaction
import requests
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils import timezone

# =========================
# Travel Package ViewSet
# =========================
class TravelPackageViewSet(viewsets.ModelViewSet):
    queryset = TravelPackage.objects.all()
    serializer_class = TravelPackageSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'description']

    def get_permissions(self):
        if self.action in ['create', 'update', 'destroy']:
            return [IsAdmin()]
        return []

# =========================
# Reservation ViewSet
# =========================
class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer

    def create(self, request, *args, **kwargs):
        # Decrement seats logic
        package_id = request.data.get('travel_package')
        number_of_people = int(request.data.get('number_of_people'))
        if not TravelPackage.objects.filter(id=package_id).exists():
            print(package_id)
            print(number_of_people)
            return Response({'error': 'Travel package not found'}, status=404)
        package = TravelPackage.objects.get(id=package_id)

        if package.available_seats >= number_of_people:
            package.available_seats -= number_of_people
            package.save()

            # Send confirmation email
            send_mail(
                'Reservation Confirmation',
                f'Your reservation for {package.title} has been confirmed.',
                'noreply@travelagency.com',
                [request.data.get('customer_email')],
                fail_silently=True
            )

            return super().create(request, *args, **kwargs)
        else:
            return Response({'error': 'Not enough seats available'}, status=400)

    def get_permissions(self):
        if self.action == 'list':
            return [IsAdmin() or IsSeller()]
        return []

class InstantQuotationView(APIView):

    @swagger_auto_schema(
        operation_description="Calculate the instant quotation based on travel package and number of people.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['travel_package', 'number_of_people'],
            properties={
                'travel_package': openapi.Schema(type=openapi.TYPE_INTEGER, description='Travel Package ID'),
                'number_of_people': openapi.Schema(type=openapi.TYPE_INTEGER, description='Number of people for reservation'),
            },
        )
    )
    def post(self, request, *args, **kwargs):
        try:
            package_id = request.data.get('travel_package')
            number_of_people = int(request.data.get('number_of_people'))

            if not package_id or not number_of_people:
                return Response({'error': 'Please provide travel_package and number_of_people.'},
                                status=status.HTTP_400_BAD_REQUEST)

            try:
                package = TravelPackage.objects.get(id=package_id)
            except TravelPackage.DoesNotExist:
                return Response({'error': 'Travel package not found.'}, status=status.HTTP_404_NOT_FOUND)

            if number_of_people > package.available_seats:
                return Response({'error': 'Not enough seats available.'}, status=status.HTTP_400_BAD_REQUEST)

            total_price = number_of_people * float(package.price)

            return Response({
                'travel_package': package.title,
                'price_per_person': float(package.price),
                'number_of_people': number_of_people,
                'total_price': total_price,
                'available_seats': package.available_seats
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# =========================
# Email Authentication (JWT)
# =========================

class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer


# =========================
# Create User (JWT)
# =========================
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

# Create user with profile
class RegisterWithProfileView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserWithProfileSerializer

# Create profile for existing user
class CreateUserProfileView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # Return the profile of the currently logged-in user
        user = self.request.user
        if hasattr(user, 'profile'):
            return user.profile
        return None


    def get(self, request, *args, **kwargs):
        profile = self.get_object()
        if profile is None:
            return Response(
                {'detail': 'Profile not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer(profile)
        return Response(serializer.data)
    
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        if hasattr(user, 'profile'):
            return Response({'error': 'User already has a profile.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=user)
        return Response({'message': 'Profile created successfully.'}, status=status.HTTP_201_CREATED)
    
    def put(self, request, *args, **kwargs):
        profile = self.get_object()
        if profile is None:
            return Response(
                {'detail': 'Profile not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer(profile, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

# Admin-only: Assign role to user by email
class AssignRoleView(generics.GenericAPIView):
    permission_classes = [IsAdmin]

    @swagger_auto_schema(
        operation_description="Assign a role to a user based on email.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'role'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='User email'),
                'role': openapi.Schema(type=openapi.TYPE_STRING, description='Role to assign (Admin, Seller, Manager)'),
            },
        )
    )
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        role = request.data.get('role')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        group, created = Group.objects.get_or_create(name=role)
        user.groups.clear()  # optional: clear old roles
        user.groups.add(group)

        return Response({'message': f'Role {role} assigned to {user.email}.'}, status=status.HTTP_200_OK)

# guidini
class InitiatePaymentView(APIView):
    permission_classes = [permissions.AllowAny]  # Change based on your need

    @swagger_auto_schema(
        operation_description="Initiate payment for a reservation using Guiddini.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['amount'],
            properties={
                'amount': openapi.Schema(type=openapi.TYPE_STRING, description='Payment amount'),
            },
        )
    )
    def post(self, request):
        amount = request.data.get('amount')
        if not amount:
            return Response({'error': 'Amount is required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            attrs = initiate_payment(amount)
            return Response(attrs, status=status.HTTP_200_OK)
        except requests.HTTPError as e:
            return Response({'error': str(e), 'details': e.response.text}, status=status.HTTP_502_BAD_GATEWAY)

class ShowTransactionView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Check the payment status using the order number (mdOrder) provided by Guiddini.",
        manual_parameters=[
            openapi.Parameter(
                'order_number',
                openapi.IN_QUERY,
                description="Order number from payment initiation (mdOrder).",
                type=openapi.TYPE_STRING,
                required=True
            )
        ]
    )
    def get(self, request):
        order_number = request.query_params.get('order_number')
        if not order_number:
            return Response({'error': 'order_number is required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            attrs = show_transaction(order_number)
            return Response(attrs, status=status.HTTP_200_OK)
        except requests.HTTPError as e:
            return Response({'error': str(e)}, status=status.HTTP_502_BAD_GATEWAY)


# users me
@api_view(['GET'])
def current_user(request):
    return Response({
        'username': request.user.username,
        'email': request.user.email,
        'is_staff': request.user.is_staff
    })

class UserListView(generics.ListAPIView):
    """
    View to list all users (Admin only)
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]  # Only admin can access
    pagination_class = None

@api_view(['GET'])
def reservation_stats(request):
    now = timezone.now()
    
    # Total packages count
    total_packages = TravelPackage.objects.count()
    
    # Active reservations - trips that haven't ended yet
    active_reservations = Reservation.objects.filter(
        travel_package__end_date__gte=now  # End date is in future
    ).count()
    
    # Total revenue - sum of all reservation totals
    # Calculate based on package price * number of people
    total_revenue = sum(
        reservation.travel_package.price * reservation.number_of_people
        for reservation in Reservation.objects.all()
    )
    
    return Response({
        'total_packages': total_packages,
        'active_reservations': active_reservations,
        'total_revenue': float(total_revenue)
    })