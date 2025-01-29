import re
import dotenv
import os
from storage import userdata
from actions import work, give, steal, gamble, connect_four, check_balance, check_leaderboard, check_game_history

dotenv.load_dotenv()
PREFIX = os.getenv('PREFIX')

async def process(client, ctx): # if message starts with command and matches param regex, grab params and run associated command
    off_channels = [1080247854922203146]
    if ctx.channel.id in off_channels:
        return
    
    content = ctx.content
    print(content)

    async def id_is_user(id):
        member = ctx.guild.get_member(id)

        if member == None:
            await ctx.reply('User not found!')
            return False
        
        else:
            return True

    # help 
    if content == PREFIX + 'help':
        await ctx.reply('<:sun:1332391811951624212>')

    # work
    elif content == PREFIX + 'work':
        await work.run(ctx)

    # give
    elif content.startswith(tuple(PREFIX + x for x in ('give', 'gift', 'pay'))):
        r = re.match(r'^(give|gift|pay) <@(\d{18,19})> (\d+)$', content[len(PREFIX):])
        if r:
            id = ctx.author.id
            recipient = int(r.group(2))
            value = int(r.group(3))

            if await id_is_user(recipient):
                await give.run(ctx, id, recipient, value)
        
        else:
            await ctx.reply(f'To give someone bits, type \'{PREFIX}give `user` `value`\'')

    # steal
    elif content.startswith(tuple(PREFIX + x for x in ('steal', 'rob', 'heist'))):
        r = re.match(r'^(steal|rob|heist) <@(\d{18,19})>$', content[len(PREFIX):])
        if r:
            id = ctx.author.id
            target = int(r.group(2))

            if await id_is_user(target):
                await steal.run(ctx, client, id, target)
        
        else:
            await ctx.reply(f'To steal someone\'s bits, type \'{PREFIX}steal `user`\'')

    # gambling !
    elif content.startswith(PREFIX + 'gamble'):
        r = re.match(r'^gamble( (\d+))?$', content[len(PREFIX):])
        if r:
            wager = r.group(2)
            wager = int(wager) if wager else 1
            
            await gamble.run(ctx, wager)

        else:
            await ctx.reply(f'To gamble, type \'{PREFIX}gamble `value`\'')

    # connect 4
    elif content.startswith(tuple(PREFIX + x for x in ('connect4', 'connectfour', 'c4'))):
        r = re.match(r'^(connect4|connectfour|c4) <@(\d{18,19})>( \d+)?( freaky)?$', content[len(PREFIX):])
        if r:
            id = ctx.author.id
            opponent = int(r.group(2))
            wager = r.group(3)
            wager = int(wager) if wager else 0
            freaky = r.group(4)
            freaky = True if freaky else False

            if await id_is_user(opponent):
                await connect_four.run(client, ctx, id, opponent, wager, freaky)

        else:
            await ctx.reply(f'To play Connect 4, type \'{PREFIX}c4 `user` `value`\'')

    # check balance
    elif content.startswith(tuple(PREFIX + x for x in ('bal', 'balance', 'money', 'bits'))):
        r = re.match(r'^(bal|balance|money|bits)( <@(\d{18,19})>)?$', content[len(PREFIX):])
        if r:
            id = r.group(3)
            id = int(id) if id else ctx.author.id
        
            if await id_is_user(id):
                await check_balance.run(ctx, id)

        else:
            await ctx.reply(f'To check a balance, type \'{PREFIX}bal `user`\'')

    # check leaderboard
    elif content in [PREFIX + x for x in ['lb', 'leaderboard']]:
        await check_leaderboard.run(ctx)

    # check game history
    elif content.startswith(tuple(PREFIX + x for x in ('wl', 'winloss', 'gamehistory'))):
        r = re.match(r'^(wl|winloss|gamehistory)( <@(\d{18,19})>)?$', content[len(PREFIX):])
        if r:
            id = r.group(3)
            id = int(id) if id else ctx.author.id

            if await id_is_user(id):
                await check_game_history.run(ctx, id)

        else:
            await ctx.reply(f'To check game history, type \'{PREFIX}wl `user`\'')


async def startup():
    userids = await userdata.get_all_users()

    for userid in userids:
        await userdata.set_data(userid, ingame=False)