import rules


@rules.predicate
def session_is_snip_author(session, snip):
    if 'authenticated' not in session or 'discord_id' not in session:
        return False
    return session['discord_id'] == snip.author.discordid


rules.add_rule('can_change_snip', session_is_snip_author)
