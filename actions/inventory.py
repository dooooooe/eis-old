from storage import userdata

async def run(ctx):
    userid = ctx.author.id
    data = await userdata.get_data(userid)

    name = data['name']
    inventory = data['inventory']

    d_str = f'# **{name}\'s Inventory**\n'

    for category, items in inventory.items():
        d_str += f'**{category.title()}:**\n'

        for item, amount in items.items():
            d_str += f'> {item} x{amount}\n'

        if len(items) < 3:
            for _ in range(3 - len(items)):
                d_str += '> \n'

        d_str += '\n'

    d_str = d_str[:-2] + '_ _'

    await ctx.reply(d_str)