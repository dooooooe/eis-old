import random
from storage import userdata

results = {
    'win': (1, 31),
    'loss': (-1, 50),
    'jackpot': (20, 1)
}

async def run(ctx, wager):
    userid = ctx.author.id
    data = await userdata.get_data(userid)
    balance = data['money']

    if balance < wager:
        await ctx.reply('You do not have enough bits!')

    else:
        payout = random.choices(list(r[0] for r in results.values()), weights=list(r[1] for r in results.values()), k=1)[0]
        result = None

        if payout == 1:
            result = 'W'
            await ctx.reply(f'You won {wager} bit' + ('s!' if wager != 1 else '!'))

        elif payout == -1:
            result = 'L'
            await ctx.reply('<:mimimimimimimi:1332364481694666873>')

        else:
            result = 'W'
            await ctx.reply(f'**Jackpot!** You won {wager*payout} bits!')

        data = await userdata.get_data(userid)
        balance = data['money']

        await userdata.set_data(userid, money=balance + (wager*payout))
        await userdata.update_history(userid, 'game_history', result)


def get_ev():
    ev = 0
    x = 0

    for payout, chance in list(results.values()):
        ev += payout * chance
        x += chance

    ev = (ev / x) * 100
    
    return ev

# print(f' ev is {round(get_ev(), 2)}% return per play')