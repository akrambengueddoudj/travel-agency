from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_http_methods
from django.contrib.auth import login, logout
from django.contrib import messages
from django.http import JsonResponse
import requests
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from api.models import TravelPackage, Reservation
from api.serializers import ReservationSerializer

def index(request):
    """Home page view"""
    return render(request, 'index.html')

@require_http_methods(["GET", "POST"])
def login_view(request):
    """Handle user login"""
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            response = requests.post(
                'http://127.0.0.1:8000/api/login/',
                json={'email': email, 'password': password}
            )
            response.raise_for_status()  # Raises exception for 4XX/5XX errors
            
            auth_data = response.json()
            request.session['access_token'] = auth_data.get('access')
            request.session['refresh_token'] = auth_data.get('refresh')
            
            # Get user details
            user_response = requests.get(
                'http://127.0.0.1:8000/api/users/me/',
                headers={'Authorization': f'Bearer {auth_data.get("access")}'}
            )
            user_data = user_response.json()
            
            # Create or update user
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'username': user_data.get('username', email.split('@')[0]),
                    'is_active': True
                }
            )
            
            login(request, user)
            return redirect('index')
            
        except requests.exceptions.RequestException as e:
            messages.error(request, 'Invalid credentials')
            return redirect('login')
    
    return render(request, 'auth/login.html')
def logout_view(request):
    """Handle user logout"""
    logout(request)
    if 'auth_token' in request.session:
        del request.session['auth_token']
    return redirect('index')

def register_view(request):
    """Handle user registration"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        response = requests.post(
            'http://127.0.0.1:8000/api/register/',
            json={
                'username': username,
                'email': email,
                'password': password
            }
        )
        
        if response.status_code == 201:
            messages.success(request, 'Registration successful! Please login.')
            return redirect('login')
        
        messages.error(request, 'Registration failed')
        return redirect('register')
    
    return render(request, 'auth/register.html')


def package_list(request):
    """List all travel packages"""
    return render(request, 'packages/list.html')


def package_detail(request, pk):
    """Show package details"""
    if TravelPackage.objects.filter(id=pk).exists():
        return render(request, 'packages/detail.html', {'package_id': pk, 'package': TravelPackage.objects.get(id=pk)})
    else:
        return redirect(package_list)


def create_package(request):
    """Create a new package"""
    return render(request, 'packages/form.html')


def create_reservation(request, package_id):
    """Create a new reservation"""
    return render(request, 'reservations/form.html', {'package_id': package_id})


def reservation_list(request):
    """List user's reservations"""
    return render(request, 'reservations/list.html')


def reservation_detail(request, pk):
    """Show reservation details"""
    if Reservation.objects.filter(id=pk).exists():
        reservation = Reservation.objects.get(id=pk)
        # serialize reservation using ReservationSerializer
        serializer = ReservationSerializer(reservation)
        return render(request, 'reservations/detail.html', {'reservation_id': pk, 'reservation': serializer.data, 'reservation_created_at': reservation.created_at})
    else:
        return redirect(reservation_list)

@login_required
def payment_view(request):
    """Handle payment process"""
    reservation_id = request.GET.get('reservation_id')
    if not reservation_id:
        return redirect('index')
    
    return render(request, 'payment/payment.html', {
        'reservation_id': reservation_id
    })


def admin_dashboard(request):
    """Admin dashboard view"""
    return render(request, 'admin/dashboard.html')


def assign_role_view(request):
    """Assign roles to users"""
    return render(request, 'admin/assign_role.html')


def profile_view(request):
    """User profile view"""
    return render(request, 'profile.html')

# API proxy views to handle CSRF and session authentication
@csrf_exempt  # Temporarily exempt for testing, remove in production
def api_proxy(request, endpoint):
    """Proxy API requests to add CSRF and session handling"""
    api_url = f'http://127.0.0.1:8000/api/{endpoint}/'
    headers = {
        'Content-Type': 'application/json',
    }
    
    # Forward the authorization header if it exists
    auth_header = request.headers.get('Authorization')
    if auth_header:
        headers['Authorization'] = auth_header
    elif request.user.is_authenticated and 'access_token' in request.session:
        headers['Authorization'] = f'Bearer {request.session["access_token"]}'
    
    try:
        if request.method == 'GET':
            response = requests.get(
                api_url,
                headers=headers,
                params=request.GET
            )
        elif request.method == 'POST':
            response = requests.post(
                api_url,
                headers=headers,
                json=request.POST.dict() or None
            )
        elif request.method == 'PUT':
            response = requests.put(
                api_url,
                headers=headers,
                json=request.POST.dict() or None
            )
        elif request.method == 'PATCH':
            response = requests.patch(
                api_url,
                headers=headers,
                json=request.POST.dict() or None
            )
        elif request.method == 'DELETE':
            response = requests.delete(
                api_url,
                headers=headers
            )
        else:
            return JsonResponse({'error': 'Method not allowed'}, status=405)
        
        # Handle token refresh if 401
        if response.status_code == 401 and 'refresh_token' in request.session:
            refresh_response = requests.post(
                'http://127.0.0.1:8000/api/refresh/',
                json={'refresh': request.session['refresh_token']}
            )
            if refresh_response.status_code == 200:
                request.session['access_token'] = refresh_response.json().get('access')
                headers['Authorization'] = f'Bearer {request.session["access_token"]}'
                # Retry original request
                response = requests.request(
                    request.method,
                    api_url,
                    headers=headers,
                    json=request.POST.dict() or None,
                    params=request.GET
                )
        
        return JsonResponse(response.json(), status=response.status_code)
    
    except requests.exceptions.RequestException as e:
        return JsonResponse({'error': str(e)}, status=500)
    
# Custom authentication backend (add to your authentication backends in settings.py)
class APIAuthBackend:
    def authenticate(self, request, email=None, password=None):
        response = requests.post(
            'http://127.0.0.1:8000/api/login/',
            json={'email': email, 'password': password}
        )
        if response.status_code == 200:
            # Create or get user
            user_data = requests.get(
                'http://127.0.0.1:8000/api/users/me/',
                headers={'Authorization': f'Basic {response.json().get("access")}'}
            ).json()
            
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'username': user_data.get('username'),
                    'email': email
                }
            )
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None