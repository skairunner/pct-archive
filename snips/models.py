from django.db import models
from django.shortcuts import reverse
import requests
import mistletoe

from .utility import elastic_filter


class SnipAuthor(models.Model):
    name = models.CharField(max_length=100)
    discordid = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class CharacterTag(models.Model):
    tagname = models.CharField(max_length=255)
    elasticname = models.CharField(max_length=255)

    def __str__(self):
        return self.tagname

    def save(self, *args, **kwargs):
        self.elasticname = elastic_filter(self.tagname)
        super().save(*args, **kwargs)


class Snip(models.Model):
    author = models.ForeignKey(SnipAuthor, on_delete=models.CASCADE)
    timeposted = models.DateTimeField()
    title = models.CharField(max_length=255)
    summary = models.CharField(max_length=255, default='', blank=True)
    content = models.TextField()
    content_html = models.TextField(default='')
    tags = models.ManyToManyField(CharacterTag)
    isdeleted = models.BooleanField(default=False)

    def do_delete(self):
        r = requests.delete(f'http://localhost:9200/snips/doc/{self.id}')
        if r.status_code != 200:
            print(r.json())

    def save(self, *args, **kwargs):
        self.content_html = mistletoe.markdown(self.content)
        # Also post it to Elasticsearch
        if not self.isdeleted and self.id:
            payload = {
                    'title': self.title,
                    'summary': self.summary,
                    'content': self.content,
                    'tags': [tag.elasticname for tag in self.tags.all()],
                    'timeposted': self.timeposted.timestamp(),
                    'author': self.author.id
                    }
            r = requests.put(f'http://localhost:9200/snips/doc/{self.id}', json=payload)
            if r.status_code != 200:
                print(r.json())
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('snip-view', args=[self.pk])


class DiscordMessage(models.Model):
    parent = models.ForeignKey(Snip, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
    messageid = models.CharField(max_length=255)
    channelid = models.CharField(max_length=255)
    serverid = models.CharField(max_length=255)
