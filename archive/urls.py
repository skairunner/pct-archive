from django.contrib import admin
from django.urls import include, path
from django.views.generic.base import RedirectView
from django.urls import reverse_lazy


urlpatterns = [
    path('admin/', admin.site.urls),
    path('snips/', include('snips.urls')),
    path('auth/', include('discordlogin.urls')),
    path('', RedirectView.as_view(url=reverse_lazy('snip-index')),),
]
