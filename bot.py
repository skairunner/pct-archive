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
from importsnips import process_snip, get_snip_count

CHANNEL_ID = '406611842257911828'
SNIP_DIFF_REPORT_CHANNEL = '406892517380980747'
logging.basicConfig(level=logging.INFO)
client = discord.Client()

if '--dry-run' in sys.argv:
    IS_DRY_RUN = True
else:
    IS_DRY_RUN = False

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
        # Count # of new snips, and the total for each author
        newsnips = {}
        names = {}
        for snip in snips:
            authorid = snip[0]['authorid']
            if authorid not in newsnips:
                newsnips[authorid] = 1
            else:
                newsnips[authorid] += 1
            names[authorid] = snip[0]['author']

        # Retrieve new total per author
        totalsnips = {}
        for authorid in newsnips:
            totalsnips[authorid] = get_snip_count(authorid) + newsnips[authorid]

        if not IS_DRY_RUN:
            for snip in snips:
                process_snip(snip)

        # Print success
        channel = client.get_channel(SNIP_DIFF_REPORT_CHANNEL)
        formatstring = '{:<32}  {:>2}  {:>3}'
        lines = ['Snip Archive Update ```', formatstring.format('Username', '+', '=')]
        for authorid in newsnips:
            name = names[authorid]
            delta = newsnips[authorid]
            total = totalsnips[authorid]
            lines.append(formatstring.format(name, delta, total))
        lines.append('```')
        content = '\n'.join(lines)
        if IS_DRY_RUN:
            content = '===THIS IS A DRY RUN===\n' + content
        await client.send_message(channel, content)
    else:  # No snips to update
        content = 'No new snips since last run.'
        if IS_DRY_RUN:
            content = '===THIS IS A DRY RUN===\n' + content
        await client.send_message(channel, content)

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
