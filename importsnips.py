import os
import json
import datetime
import django
import string


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'archive.settings')
django.setup()

from snips.models import Snip, SnipAuthor, CharacterTag

timefmt = '%Y-%m-%d %H:%M:%S'

class Tag:
    def __init__(self, tag, keywords):
        self.tag = tag
        self.keywords = keywords
        try:
            self.obj = CharacterTag.objects.get(tagname=tag)
        except CharacterTag.DoesNotExist:
            self.obj = CharacterTag(tagname=tag)
            self.obj.save()


TAGS = {
    'Lisa Wilbourn (Tattletale)' : [
        'lisa',
        'tattletale'
    ]
}
tagarray = []

# Set tags
for tag, keywords in TAGS.items():
    tagarray.append(Tag(tag, keywords))


# Filter special
transdict = {ord(c): None for c in string.punctuation + '\n'}


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

    words = content.lower().translate(transdict).split(' ')
    # Guess character tags
    for tag in tagarray:
        for keyword in tag.keywords:
            if keyword in words:
                snip.tags.add(tag.obj)
                break
    snip.save()
