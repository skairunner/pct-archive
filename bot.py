import discord
import datetime
import asyncio
import logging
import os
import sys
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'archive.settings')
django.setup()

from snips.models import DiscordMessage
from importsnips import process_snip

CHANNEL_ID = '406611842257911828'
logging.basicConfig(level=logging.INFO)
client = discord.Client()

timefmt = '%Y-%m-%d %H:%M:%S'
async def get_logs():
    channel = client.get_channel(CHANNEL_ID)
    data = []
    counter = 0

    # get last msgid from discord
    lastmsgid = DiscordMessage.objects.order_by('-timestamp').first().messageid
    lastmsg = await client.get_message(channel, lastmsgid)


    kwargs = {'after': lastmsg}

    # Gets up to 100 messages since last importing.
    async for msg in client.logs_from(channel, limit=100, **kwargs, reverse=True):
        data.append({
            'timestamp': msg.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'authorid': msg.author.id,
            'author': msg.author.name + '#' + msg.author.discriminator,
            'content': msg.content,
            'msgid': msg.id,
            'channelid': CHANNEL_ID,
            'serverid': msg.server.id
        })
        lastmsg = msg
        counter += 1

    if len(data) != 0:
        # Split data into snips
        SNIP = []
        snips = []
        for msg in data:
            if len(SNIP) == 0:
                SNIP.append(msg)
            else:
                # if last msg was sent by different person
                # OR was sent more than 2 minutes ago
                # break into new snip
                lastmsg = SNIP[-1]
                lasttime = datetime.datetime.strptime(lastmsg['timestamp'], timefmt)
                thistime = datetime.datetime.strptime(msg['timestamp'], timefmt)
                if lastmsg['authorid'] != msg['authorid'] or \
                        (thistime - lasttime).total_seconds() > 120:
                    # Pop snip and start new one
                    snips.append(SNIP)
                    SNIP = [msg]
                else:
                    SNIP.append(msg)
        snips.append(SNIP)
        for snip in snips:
            process_snip(snip)

    print('Retrieved {} messages, stored.'.format(counter))
    sys.exit(0)


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    # scrape the missed logs on startup
    await get_logs()


@client.event
async def on_message(message):
    if message.author.id == '164963698274729985':
        pass
    print(message.author, message.content)


client.run(os.environ['BOTTOKEN'])
