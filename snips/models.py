from django.db import models
from django.shortcuts import reverse
import mistletoe


class SnipAuthor(models.Model):
    name = models.CharField(max_length=100)
    discordid = models.CharField(max_length=255)


class CharacterTag(models.Model):
    tagname = models.CharField(max_length=255)

    def __str__(self):
        return self.tagname


class Snip(models.Model):
    author = models.ForeignKey(SnipAuthor, on_delete=models.CASCADE)
    timeposted = models.DateTimeField()
    title = models.CharField(max_length=255)
    summary = models.CharField(max_length=255, default='', blank=True)
    content = models.TextField()
    content_html = models.TextField(default='')
    tags = models.ManyToManyField(CharacterTag)
    isdeleted = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.content_html = mistletoe.markdown(self.content)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('snip-view', args=[self.pk])


class DiscordMessage(models.Model):
    parent = models.ForeignKey(Snip, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
    messageid = models.CharField(max_length=255)
    channelid = models.CharField(max_length=255)
    serverid = models.CharField(max_length=255)
