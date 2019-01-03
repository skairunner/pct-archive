import rules


@rules.predicate
def session_is_snip_author(request, snip):
    session = request.session
    if 'authenticated' not in session or 'discord_id' not in session:
        return False
    return session['discord_id'] == snip.author.discordid


@rules.predicate
def session_is_admin(request, snip):
    return request.user.is_superuser


rules.add_rule('can_change_snip', session_is_snip_author | session_is_admin)
