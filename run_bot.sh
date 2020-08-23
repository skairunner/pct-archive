#! /bin/sh
cd /root/pct-archive
export PATH=/usr/bin:/usr/local/bin:$PATH
direnv exec . poetry run python bot.py
