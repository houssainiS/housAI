from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

app_name = 'login'

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('subscription/', views.subscription_plans, name='subscription_plans'),
    path('subscription/update/<str:plan>/', views.update_subscription, name='update_subscription'),
    path('logout/', LogoutView.as_view(next_page='login:index'), name='logout'),  # Logout view
    path('verify-email/<uidb64>/<token>/', views.verify_email, name='verify_email'),
]