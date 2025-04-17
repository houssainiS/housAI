from django.urls import path
from . import views

app_name = 'login'

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
        path('subscription/', views.subscription_plans, name='subscription_plans'),
    path('subscription/update/<str:plan>/', views.update_subscription, name='update_subscription'),
]