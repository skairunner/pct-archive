from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import TemplateView
import urllib.parse
import os
import requests

from snips.models import SnipAuthor


API_BASE = 'https://discordapp.com/api'
BASE_URL = os.environ['APP_URL']
REDIRECT_URL = reverse_lazy('auth-redirect')


class LinkToDiscord(TemplateView):
    template_name = 'discordlogin/lets-authorize.html'

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        redirect_url = urllib.parse.quote(f'{BASE_URL}{REDIRECT_URL}')
        oauth = f'{API_BASE}/oauth2/authorize?client_id={os.environ["DISCORD_CLIENT_ID"]}&redirect_uri={redirect_url}&response_type=code&scope=identify'
        kwargs['oauth_url'] = oauth
        return kwargs


def Authenticate(request, *args, **kwargs):
    code = request.GET.get('code')
    # Let's go get the token
    headers = {
        'User-Agent': 'PCT Archive Authentication',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    payload = {
        'client_id': os.environ['DISCORD_CLIENT_ID'],
        'client_secret': os.environ['DISCORD_CLIENT_SECRET'],
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': f'{BASE_URL}{REDIRECT_URL}',
        'scope': 'identify'
    }
    r = requests.post(
            f'{API_BASE}/oauth2/token',
            headers=headers,
            data=payload)
    request.session['discord_token'] = r.json()['access_token']
    headers = {
        'User-Agent': 'PCT Archive Authentication',
        'Authorization': f'Bearer {request.session["discord_token"]}',
    }
    r = requests.get(
        f'{API_BASE}/users/@me',
        headers=headers)
    data = r.json()
    request.session['authenticated'] = True
    request.session['discord_id'] = data['id']
    request.session['discord_username'] = f'{data["username"]}#{data["discriminator"]}'
    request.session['discord_avatar'] = data['avatar']

    try:
        author = SnipAuthor.objects.get(discordid=data['id'])
        author.name = request.session['discord_username']
        author.save()
    except SnipAuthor.DoesNotExist:
        pass

    return HttpResponseRedirect('/')


def EndSession(request, *args, **kwargs):
    request.session.flush()
    return HttpResponseRedirect('/')
