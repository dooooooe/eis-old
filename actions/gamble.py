import random
import asyncio
from storage import userdata

async def run(ctx, wager):
    userid = ctx.author.id
    data = await userdata.get_data(userid)
    balance = data['money']

    if balance < wager:
        await ctx.reply('You do not have enough bits!')
        return

    if data['gambling']:
        await ctx.reply('You are already gambling!')
        return

    await userdata.set_data(userid, gambling=True)

    emojis = ['🧀', '🥐', '🍞', '🥛', '🫘' , '🥔']
    one = random.choice(emojis)
    two = random.choice(emojis)
    three = random.choice(emojis)
    
    game = await ctx.reply(f'**Slots**\n1️⃣2️⃣3️⃣\n{one}{two}{three}\n🟦⬛🟦\n\nSpinning...')
    await asyncio.sleep(0.5)

    for i in range(4):
        one = random.choice(emojis)
        two = random.choice(emojis)
        three = random.choice(emojis)

        await game.edit(content=f'**Slots**\n1️⃣2️⃣3️⃣\n{one}{two}{three}\n🟦⬛🟦\n\nSpinning...')
        await asyncio.sleep(0.5)

    payout = 0

    if len(set([one, two, three])) == 1: # jackpot x3 cheese x17
        if one == '🧀':
            payout = 17

            await game.edit(content=f'**Slots**\n1️⃣2️⃣3️⃣\n{one}{two}{three}\n🟦💰🟦\n\n🧀You got **THE BIG CHEESE**!!! You won {wager*payout} (x{payout}) bits!🧀')
            await userdata.update_history(userid, 'game_history', 'W')

        else:
            payout = 3

            await game.edit(content=f'**Slots**\n1️⃣2️⃣3️⃣\n{one}{two}{three}\n🟦💰🟦\n\nJackpot!! You won {wager*payout} (x{payout}) bits!')
            await userdata.update_history(userid, 'game_history', 'W')

    elif len(set([one, two, three])) == 2: # win 1x
        payout = 1
        await game.edit(content=f'**Slots**\n1️⃣2️⃣3️⃣\n{one}{two}{three}\n🟦💵🟦\n\nCongratulations! You won {wager} bit' + ('s!' if wager != 1 else '!'))
        await userdata.update_history(userid, 'game_history', 'W')

    else: #lose -1x
        payout = -1
        await game.edit(content=f'**Slots**\n1️⃣2️⃣3️⃣\n{one}{two}{three}\n🟦⬛🟦\n# <:hehehehaw:1334502426069172246>')
        await userdata.update_history(userid, 'game_history', 'L')
    
    balance = await userdata.get_data(userid, 'money')
    await userdata.set_data(userid, money =balance + wager*payout, gambling=False)