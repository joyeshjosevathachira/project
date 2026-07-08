from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required

from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from .forms import UserRegisterForm, ProfileUpdateForm
from .serializers import UserSerializer, RegisterSerializer


# ---------------------------------------------------------------------------
# Server-rendered auth views (session based, using Django's auth system)
# ---------------------------------------------------------------------------
def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # log the user in immediately -> creates a session
            messages.success(request, 'Your account has been created!')
            return redirect('home')
    else:
        form = UserRegisterForm()
    return render(request, 'registration/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)  # creates a session cookie for the user
            messages.success(request, f'Welcome back, {user.username}!')
            next_url = request.GET.get('next') or 'home'
            return redirect(next_url)
        messages.error(request, 'Invalid username or password.')
    return render(request, 'registration/login.html')


def logout_view(request):
    logout(request)  # flushes the session
    messages.info(request, 'You have been logged out.')
    return redirect('home')


@login_required
def profile_view(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated.')
            return redirect('accounts:profile')
    else:
        form = ProfileUpdateForm(instance=profile)
    return render(request, 'registration/profile.html', {'form': form})


# ---------------------------------------------------------------------------
# REST API views
# ---------------------------------------------------------------------------
class RegisterAPIView(generics.CreateAPIView):
    """POST /api/v1/auth/register/ - create a new user account."""
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer


class LoginAPIView(APIView):
    """
    POST /api/v1/auth/login/ {username, password}
    Logs the user into a Django session AND returns a DRF auth token,
    so API clients can authenticate either way.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is None:
            return Response({'detail': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)
        login(request, user)  # establishes server-side session
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data,
        })


class LogoutAPIView(APIView):
    """POST /api/v1/auth/logout/ - destroys the current session."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({'detail': 'Logged out successfully.'}, status=status.HTTP_204_NO_CONTENT)


class ProfileAPIView(generics.RetrieveUpdateAPIView):
    """GET/PUT/PATCH /api/v1/auth/me/ - view or update the logged-in user's profile."""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user
