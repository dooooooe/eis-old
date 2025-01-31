import re
from storage import userdata

DOOE_PREFIX = 'eis '

async def process(client, ctx):
    content = ctx.content
    print(content)

    def re_match(commands, user=None, value=None, percent=None, string=None, freaky=None):
        pattern = r'^' + '(?:' + '|'.join(re.escape(command) for command in commands) + ')'

        if user:
            pattern += r'(?: ((?:<@\d{18,19}>)|.+))' + ('?' if user == 'optional' else '')

        if value:
            pattern += r'(?: (-?\d+' + ('%?))' if percent else '))') + ('?' if value == 'optional' else '')

        if string:
            pattern += r'(?: (.+))' + ('?' if string == 'optional' else '')

        if freaky:
            pattern += '( freaky)?'

        pattern += '$'

        return re.match(pattern, content)
    

    async def to_userid(group):
        if group is None:
            return -1
        
        elif re.match(r'<@\d{18,19}>', group):
            return int(group[2:-1])
        
        else:
            for userid in await userdata.get_all_users():
                name = ctx.guild.get_member(userid).name
                nickname = await userdata.get_data(userid, 'nickname')

                if group in [name, nickname]:
                    return userid
            
            return -1
    

    async def id_is_user(id):
        member = ctx.guild.get_member(id)

        if member == None:
            await ctx.reply('User not found!')
            return False
        
        else:
            return True
    
    # add balance
    addbal_cmds = tuple(DOOE_PREFIX + x for x in ('addbal', 'addbalance', 'addbits', 'give', 'givebits'))
    if content.startswith(addbal_cmds):
        r = re_match(addbal_cmds, user=True, value=True)
        if r:
            id = await to_userid(r.group(1))
            amount = int(r.group(2))

            if await id_is_user(id):
                data = await userdata.get_data(id)
                bal = data['money']
                name = data['name']
                bal += amount
                await userdata.set_data(id, money=bal)
                await ctx.reply(f'gave {name} {amount} bits')

        else:
            await ctx.reply('eis give `user` `amount`')

        return

    # set balance
    setbal_cmds = tuple(DOOE_PREFIX + x for x in ('setbal', 'setbalance', 'setbits'))
    if content.startswith(setbal_cmds):
        r = re_match(setbal_cmds, user=True, value=True)
        if r:
            id = await to_userid(r.group(1))
            amount = int(r.group(2))

            if await id_is_user(id):
                name = await userdata.get_data(id, 'name')
                await userdata.set_data(id, money=amount)
                await ctx.reply(f'set {name}\'s balance to {amount} bits')

        else:
            await ctx.reply('eis setbits `user` `amount`')

        return

    # set nick
    setnick_cmds = tuple(DOOE_PREFIX + x for x in ('nickname', 'nick', 'name', 'setnickname', 'setname', 'setnick'))
    if content.startswith(setnick_cmds):
        r = re_match(setnick_cmds, user=True, string=True)
        if r:
            id = await to_userid(r.group(1))
            new_name = r.group(2)

            if await id_is_user(id):
                name = await userdata.get_data(id, 'name')
                await userdata.set_data(id, nickname=new_name)
                await ctx.reply(f'{name} is now known as {new_name}')

        else:
            await ctx.reply('eis setnick `user` `name`')
    
        return 