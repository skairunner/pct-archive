import os
import json
import datetime
import django
import string
import re
import pytz


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'archive.settings')
django.setup()

from snips.models import Snip, SnipAuthor, CharacterTag, DiscordMessage

for snip in Snip.objects.all():
    snip.save()
