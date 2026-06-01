from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/liquidacion/', consumers.LiquidacionConsumer.as_asgi()),
]