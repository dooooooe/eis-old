from storage import userdata

async def run(ctx, userid, new_name):
    if new_name is None:
        nickname = userdata.get_data(userid, 'nickname')

        if nickname:
            await ctx.reply(f'Your nickname is {nickname}')

        else:
            await ctx.reply('No nickname set!')

    for id in await userdata.get_all_users():
        name = ctx.guild.get_member(userid).name
        if new_name in (name, await userdata.get_data(userid, 'nickname')):
            await ctx.reply(f'Name already in use by {name}!')
            return
        
    await userdata.set_data(userid, nickname=new_name)
    await ctx.reply(f'Nickname set to {new_name}')