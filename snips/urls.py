from django.urls import path

from . import views as v


urlpatterns = [
    path('', v.SnipsList.as_view(), name='snip-index'),
    path('<int:pk>', v.SnipDetails.as_view(), name='snip-view'),
]
