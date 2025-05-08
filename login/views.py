from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate , get_user_model
from django.contrib.auth.forms import UserCreationForm
from .models import User , Subscription
from .forms import CustomUserCreationForm
#mail verification imports
from django.http import HttpResponse
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.encoding import force_str
#reset password 
from django.contrib.auth.forms import SetPasswordForm


def index(request):
    # If the user is already logged in, redirect them to the home page
    if request.user.is_authenticated:
        return redirect('work:home', user_id=request.user.id)
    return render(request, 'login/index.html')



#password reset in case forgot

User = get_user_model()

def password_reset_request(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        try:
            user = User.objects.get(username=username)
            if not user.email:
                return HttpResponse("This user doesn't have an email.")
            
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            link = request.build_absolute_uri(
                reverse('login:password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
            )

            subject = "Reset Your Password"
            message = f"""
<html>
<body style="background-color: #ffffff; font-family: Arial, sans-serif; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px; background-color: #f9f9f9;">
        <h2 style="color: #6366f1; text-align: center;">Reset Your Password – housAI</h2>
        <p style="font-size: 16px; color: #555;">
            Hi {user.username},
        </p>
        <p style="font-size: 16px; color: #555;">
            We received a request to reset your password. Click the button below to choose a new password:
        </p>
        <p style="text-align: center;">
            <a href="{link}" style="background-color: #6366f1; color: white; padding: 12px 30px; text-decoration: none; border-radius: 4px; font-size: 16px;">Reset Password</a>
        </p>
        <p style="font-size: 14px; color: #777; text-align: center;">
            If you didn’t request a password reset, you can safely ignore this email.
        </p>
        <p style="font-size: 14px; color: #777; text-align: center;">
            – The housAI Team
        </p>
    </div>
</body>
</html>
"""

            send_mail(subject, '', 'housai.email@gmail.com', [user.email], html_message=message)

            return render(request, 'login/password_reset_email_sent.html')
        except User.DoesNotExist:
            return render(request, 'login/user_not_found.html')

    return render(request, 'login/password_reset_request.html')


def password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except Exception:
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                login(request, user)
                return redirect('work:home', user_id=user.id)
        else:
            form = SetPasswordForm(user)
        return render(request, 'login/password_reset_confirm.html', {'form': form})
    else:
        return HttpResponse("Invalid or expired link.")
    


#register & verification
def send_verification_email(request, user):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    link = request.build_absolute_uri(
        reverse('login:verify_email', kwargs={'uidb64': uid, 'token': token})
    )
    subject = "Welcome to housAI – Verify Your Email"
    message = f"""
    <html>
    <body style="background-color: #ffffff; font-family: Arial, sans-serif; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px; background-color: #f9f9f9;">
            <h2 style="color: #6366f1; text-align: center;">Welcome to housAI!</h2>
            <p style="font-size: 16px; color: #555;">
                Hi {user.username},
            </p>
            <p style="font-size: 16px; color: #555;">
                Thank you for joining housAI! We're excited to have you on board. Please click the button below to verify your email address and get started:
            </p>
            <p style="text-align: center;">
                <a href="{link}" style="background-color: #6366f1; color: white; padding: 12px 30px; text-decoration: none; border-radius: 4px; font-size: 16px;">Verify Email</a>
            </p>
            <p style="font-size: 14px; color: #777; text-align: center;">
                If you did not sign up for this account, please ignore this email.
            </p>
            <p style="font-size: 14px; color: #777; text-align: center;">
                – The housAI Team
            </p>
        </div>
    </body>
    </html>
    """
    send_mail(subject, message, 'housai.email@gmail.com', [user.email], html_message=message)

def verify_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)  # 🔥 Auto-login here
        return redirect('work:home', user_id=user.id)
    else:
         return HttpResponse("Email verification failed Or Its an old link. Please check the link and try again.")
def register(request):
    if request.user.is_authenticated:
        return redirect('work:home', user_id=request.user.id)

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Deactivate account
            user.save()
            send_verification_email(request, user)
            return render(request, 'login/email_verification_sent.html')

    else:
        form = CustomUserCreationForm()
    return render(request, 'login/register.html', {'form': form})

#login

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