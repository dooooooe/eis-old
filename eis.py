import re
import dotenv
import os
import asyncio
from storage import userdata, stocks
from actions import work, give, steal, coinflip, gamble, connect_four, nickname, inventory, check_balance, check_leaderboard, check_game_history, market

dotenv.load_dotenv()
PREFIX = os.getenv('PREFIX')

async def process(client, ctx): # if message starts with command and matches param regex, grab params and run associated command
    # await ctx.channel.send('hi! this is a test build of eis and shown userdata may not be up to date; additionally, transactions made on the test build will not be recorded on the live build')

    off_channels = [1080247854922203146]
    if ctx.channel.id in off_channels:
        return
    
    content = ctx.content
    
    log_str = f'[{ctx.guild}] {ctx.author}: {content}\n'
    print(log_str)
    with open('log.txt', 'a') as f:
        f.write(log_str)
    
        
    def re_match(commands, user=None, value=None, percent=None, string=None, freaky=None):
        pattern = r'^' + '(?:' + '|'.join(re.escape(command) for command in commands) + ')'

        if user:
            pattern += r'(?: ((?:<@\d{18,19}>)|.+))' + ('?' if user == 'optional' else '')

        if value:
            pattern += r'(?: (\d+' + ('%?))' if percent else '))') + ('?' if value == 'optional' else '')

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
        

    # help 
    if content == PREFIX + 'help':
        await ctx.reply('<:sun:1332391811951624212>')

    # work
    if content == PREFIX + 'work':
        await work.run(ctx)
        return

    # give
    give_cmds = tuple(PREFIX + x for x in ('give', 'gift', 'pay'))

    if content.startswith(give_cmds):
        r = re_match(give_cmds, user=True, value=True)
        if r:
            id = ctx.author.id
            recipient = await to_userid(r.group(1))
            value = int(r.group(2))

            if await id_is_user(recipient):
                await give.run(ctx, id, recipient, value)
        
        else:
            await ctx.reply(f'To give someone bits, type \'{PREFIX}give `user` `value`\'')

        return 

    # steal
    steal_cmds = tuple(PREFIX + x for x in ('steal', 'rob', 'heist'))

    if content.startswith(steal_cmds):
        r = re_match(steal_cmds, user=True)
        if r:
            id = ctx.author.id
            target = await to_userid(r.group(1))

            if await id_is_user(target):
                await steal.run(ctx, client, id, target)
        
        else:
            await ctx.reply(f'To steal someone\'s bits, type \'{PREFIX}steal `user`\'')

        return
    
    # coinflip
    coinflip_cmds = tuple(PREFIX + x for x in ('coinflip', 'flipcoin', 'flip', 'coin'))

    if content.startswith(coinflip_cmds):
        r = re_match(coinflip_cmds, value='optional', percent=True)
        if r:
            wager = r.group(1) if r.group(1) else 1

            if '%' in str(wager):
                wager = int(wager[:-1])/100
                if wager > 0.25:
                    ctx.reply(r'You cannot bet over 25% of your total balance with a percent value! Use the actual number to ensure you know just how much you are betting!')
                    return
                else:
                    wager = round(wager * await userdata.get_data(ctx.author.id, 'money'))
            else:
                wager = int(wager)

            await coinflip.run(ctx, wager)

        else:
            await ctx.reply(f'To flip a coin, type \'{PREFIX}coinflip `value`\'')

        return

    # gambling !
    gamble_cmds = tuple(PREFIX + x for x in ('gamble', 'slots', 'spin'))

    if content.startswith(gamble_cmds):
        r = re_match(gamble_cmds, value='optional', percent=True)
        if r:
            wager = r.group(1) if r.group(1) else 1

            if '%' in str(wager):
                wager = int(wager[:-1])/100
                if wager > 0.25:
                    ctx.reply(r'You cannot bet over 25% of your total balance with a percent value! Use the actual number to ensure you know just how much you are betting!')
                    return
                else:
                    wager = round(wager * await userdata.get_data(ctx.author.id, 'money'))
            else:
                wager = int(wager)
            
            await gamble.run(ctx, wager)

        else:
            await ctx.reply(f'To play slots, type \'{PREFIX}slots `value`\'')

        return

    # connect 4
    c4_cmds = tuple(PREFIX + x for x in ('connect4', 'connectfour', 'c4'))

    if content.startswith(c4_cmds):
        r = re_match(c4_cmds, user=True, value='optional', freaky='optional')
        if r:
            id = ctx.author.id
            opponent = await to_userid(r.group(1))
            wager = int(r.group(2)) if r.group(2) else 0
            freaky = True if r.group(3) else False

            if await id_is_user(opponent):
                await connect_four.run(client, ctx, id, opponent, wager, freaky)

        else:
            await ctx.reply(f'To play Connect 4, type \'{PREFIX}c4 `user` `value`\'')

        return
    
    # nickname
    nickname_cmds = tuple(PREFIX + x for x in ('nickname', 'nick', 'name', 'setnickname', 'setname', 'setnick'))

    if content.startswith(nickname_cmds):
        r = re_match(nickname_cmds, string='optional')
        if r:
            id = ctx.author.id
            name = r.group(1)

            await nickname.run(ctx, id, name)

        else:
            await ctx.reply(f'To set your nickname, type \'{PREFIX}nickname `name`\'')

        return
    
    # inventory
    inv_cmds = tuple(PREFIX + x for x in ('inventory', 'inv', 'checkinv', 'checkinventory'))
    if content in (inv_cmds):
        await inventory.run(ctx)

    # check balance
    bal_cmds = tuple(PREFIX + x for x in ('bal', 'balance', 'money', 'bits'))

    if content.startswith(bal_cmds):
        r = re_match(bal_cmds, user='optional')
        if r:
            id = await to_userid(r.group(1)) if r.group(1) else ctx.author.id
        
            if await id_is_user(id):
                await check_balance.run(ctx, id)

        else:
            await ctx.reply(f'To check a balance, type \'{PREFIX}bal `user`\'')

        return

    # check leaderboard
    if content in [PREFIX + x for x in ['lb', 'leaderboard']]:
        await check_leaderboard.run(ctx)

        return

    # check game history
    game_hist_cmds = tuple(PREFIX + x for x in ('wl', 'winloss', 'gamehistory'))
    if content.startswith(game_hist_cmds):
        r = re_match(game_hist_cmds, user='optional')
        if r:
            id = await to_userid(r.group(1)) if r.group(1) else ctx.author.id

            if await id_is_user(id):
                await check_game_history.run(ctx, id)

        else:
            await ctx.reply(f'To check game history, type \'{PREFIX}wl `user`\'')

        return
    
    # stocks
    stocks_cmds = tuple(PREFIX + x for x in ('stocks', 'stock', 'market'))
    if content.startswith(stocks_cmds):
        await market.run(ctx, client, content, stocks_cmds)


async def startup(client):
    userids = await userdata.get_all_users()

    for userid in userids:
        name = await userdata.get_data(userid, 'name')

        if name == None:
            name = client.get_user(userid).name

        await userdata.set_data(userid, name=name, ingame=False, gambling=False)

    await continuous_tasks()


async def continuous_tasks():
    
    async def tick_all_stocks():
        while True:
            await asyncio.sleep(300)
            for symbol in stocks.get_all_stocks():
                await stocks.tick_stock(symbol)
            
            
    asyncio.create_task(tick_all_stocks())