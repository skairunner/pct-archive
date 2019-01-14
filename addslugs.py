import os
import json
import datetime
import django
import string
import re
import pytz


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'archive.settings')
django.setup()

from snips.models import Snip
from django.utils.text import slugify

for snip in Snip.objects.all():
    snip.slug = slugify(snip.title)[:50]
    snip.save()
