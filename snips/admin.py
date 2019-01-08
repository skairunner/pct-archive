from django.contrib import admin
from . import models as m


admin.site.register(m.Snip)
admin.site.register(m.SnipAuthor)
admin.site.register(m.CharacterTag)
admin.site.register(m.DiscordMessage)
