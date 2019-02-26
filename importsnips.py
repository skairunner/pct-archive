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

timefmt = '%Y-%m-%d %H:%M:%S'

class Tag:
    def __init__(self, tag, regexes):
        self.tag = tag
        self.regexes = regexes
        try:
            self.obj = CharacterTag.objects.get(tagname=tag)
            self.obj.save()
        except CharacterTag.DoesNotExist:
            self.obj = CharacterTag(tagname=tag)
            self.obj.save()


with open('tags.json') as f:
    TAGS = json.load(f)
tagarray = []

# Set tags
for tag, regex in TAGS.items():
    tagarray.append(Tag(tag, regex))


# Take array of messages that form a snip, save.
def process_snip(data):
    authorid = data[0]['authorid']
    authorname = data[0]['author']

    # Set author
    try:
        author = SnipAuthor.objects.get(discordid=authorid)
    except SnipAuthor.DoesNotExist:
        author = SnipAuthor(name=authorname, discordid=authorid)
        author.save()

    try:
        snip = DiscordMessage.objects.get(messageid=data[0]['msgid']).parent
    except DiscordMessage.DoesNotExist:
        snip = Snip()
    # Save snip
    snip.author = author
    timestamp = datetime.datetime.strptime(data[0]['timestamp'], timefmt)
    snip.timeposted = timestamp.replace(tzinfo=pytz.UTC)
    if not snip.title:
        snip.title = f'snip {data[0]["msgid"]}'
    # First replace code fences and markdown/md with a trailing newline, then replace without
    content = re.sub(r'```(markdown|md)?\n', '', '\n'.join([datum['content'] for datum in data]))
    content = re.sub(r'```(markdown|md)?', '', content)
    snip.content = content
    snip.save()

    # Also save individual messages
    for datum in data:
        try:
            msg = DiscordMessage.objects.get(messageid=datum['msgid'])
        except DiscordMessage.DoesNotExist:
            msg = DiscordMessage()
        msg.parent = snip
        timestamp = datetime.datetime.strptime(datum['timestamp'], timefmt)
        msg.timestamp = timestamp.replace(tzinfo=pytz.UTC)
        msg.messageid = datum['msgid']
        msg.channelid = datum['channelid']
        msg.serverid = datum['serverid']
        msg.save()

    searchtext = content
    # Guess character tags
    for tag in tagarray:
        for regex in tag.regexes:
            if re.search(regex, searchtext):
                snip.tags.add(tag.obj)
                break
    snip.save()

if __name__ =='__main__':
    for filename in os.listdir('sniparchive'):
        with open(f'sniparchive/{filename}') as f:
            try:
                data = json.load(f)
            except json.decoder.JSONDecodeError as e:
                print(filename); raise e
        process_snip(data)
