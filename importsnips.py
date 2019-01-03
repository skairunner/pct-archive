import os
import json
import datetime
import django


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'archive.settings')
django.setup()

from snips.models import Snip, SnipAuthor

timefmt = '%Y-%m-%d %H:%M:%S'

for filename in os.listdir('sniparchive'):
    with open(f'sniparchive/{filename}') as f:
        data = json.load(f)
    authorid = data[0]['authorid']
    authorname = data[0]['author']
    try:
        author = SnipAuthor.objects.get(discordid=authorid)
    except SnipAuthor.DoesNotExist:
        author = SnipAuthor(name=authorname, discordid=authorid)
        author.save()

    snip = Snip(
        author=author,
        timeposted=datetime.datetime.strptime(data[0]['timestamp'], timefmt),
        title=filename.split('.')[0])
    content = ''.join([datum['content'] for datum in data])
    content = content.replace('```', '')
    snip.content = content
    snip.save()
