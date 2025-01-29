# not the best code but it works

import asyncio
from storage import userdata

class ConnectFour:
    def __init__(self):
        self.winner = None
        self.columns = 7
        self.rows = 6
        self.board = [[' ' for _ in range(self.columns)] for _ in range(self.rows)]
        self.turn = 0
        

    def insert(self, player, column):
        if column in range(self.columns) and player in ['X', 'O']:
            for row in range(self.rows -1, -1, -1):
                if self.board[row][column] == ' ':
                    self.board[row][column] = player
                    self.turn += 1
                    return True
        return False
    
    
    def check_win(self):
        def window(array, x, y, dx, dy, size):
            try:
                return [array[y+(s*dy)][x+(s*dx)] for s in range(size)]
            except IndexError:
                return [' ', ' ', ' ', ' ']
        
        for x in range(self.columns):
            for y in range(self.rows):
                windows = [window(self.board, x, y, dx, dy, 4) for dx, dy in [(1, 0), (0, 1), (1, 1), (1, -1)]]
                
                for w in windows:
                    if w and all(x == w[0] and x != ' ' for x in w):
                        self.winner = w[0]
                        return True
        return False
    

    def slide(self):
        for row in range(self.rows - 1, -1, -1):
            if row % 2 == 0:
                self.board[row] = [self.board[row][-1]] + self.board[row][:-1]

            else:
                self.board[row] = self.board[row][1:] + [self.board[row][0]]
    

    def fall(self):
        moved = False
        
        for col in range(self.columns):
            for row in range(self.rows - 2, -1, -1): 
                if self.board[row][col] != ' ' and self.board[row + 1][col] == ' ':
                    self.board[row + 1][col] = self.board[row][col]
                    self.board[row][col] = ' '
                    moved = True
        
        return moved


    def to_discord(self, freaky: bool=False):
        d_str = ('🟦' if freaky else '') + '1️⃣2️⃣3️⃣4️⃣5️⃣6️⃣7️⃣' + ('🟦\n' if freaky else '\n')

        for row in range(self.rows):
            if freaky:
                if row % 2 == 0:
                    d_str += '➡️'
                else:
                    d_str += '⬅️'

            for column in range(self.columns):
                slot = self.board[row][column]

                if row%2 == column%2:
                    d_str += '<:redlightgray:1332993329935155211>' if slot == 'O' else '<:bluelightgray:1332993967444201482>' if slot == 'X' else '<:lightgray:1332989657583058965>'

                else:
                    d_str += '<:redgray:1332993584168828969>' if slot == 'O' else '<:bluegray:1332993982023598194>' if slot == 'X' else '<:gray:1332991510576107573>'
                
            if freaky:
                if row % 2 == 0:
                    d_str += '➡️'
                else:
                    d_str += '⬅️'
            
            d_str += '\n'

        return d_str
    

    def print_board(self):
        print('\n ' + ''.join(str(col + 1) for col in range(self.columns)))

        for y in range(self.rows):
                print('>', end='')

                for x in range(self.columns):
                    print(self.board[y][x], end='')
                    
                print('<')


    def play(self):
        print('Connect 4!')
        
        players = ['O' ,'X']

        while self.turn < self.rows * self.columns:
            player = players[self.turn % 2]

            self.print_board()
            print(f'{player} to play...')

            while True:
                try:
                    if self.insert(player, int(input()) - 1):
                        break
                    else:
                        print('Invalid row!')

                except ValueError:
                    print(f'Invalid input! Please select a column from 1-{self.columns}.')

            if self.check_win():
                self.print_board()
                print(f'{self.winner} won!!!')
                break


async def run(client, ctx, p1, p2, wager, freaky: bool=False):
    vs_self = True
    if p1 == p2 and not vs_self:
        await ctx.reply('You can not play against yourself.')
        return

    p1_name = ctx.author.name
    p1_data = await userdata.get_data(p1)
    p1_bal = p1_data['money']
    
    if p1_data['ingame']:
        await ctx.reply('You are already in a game!')
        return
    
    if p1_bal < wager:
        await ctx.reply('You do not have enough bits!')
        return

    p2_name = ctx.guild.get_member(p2).name
    p2_data = await userdata.get_data(p2)
    p2_bal = p2_data['money']

    if p2_data['ingame']:
        await ctx.reply(f'{p2_name} is currently in a game.')
        return
    
    if p2_bal < wager:
        await ctx.reply(f'{p2_name} does not have enough bits!')
        return
    
    stakes = round(wager/p2_bal * 100, 1)
    high_stakes = True if stakes >= 25 and wager > 10 else False

    await userdata.set_data(p1, ingame=True)
    
    game = await ctx.reply(f'**Connect 4**\n{p1_name} has challenged {p2_name} to Connect 4!\n' + (f'\nBet: {wager} bits' if wager != 0 else '') + f'\n{p2_name} has 20 seconds to accept...')
    await add_reactions(game, ['✅', '❌'])

    reaction = await wait_for_reactions(client, p2, game, ['✅', '❌'], 20)
    accept = True if reaction == '✅' else False

    if high_stakes and accept:
        await game.edit(content=f'**Connect 4**\n{p1_name} has challenged {p2_name} to Connect 4!\n\nBet: {wager} bits\n{p2_name}, are you sure? This bet is {stakes}% of your total balance!')
        await add_reactions(game, ['✅', '❌']) 

        reaction = await wait_for_reactions(client, p2, game, ['✅', '❌'], 20)
        accept = True if reaction == '✅' else False

    await game.clear_reactions()

    if accept:
        await game.edit(content=f'**Connect 4**\n{p1_name} has challenged {p2_name} to Connect 4!\n\n{p2_name} has accepted!')

    else:
        await game.edit(content=f'**Connect 4**\n{p1_name} has challenged {p2_name} to Connect 4!\n\n{p2_name} declined...')
        await userdata.set_data(p1, ingame=False)
        return
    
    # game actually starts
    await userdata.set_data(p2, ingame=True)

    c = ConnectFour()

    options = {
        '1️⃣': 0, 
        '2️⃣': 1, 
        '3️⃣': 2, 
        '4️⃣': 3, 
        '5️⃣': 4, 
        '6️⃣': 5, 
        '7️⃣': 6}

    await add_reactions(game, options.keys())

    winner = None
    loser = None

    game_over = False

    while True:
        p = p1 if c.turn % 2 == 1 else p2
        state = '\n'

        if freaky and not c.check_win() and c.turn % 5 == 0 and c.turn != 0:
            await game.edit(content='**Connect 4**\n' + c.to_discord() + '\n Sliding...')
            await asyncio.sleep(0.5)

            c.slide()
            await game.edit(content='**Connect 4**\n' + c.to_discord() + '\n Sliding...')
            await asyncio.sleep(0.5)

            if c.fall():
                await game.edit(content='**Connect 4**\n' + c.to_discord() + '\n Sliding...')
                await asyncio.sleep(0.2)

            await asyncio.sleep(0.5)
    
        if c.check_win():
            winner, winner_name, winner_bal = ((p1, p1_name, p1_bal) if c.winner == 'O' else (p2, p2_name, p2_bal))
            loser, loser_bal = ((p2, p2_bal - wager) if winner == p1 else (p1, p1_bal - wager))
            
            state += f'{winner_name} has won' + (f' {wager} bits!' if wager != 0 else '!')
            game_over = True

        elif c.turn >= c.rows * c.columns:
            state += 'Game ended in a draw.'
            game_over = True
        
        if not game_over:
            if freaky and not c.check_win():
                next_slide = 5 - c.turn % 5
                state += f'Next slide in {next_slide} turn' + ('s\n' if next_slide != 1 else '\n')

            if c.turn % 2 == 1:
                state += f'🔴 to move ({p1_name})'

            else:
                state += f'🔵 to move ({p2_name})'

        await game.edit(content='**Connect 4**\n' + c.to_discord(freaky) + state)
        
        if game_over:
            break

        while True:
            reaction = await wait_for_reactions(client, p, game, options.keys(), 90)

            if reaction == None:
                loser, loser_bal, loser_name = ((p1, p1_bal, p1_name) if c.turn % 2 == 1 else (p2, p2_bal, p2_name))
                winner, winner_bal = ((p1, p1_bal) if winner == p2 else (p2, p2_bal))
                game_over = True

                await game.edit(content='**Connect 4**\n' + c.to_discord(freaky) + f'\n{loser_name} has forfeited by timeout.')

            elif c.insert('O' if c.turn % 2 == 1 else 'X', options[reaction]):
                break
            
            else:
                await game.edit(content='**Connect 4**\n' + c.to_discord(freaky) + state + '\nInvalid column!')

        if game_over:
            break

    await game.clear_reactions()

    if winner != loser:
        await userdata.set_data(winner, money=winner_bal + wager, ingame=False)
        await userdata.set_data(loser, money=loser_bal - wager, ingame=False)

        await userdata.update_history(winner, 'game_history', 'W')
        await userdata.update_history(loser, 'game_history', 'L')

    else:
        await userdata.set_data(p1, ingame=False)
        await userdata.set_data(p2, ingame=False)

        await userdata.update_history(p1, 'game_history', 'D')
        await userdata.update_history(p2, 'game_history', 'D')


async def wait_for_reactions(client, userid, message, reactions, time):
    def check(reaction, user):
        return (
            user.id == userid
            and (str(reaction.emoji) == reactions or str(reaction.emoji) in reactions)
            and reaction.message.id == message.id
        )

    try:
        reaction, user = await client.wait_for("reaction_add", timeout=time, check=check)
        return str(reaction.emoji)

    except asyncio.TimeoutError:
        return None


async def add_reactions(message, reactions):
    await asyncio.gather(*(message.add_reaction(reaction) for reaction in reactions))