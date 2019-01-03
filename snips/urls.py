from django.urls import path

from . import views as v


urlpatterns = [
    path('', v.SnipsList.as_view(), name='snip-index'),
    path('<int:pk>', v.SnipDetails.as_view(), name='snip-view'),
    path('<int:pk>/edit', v.SnipEdit.as_view(), name='snip-edit'),
    path('<int:pk>/delete', v.SnipDelete.as_view(), name='snip-delete'),
]
