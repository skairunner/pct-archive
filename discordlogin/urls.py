from discord.urls import path

from . import views as v


urlpatterns = [
    path('', a.LinkToDiscord.as_view(), name='auth-landing'),
]
