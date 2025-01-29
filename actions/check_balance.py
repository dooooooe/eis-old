from storage import userdata

async def run(ctx, id):
    name = ctx.guild.get_member(id).name

    data = await userdata.get_data(id)
    balance = data['money']

    if balance == 0:
        await ctx.reply(f'{name} is fucking broke!')

    elif balance < 0:
        await ctx.reply(f'Hello! It seems that {name} has obtained a negative balance. Please let dooe know so they can set them back to 0!')
    
    else:
        await ctx.reply(f'{name} has {balance} bit' + ('s' if balance != 1 else ''))