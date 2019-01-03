import os
import json
import datetime
import django
import string
import re


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'archive.settings')
django.setup()

from snips.models import Snip, SnipAuthor, CharacterTag, DiscordMessage

timefmt = '%Y-%m-%d %H:%M:%S'

class Tag:
    def __init__(self, tag, regexes):
        self.tag = tag
        self.regexes = regexes
        try:
            self.obj = CharacterTag.objects.get(tagname=tag)
        except CharacterTag.DoesNotExist:
            self.obj = CharacterTag(tagname=tag)
            self.obj.save()


with open('tags.json') as f:
    TAGS = json.load(f)
tagarray = []

# Set tags
for tag, regex in TAGS.items():
    tagarray.append(Tag(tag, regex))


for filename in os.listdir('sniparchive'):
    with open(f'sniparchive/{filename}') as f:
        data = json.load(f)
    authorid = data[0]['authorid']
    authorname = data[0]['author']

    # Set author
    try:
        author = SnipAuthor.objects.get(discordid=authorid)
    except SnipAuthor.DoesNotExist:
        author = SnipAuthor(name=authorname, discordid=authorid)
        author.save()

    # Save snip
    snip = Snip(
        author=author,
        timeposted=datetime.datetime.strptime(data[0]['timestamp'], timefmt),
        title=filename.split('.')[0])
    content = ''.join([datum['content'] for datum in data])
    content = content.replace('```', '')
    snip.content = content
    snip.save()

    # Also save individual messages
    for datum in data:
        msg = DiscordMessage(
                parent=snip,
                timestamp=datetime.datetime.strptime(datum['timestamp'], timefmt),
                messageid=datum['msgid'],
                channelid=datum['channelid'],
                serverid=datum['serverid'])
        msg.save()

    searchtext = content
    # Guess character tags
    for tag in tagarray:
        for regex in tag.regexes:
            if re.search(regex, searchtext):
                snip.tags.add(tag.obj)
                break
    snip.save()
