from storage import userdata, stocks

async def run(ctx):
    userids = await userdata.get_all_users()

    stock_values = {}

    for stock in stocks.get_all_stocks():
        price = await stocks.get_stock(stock)['price']

        stock_values[stock] = price

    lb = []

    for userid in userids:
        data = await userdata.get_data(userid)
        name = ctx.guild.get_member(userid).name  
        bal = data['money']
        portfolio = data['inventory']['portfolio']

        portfolio_value = 0
        for stock, amount in portfolio.items():
            portfolio_value += stock_values[stock] * amount

        net_worth = bal + portfolio_value

        lb.append((net_worth, name))

    lb.sort(key=lambda x: -x[0])

    lb_str = '## **eis Net Worth Leaderboard**\n'
    counter = 0
    
    for user in lb:
        counter += 1

        name = user[1]
        bal = user[0]

        lb_str += f'> **{counter}. {name}** {bal:,} bits\n'

        if counter == 10:
            break

    await ctx.reply(lb_str)