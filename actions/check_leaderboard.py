from storage import userdata

async def run(ctx):
    userids = await userdata.get_all_users()

    lb = []

    for userid in userids:
        data = await userdata.get_data(userid)
        name = ctx.guild.get_member(userid).name  
        bal = data['money']

        lb.append((bal, name))

    lb.sort(key=lambda x: -x[0])

    lb_str = '## **eis Leaderboard**\n'
    counter = 0
    
    for user in lb:
        counter += 1

        name = user[1]
        bal = user[0]

        lb_str += f'> **{counter}. {name}** {bal:,} bits\n'

        if counter == 10:
            break

    await ctx.reply(lb_str)