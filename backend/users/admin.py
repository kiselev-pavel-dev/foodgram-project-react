from django.contrib import admin

from .models import Subscription, User


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'username',
        'email',
        'first_name',
        'last_name',
        'is_superuser',
    )
    search_fields = ('username',)
    list_filter = ('email', 'username')


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'author',
        'subscriber',
    )


admin.site.register(User, UserAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
