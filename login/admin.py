from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Subscription

#unregister group
from django.contrib.auth.models import Group
admin.site.unregister(Group)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'is_active', 'start_date', 'end_date')

class CustomUserAdmin(UserAdmin):
    model = User

    # Custom method to show subscription plan
    def subscription_plan(self, obj):
        return obj.subscription.plan if hasattr(obj, 'subscription') and obj.subscription else 'No Plan'
    subscription_plan.short_description = 'Subscription Plan'  # Column name in admin

    list_display = ('username', 'email', 'subscription_plan')  # Show plan instead of role
    search_fields = ('username', 'email')
    # No need for list_filter if not using 'role'
    fieldsets = UserAdmin.fieldsets  # No extra fields for now

admin.site.register(User, CustomUserAdmin)

admin.site.site_header = "housAI"
admin.site.site_title = "housAI"
admin.site.index_title = "Welcome to housAI"