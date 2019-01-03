from django.urls import path

from . import views as v


urlpatterns = [
    path('', v.LinkToDiscord.as_view(), name='auth-landing'),
    path('return', v.Authenticate, name='auth-redirect'),
]
