
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from data_grabber import views


router = DefaultRouter()
router.register('symbol_info', views.SymbolInfoViewSet)
router.register('grabber_settings', views.GrabberSettingsViewSet)
router.register('grabber_run', views.GrabberRunsViewSet)
router.register('binance_account', views.BinanceAccountViewSet)


app_name = 'data_grabber'

urlpatterns = [
    path('', include(router.urls))
]
