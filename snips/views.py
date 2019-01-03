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

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        # Get first message to make a link
        msg = self.object.discordmessage_set.all().order_by('timestamp').first()
        kwargs['discordlink'] = f'https://discordapp.com/channels/{msg.serverid}/{msg.channelid}/{msg.messageid}'
        return kwargs


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


class TagForm(forms.Form):
    def __init__(self, *args, **kwargs):
        tags = kwargs.pop('tags')
        if 'checked' in kwargs:
            checked = kwargs.pop('checked')
        else:
            checked = None

        super().__init__(*args, **kwargs)
        for tag in tags:
            default = tag in checked if checked else False
            self.fields[tag] = forms.BooleanField(
                    required=False,
                    initial=default,
                    label=tag)


class AddTag(SingleObjectMixin, FormView):
    form_class = TagForm
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

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        tags = [tag.tagname for tag in
                CharacterTag.objects.all().order_by('tagname')]
        exists = [tag.tagname for tag in self.object.tags.all()]
        kwargs['tags'] = tags
        kwargs['checked'] = exists
        return kwargs

    def form_valid(self, form):
        for key, val in form.cleaned_data.items():
            if val:
                tag = CharacterTag.objects.get(tagname=key)
                self.object.tags.add(tag)
        return HttpResponseRedirect(self.object.get_absolute_url())


class RemoveTag(SingleObjectMixin, FormView):
    form_class = TagForm
    template_name = 'snips/remove-tag.html'
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

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        tags = [tag.tagname for tag in self.object.tags.all()]
        kwargs['tags'] = tags
        return kwargs

    def form_valid(self, form):
        for key, val in form.cleaned_data.items():
            if val:
                tag = CharacterTag.objects.get(tagname=key)
                self.object.tags.remove(tag)
        self.object.save()
        print(form.cleaned_data)
        return HttpResponseRedirect(self.object.get_absolute_url())


class CreateTag(CreateView):
    model = CharacterTag
    template_name = 'snips/create-tag.html'
    fields = ['tagname']

    def get_success_url(self):
        if 'return' in self.request.GET:
            return self.request.GET.get('return')
        return '/'


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
