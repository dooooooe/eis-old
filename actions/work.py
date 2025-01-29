import time
import random
from storage import userdata

async def run(ctx):
    userid = ctx.author.id
    data = await userdata.get_data(userid)
    last_worked = float(data['last_worked'])

    cooldown = 120
    diff = time.time() - last_worked
    remaining = round(cooldown - diff)

    if remaining > 0:
        time_parts = [(remaining // 86400, "day"), ((remaining % 86400) // 3600, "hour"), ((remaining % 3600) // 60, "minute"), (remaining % 60, "second")]
        non_zero_parts = [f"{v} {n}{'s' if v != 1 else ''}" for v, n in time_parts if v > 0]

        if len(non_zero_parts) > 2:
            time_string = ", ".join(non_zero_parts[:-1]) + ", and " + non_zero_parts[-1]

        elif len(non_zero_parts) == 2:
            time_string = " and ".join(non_zero_parts)
            
        else:
            time_string = non_zero_parts[0]

        await ctx.reply(f'You must wait {time_string} to work again')

    else:
        earnings = random.randint(0, 20)
        
        data = await userdata.get_data(userid)
        balance = data['money']

        await userdata.set_data(userid, money=balance + earnings, last_worked=time.time())

        if earnings == 0:
            await ctx.reply('You worked hard and earned 0 fucking bits you stupid fucking retard. You absolute fucking muggle. You got fucking nothing. You should fucking kill yourself right now you completely useless piece of shit disgusting specimen of a subhuman worm. Eat shit and die.')

        elif earnings > 10:
            await ctx.reply(f'You worked extra hard and earned {earnings} bits!')

        else:
            await ctx.reply(f'You worked hard and earned {earnings} bit' + ('s' if earnings != 1 else ''))