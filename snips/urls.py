from django.urls import path

from . import views as v


urlpatterns = [
    path('', v.SnipsList.as_view(), name='snip-index'),
    path('<int:pk>', v.RedirectToSluggedSnip),
    path('<int:pk>.<slug:slug>', v.SnipDetails.as_view(), name='snip-view'),
    path('<int:pk>/edit', v.SnipEdit.as_view(), name='snip-edit'),
    path('<int:pk>/delete', v.SnipDelete.as_view(), name='snip-delete'),
    path('<int:pk>/addchar', v.AddTag.as_view(), name='snip-addtag'),
    path('<int:pk>/removechar', v.RemoveTag.as_view(), name='snip-removetag'),
    path('addchar', v.CreateTag.as_view(), name='createtag'),
    path('search', v.Search.as_view(), name='snip-search'),
]
