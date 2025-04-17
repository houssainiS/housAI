from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from .models import User , Subscription
from .forms import CustomUserCreationForm


def index(request):
    # If the user is already logged in, redirect them to the home page
    if request.user.is_authenticated:
        return redirect('work:home', user_id=request.user.id)
    return render(request, 'login/index.html')

def register(request):
    # If the user is already logged in, redirect them to the home page
    if request.user.is_authenticated:
        return redirect('work:home', user_id=request.user.id)
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()  # Save the user, `role` will be null by default
            login(request, user)  # Automatically log the user in after registration
            return redirect('work:home', user_id=user.id)  # Redirect to home or dashboard page
    else:
        form = CustomUserCreationForm()
    return render(request, 'login/register.html', {'form': form})

def login_view(request):
    # If the user is already logged in, redirect them to the home page
    if request.user.is_authenticated:
        return redirect('work:home', user_id=request.user.id)
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Redirect to the user's home page, passing the user ID as an argument
            return redirect('work:home', user_id=user.id)
        else:
            return render(request, 'login/login.html', {'error': 'Invalid credentials'})
    return render(request, 'login/login.html')


# subscriptions plan 

def subscription_plans(request):
    if request.user.is_authenticated:
        # Get the user's current subscription if available
        current_subscription = Subscription.objects.filter(user=request.user).first()
        return render(request, 'login/subscription_plans.html', {
            'current_subscription': current_subscription,
        })
    else:
        return redirect('login:login')  # Redirect to login if not authenticated

def update_subscription(request, plan):
    if request.user.is_authenticated:
        # Check if the user already has a subscription
        subscription, created = Subscription.objects.get_or_create(user=request.user)

        # Update the subscription plan
        subscription.plan = plan
        subscription.is_active = True  # Make sure the subscription is active
        subscription.save()

        return redirect('login:subscription_plans')  # Redirect back to subscription page
    else:
        return redirect('login:login')  # Redirect to login if not authenticated