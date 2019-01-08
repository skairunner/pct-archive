from django import forms, template
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import HttpResponseRedirect
from django.shortcuts import reverse
from django.views.generic import ListView, DetailView,\
        UpdateView, DeleteView, FormView, CreateView, TemplateView
from django.views.generic.edit import FormMixin
from django.views.generic.detail import SingleObjectMixin
import json
import requests
import rules

from .models import Snip, CharacterTag, SnipAuthor
from .utility import sanitize_keys


class PaginationForm(forms.Form):
    perpage = forms.ChoiceField(choices=[(10, '10'), (25, '25'), (50, '50'), (100, '100')])
    def __init__(self, *args, **kwargs):
        initial = kwargs.pop('initial')
        super().__init__(*args, **kwargs)
        self.initial['perpage'] = initial


class SnipsList(FormMixin, ListView):
    model = Snip
    template_name = 'snips/list.html'
    form_class = PaginationForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['initial'] = self.request.session.get('paginate', 50)
        return kwargs

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_valid(self, form):
        self.request.session['paginate'] = int(form.cleaned_data['perpage'])
        return HttpResponseRedirect(reverse('snip-index'))

    def get_paginate_by(self, queryset):
        self.paginate_by = self.request.session.get('paginate', 50)
        return self.paginate_by

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
        paginate_by = self.get_paginate_by(self.get_queryset())
        snips_before = (paginator.number - 1) * paginate_by
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
            self.fields['tag_' + tag] = forms.BooleanField(
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
        self.object.do_delete()
        self.object.save()
        return HttpResponseRedirect(success_url)


class SearchForm(TagForm):
    searchphrase = forms.CharField(required=False)
    author = forms.ModelChoiceField(
            queryset=SnipAuthor.objects.order_by('name'),
            required=False)

    def clean(self):
        cleaned_data = super().clean()
        # If both search phrase blank and no tags, error
        has_tags = False
        for key, val in cleaned_data.items():
            if key.startswith('tag_'):
                has_tags |= val
        searchphrase = cleaned_data['searchphrase']
        author = cleaned_data['author']
        if (not has_tags) and (not author) and (not searchphrase):
            raise ValidationError('You need to search for something', code='blank-form')
        return cleaned_data


class Search(FormView):
    form_class = SearchForm
    template_name = 'snips/search.html'

    def process_result(self, data):
        out = {}
        out['success'] = True
        out['took'] = data['took']
        out['hits'] = []
        for hit in data['hits']['hits']:
            out['hits'].append(Snip.objects.get(id=hit['_id']))
        return out

    def get_tags(self, form):
        tags = []
        for key, val in form.cleaned_data.items():
            if key.startswith('tag_') and val:
                tags.append(key[4:])
        return [CharacterTag.objects.get(tagname=tag).elasticname for tag in tags]

    def form_valid(self, form):
        tags = self.get_tags(form)
        searchphrase = form.cleaned_data['searchphrase']
        author = form.cleaned_data['author']

        payload = {'query': {'bool': {}}}
        bool_ = payload['query']['bool']
        if searchphrase:
            bool_['must'] = [{'simple_query_string': {'fields': ['title^3', 'summary^2', 'content'], 'query': searchphrase}}]
        if tags or author:
            bool_['filter'] = []
        for tag in tags:
            bool_['filter'].append({'term': {'tags': tag}})
        if author:
            bool_['filter'].append({'term': {'author': author.id}})
        payload['size'] = 50

        r = requests.get('http://localhost:9200/snips/_search', json=payload)
        data = r.json()
        if 'status' not in data:
            response = self.process_result(data)
            return self.render_to_response(self.get_context_data(searched=True, response=response))
        response = {
                'success': False
                }
        return self.render_to_response(self.get_context_data(
            searched=True,
            response=response))

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        tags = [tag.tagname for tag in
                CharacterTag.objects.all().order_by('tagname')]
        kwargs['tags'] = tags
        return kwargs
