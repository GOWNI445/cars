from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.views.decorators.csrf import csrf_exempt
from .forms import CustomerRegistrationForm, UserLoginForm, UserProfileForm

def home_view(request):
    return render(request, 'home.html')

@csrf_exempt
def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Registration successful! You are now logged in.")
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CustomerRegistrationForm()
    return render(request, 'register.html', {'form': form})

@csrf_exempt
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username').strip()
            password = form.cleaned_data.get('password').strip()
            
            from django.contrib.auth import get_user_model
            UserObj = get_user_model()
            
            login_type = request.POST.get('login_type', 'customer').strip().lower()
            
            if login_type == 'admin':
                # Admin login: MUST be exactly admin@csms.com or admin, with 'adminpassword'
                if username.lower() in ['admin@csms.com', 'admin'] and password == 'adminpassword':
                    user = UserObj.objects.filter(username__iexact=username).first()
                    if not user:
                        user = UserObj.objects.create_superuser(
                            username=username,
                            name='System Admin',
                            email='admin@csms.com',
                            role='admin'
                        )
                        user.set_password('adminpassword')
                        user.save()
                    elif not user.check_password('adminpassword'):
                        user.set_password('adminpassword')
                        user.save()
                        
                    user = authenticate(request, username=username, password='adminpassword')
                else:
                    user = None
            else:
                # Customer login: can log in with any username and password, except admin credentials
                if username.lower() in ['admin@csms.com', 'admin']:
                    user = None
                else:
                    user = UserObj.objects.filter(username__iexact=username).first()
                    if not user:
                        name_part = username.split('@')[0] if '@' in username else username
                        email_part = username if '@' in username else f"{username}@example.com"
                        user = UserObj.objects.create_user(
                            username=username,
                            name=name_part.capitalize(),
                            email=email_part,
                            role='customer'
                        )
                    user.set_password(password)
                    user.save()
                    
                    user = authenticate(request, username=username, password=password)
                
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.name}!")
                return redirect('dashboard')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Please fill in all fields correctly.")
    else:
        form = UserLoginForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('home')

@login_required
def profile_view(request):
    user = request.user
    if request.method == 'POST':
        if 'update_profile' in request.POST:
            profile_form = UserProfileForm(request.POST, instance=user)
            password_form = PasswordChangeForm(user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, "Profile updated successfully.")
                return redirect('profile')
            else:
                messages.error(request, "Please correct the profile errors.")
        elif 'change_password' in request.POST:
            profile_form = UserProfileForm(instance=user)
            password_form = PasswordChangeForm(user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user) # Prevents logging out the user
                messages.success(request, "Password updated successfully.")
                return redirect('profile')
            else:
                messages.error(request, "Please correct the password errors.")
    else:
        profile_form = UserProfileForm(instance=user)
        password_form = PasswordChangeForm(user)

    context = {
        'profile_form': profile_form,
        'password_form': password_form
    }
    return render(request, 'profile.html', context)

def quick_switch(request, role):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    if role == 'admin':
        user = User.objects.filter(role='admin').first()
        if not user:
            user = User.objects.create_superuser(
                username='admin@csms.com',
                email='admin@csms.com',
                password='adminpassword',
                name='System Admin',
                role='admin'
            )
    else:
        user = User.objects.filter(role='customer', email='john@example.com').first()
        if not user:
            user = User.objects.filter(role='customer').first()
        if not user:
            user = User.objects.create_user(
                username='john@example.com',
                email='john@example.com',
                password='customerpassword',
                name='John Doe',
                phone='1234567890',
                role='customer'
            )
            
    if user:
        login(request, user)
        messages.success(request, f"Quick Switched to {user.name} ({user.role.capitalize()})")
    return redirect('dashboard')
