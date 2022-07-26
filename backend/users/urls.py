from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import SubscribeViewSet, SubscriptionViewSet

app_name = 'users'

router = DefaultRouter()

router.register(
    'users/subscriptions', SubscriptionViewSet, basename='subscriptions'
)

router.register(
    r'users/(?P<user_id>\d+)/subscribe',
    SubscribeViewSet,
    basename='subscribes',
)

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
