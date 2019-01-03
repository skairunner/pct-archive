from django import forms
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.shortcuts import reverse
from django.views.generic import ListView, DetailView,\
        UpdateView, DeleteView, FormView, CreateView
from django.views.generic.detail import SingleObjectMixin
import rules

from .models import Snip, CharacterTag


class SnipsList(ListView):
    model = Snip
    template_name = 'snips/list.html'
    paginate_by = 50

    def get_queryset(self):
        qs = super().get_queryset()
        author = self.request.GET.get('author', None)
        qs = qs.filter(isdeleted=False)
        if author:
            qs = qs.filter(author=author)
        return qs.order_by('-timeposted')

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        paginator = kwargs['page_obj']
        objs = kwargs['object_list']
        snips_before = (paginator.number - 1) * self.paginate_by
        kwargs['pageinfo'] = {
                'total_snips': self.get_queryset().count(),
                'snips_from': snips_before + 1,
                'snips_to': snips_before + len(objs),
            }
        return kwargs


class SnipDetails(DetailView):
    model = Snip
    template_name = 'snips/single.html'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(isdeleted=False)


class SnipEdit(UpdateView):
    model = Snip
    template_name = 'snips/edit.html'
    fields = ['title', 'summary', 'content']

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(isdeleted=False)

    def get_object(self):
        obj = super().get_object()
        if not rules.test_rule('can_change_snip', self.request, obj):
            raise PermissionDenied
        return obj


class AddTagForm(forms.Form):
    new_tag = forms.ModelChoiceField(queryset=CharacterTag.objects.all())


class AddTag(SingleObjectMixin, FormView):
    form_class = AddTagForm
    template_name = 'snips/add-tag.html'
    model = Snip

    def get(self, request, *args, **kwargs):
        self.get_object(self.get_queryset())
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.get_object(self.get_queryset())
        return super().post(request, *args, **kwargs)

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(isdeleted=False)

    def get_object(self, qs=None):
        if qs:
            self.object = qs.get(id=self.kwargs['pk'])
            if not rules.test_rule('can_change_snip', self.request, self.object):
                raise PermissionDenied
            return self.object
        raise ValueError('Queryset is none')

    def form_valid(self, form):
        self.object.tags.add(form.cleaned_data['new_tag'])
        return HttpResponseRedirect(self.object.get_absolute_url())


class CreateTag(CreateView):
    model = CharacterTag
    template_name = 'snips/create-tag.html'
    fields = ['tagname']
    success_url = '/'


class SnipDelete(DeleteView):
    model = Snip
    template_name = 'snips/delete.html'

    def get_success_url(self):
        return reverse('snip-index')

    def get_object(self):
        obj = super().get_object()
        if not rules.test_rule('can_change_snip', self.request, obj):
            raise PermissionDenied
        return obj

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.isdelete = True
        self.object.save()
        return HttpResponseRedirect(success_url)
