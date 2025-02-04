from storage import userdata

async def run(ctx, userid, recipient, value):
    if userid == recipient:
        await ctx.reply(f'You gave yourself {value} bits!')
        return

    u_data = await userdata.get_data(userid)
    u_bal = u_data['money']

    if value > u_bal:
        await ctx.reply('You do not have enough bits!')
        return

    r_data = await userdata.get_data(recipient)
    r_bal = r_data['money']

    await userdata.set_data(userid, money=u_bal - value)
    await userdata.set_data(recipient, money=r_bal + value)
    
    u_name = ctx.author.name
    r_name = ctx.guild.get_member(recipient).name

    await ctx.reply(f'{u_name} gave {r_name} {value} bits!')