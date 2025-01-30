import random
from storage import userdata

async def run(ctx, wager):
    userid = ctx.author.id
    balance = await userdata.get_data(userid, 'money')

    if balance < wager:
        await ctx.reply('You do not have enough bits!')

    payout = random.choice((1, -1))

    if payout == 1:
        await ctx.reply(f'You won {wager} bit' + ('s!' if wager != 1 else '!'))
        await userdata.update_history(userid, 'game_history', 'W')

    else:
        await ctx.reply('<:mimimimimimimi:1332364481694666873>')
        await userdata.update_history(userid, 'game_history', 'L')

    balance = await userdata.get_data(userid, 'money')
    await userdata.set_data(userid, money=balance + wager*payout)