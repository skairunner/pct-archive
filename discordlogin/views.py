from django.shortcuts import render
from django.views.generic import TemplateView


class LinkToDiscord(TemplateView):
    template_name = 'discordlogin/lets-authorize.html'
