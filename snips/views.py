from django.views.generic import ListView, DetailView

from .models import Snip


class SnipsList(ListView):
    model = Snip
    template_name = 'snips/list.html'

    def get_queryset(self):
        qs = super().get_queryset()
        author = self.request.GET.get('author', None)
        if author:
            qs = qs.filter(author=author)
        return qs.order_by('-timeposted')


class SnipDetails(DetailView):
    model = Snip
    template_name = 'snips/single.html'
