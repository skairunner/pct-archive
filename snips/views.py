from django.core.exceptions import PermissionDenied
from django.views.generic import ListView, DetailView, UpdateView
import rules

from .models import Snip


class SnipsList(ListView):
    model = Snip
    template_name = 'snips/list.html'
    paginate_by = 50

    def get_queryset(self):
        qs = super().get_queryset()
        author = self.request.GET.get('author', None)
        if author:
            qs = qs.filter(author=author)
        return qs.order_by('-timeposted')


class SnipDetails(DetailView):
    model = Snip
    template_name = 'snips/single.html'


class SnipEdit(UpdateView):
    model = Snip
    template_name = 'snips/edit.html'
    fields = ['title', 'summary', 'content']

    def get_object(self):
        obj = super().get_object()
        if not rules.test_rule('can_change_snip', self.request.session, obj):
            raise PermissionDenied
        return obj
