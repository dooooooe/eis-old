import random
import time
import asyncio
import collections
import discord
from storage import userdata

class Maze: # chatgpt xd
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.maze = [['#' for _ in range(width)] for _ in range(height)]
        self.start = (0, 0)
        self.end = (height - 1, width - 1)
        self.character_pos = self.start
        self.generate_maze()
        self.place_character()


    def generate_maze(self): # THIS BREAKS ON EVEN NUMBERS FOR SOME REASON
        """Generate a maze using recursive backtracking to ensure a valid path."""
        def carve_path(x, y):
            directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
            random.shuffle(directions)
            for dx, dy in directions:
                nx, ny = x + dx * 2, y + dy * 2
                if 0 <= nx < self.height and 0 <= ny < self.width and self.maze[nx][ny] == '#':
                    self.maze[x + dx][y + dy] = ' '
                    self.maze[nx][ny] = ' '
                    carve_path(nx, ny)

        self.maze[0][0] = ' '  # Start point
        carve_path(0, 0)
        self.maze[self.height - 1][self.width - 1] = 'E'  # End point


    def place_character(self):
        self.character_pos = self.start
        x, y = self.start
        self.maze[x][y] = 'C'


    def move(self, direction):
        moves = {
            'up': (-1, 0),
            'down': (1, 0),
            'left': (0, -1),
            'right': (0, 1)
        }
        if direction not in moves:
            return

        dx, dy = moves[direction]
        cx, cy = self.character_pos
        nx, ny = cx + dx, cy + dy

        if 0 <= nx < self.height and 0 <= ny < self.width and self.maze[nx][ny] != '#':
            self.maze[cx][cy] = ' '
            self.character_pos = (nx, ny)

            if self.maze[nx][ny] == 'E':
                self.maze[nx][ny] = 'X'
                return True
            
            self.maze[nx][ny] = 'C' 

        return False


    def shortest_path(self):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        queue = collections.deque([(self.start, 0)])
        visited = set([self.start])

        while queue:
            (x, y), dist = queue.popleft()

            if (x, y) == self.end:
                return dist

            for dx, dy in directions:
                nx, ny = x + dx, y + dy

                if 0 <= nx < self.height and 0 <= ny < self.width and (nx, ny) not in visited:
                    if self.maze[nx][ny] != '#':
                        queue.append(((nx, ny), dist + 1))
                        visited.add((nx, ny))
    
    
    def to_discord(self):
        d_str = ('🟦' * (self.width + 2)) + '\n'

        for y, row in enumerate(self.maze):
            d_str += '🟦'

            for x, column in enumerate(row):
                space = self.maze[y][x]

                if space == '#':
                    d_str += '🟦'

                elif space == ' ':
                    d_str += '⬛'

                elif space == 'C':
                    d_str += '🔲'

                elif space == 'E':
                    d_str += '💰'

                elif space == 'X':
                    d_str += '<:921031:1333441161368567808>'

                else:
                    d_str += '❓'

            d_str += '🟦\n'

        d_str += ('🟦' * (self.width + 2)) + '\n'

        return d_str
    

    def display_maze(self):
        for row in self.maze:
            print(''.join(row))


    def play(self):
        print("Welcome to the Maze Game!")
        print("Use 'up', 'down', 'left', or 'right' to move the character.")
        print("Reach 'E' to win the game!")
        self.display_maze()

        while True:
            direction = input("Enter your move: ").lower()
            if direction in ['up', 'down', 'left', 'right']:
                if self.move(direction):
                    print("Game over. Thanks for playing!")
                    break
                self.display_maze()
            else:
                print("Invalid input. Please use 'up', 'down', 'left', or 'right'.")


async def run(ctx, client, userid, target):
    if target == userid:
        await ctx.reply('You successfully stole 1 gorillion bits from yourself!')
        return

    t_data = await userdata.get_data(target)
    t_bal = t_data['money']
    t_name = ctx.guild.get_member(target).name

    cooldown = 600
    remaining = round(cooldown - (time.time() - t_data['last_stolen']))

    if remaining > 0:
        time_parts = [(remaining // 86400, "day"), ((remaining % 86400) // 3600, "hour"), ((remaining % 3600) // 60, "minute"), (remaining % 60, "second")]
        non_zero_parts = [f"{v} {n}{'s' if v != 1 else ''}" for v, n in time_parts if v > 0]

        if len(non_zero_parts) > 2:
            time_string = ", ".join(non_zero_parts[:-1]) + ", and " + non_zero_parts[-1]

        elif len(non_zero_parts) == 2:
            time_string = " and ".join(non_zero_parts)
            
        else:
            time_string = non_zero_parts[0]

        await ctx.reply(f'You must wait {time_string} to steal from {t_name}.')
        return

    if t_bal < 50:
        await ctx.reply(f'{t_name} is too broke!')
        return
    
    await userdata.set_data(target, last_stolen=time.time())
    
    size = 11

    m = Maze(size, size)
    game = await ctx.reply(f'Entering {t_name}\'s vault...')
    
    options = {
        '⬅️': 'left', 
        '⬆️': 'up', 
        '⬇️': 'down', 
        '➡️': 'right'}
    
    await add_reactions(game, options.keys())

    success = False
    timeout = m.shortest_path() + 2
    start_time = time.time()
    
    async def timer():
        await asyncio.sleep(timeout)


    async def check_reactions():
        while True:
            message = await game.channel.fetch_message(game.id)  # Fetch latest message state
            bot_reactions = {reaction.emoji for reaction in message.reactions if reaction.me}  # Bot's reactions

            for emoji in options.keys():  # Check expected reactions
                if emoji not in bot_reactions:  # If missing, re-add
                    await game.add_reaction(emoji)
                    await game.channel.send(file=discord.File("./storage/images/reaction_removed.png"))

            await asyncio.sleep(1)  # Check every second


    async def game_loop():
        nonlocal success
        while True:
            await game.edit(content=f'**{t_name}\'s vault**\n' + m.to_discord() + f'\nGet to the 💰 in {timeout} seconds!')

            reaction = await wait_for_reactions(client, userid, game, options.keys(), timeout)

            if reaction is None:
                continue

            m.move(options[reaction])

            if m.character_pos == m.end:
                success = True
                break


    loop_tasks = [asyncio.create_task(game_loop()), asyncio.create_task(check_reactions()), asyncio.create_task(timer())]
    done, pending = await asyncio.wait(loop_tasks, return_when=asyncio.FIRST_COMPLETED)

    for task in pending:
        task.cancel()

    await game.clear_reactions()

    if success:
        heist_time = round(time.time() - start_time, 1)

        await game.edit(content=f'**{t_name}\'s vault**\n' + m.to_discord() + f'\nYou successfully stole 💰 from {t_name} in {heist_time} seconds!')

        stolen_percent = random.uniform(10, 15) / 100
        stolen = round(t_bal * stolen_percent)

        await game.add_reaction('💰')
        await wait_for_reactions(client, userid, game, '💰', 10)
        await game.clear_reactions()

        u_data = await userdata.get_data(userid)
        u_bal = u_data['money']

        t_data = await userdata.get_data(target)
        t_bal = t_data['money']

        await userdata.set_data(userid, money=u_bal + stolen)
        await userdata.set_data(target, money=t_bal - stolen)

        await game.edit(content=f'**{t_name}\'s vault**\n' + m.to_discord() + f'\nYou successfully stole {stolen} bits from {t_name} in {heist_time} seconds!')
        with open('./storage/steal/steal_log.txt', 'a') as file:
            file.write('1')

    else:
        await game.edit(content=f'**{t_name}\'s vault**\n' + m.to_discord() + f'\nHeist unsuccessful...')
        with open('./storage/steal/steal_log.txt', 'a') as file:
            file.write('0')

    await userdata.set_data(target, last_stolen=time.time())


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