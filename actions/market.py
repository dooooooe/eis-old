import re
import numpy as np
import discord
from sklearn.linear_model import RANSACRegressor
from storage import userdata, stocks

async def run(ctx, client, content, cmds):
    if content in cmds:
        await ctx.reply(await market_str())
        return
    
    r = re.match('(' + '|'.join(cmds) + ') .*', content)

    if not r:
        return

    prefix = r.group(1) + ' '
    
    # view
    if content.startswith(prefix + 'view '):
        to_view = content[len(prefix + 'view '):]

        stock = await stocks.get_stock(to_view.upper())

        if stock:
            await view(ctx, stock)
        
        else:
            await ctx.reply('Stock not found!')
            return
        
        return
    
    # buy
    if content.startswith(prefix + 'buy '):
        r = re.match(f'{prefix}buy ' + r'(.+)(?: (\d+))?', content)

        if not r:
            await ctx.reply('To buy a stock, type \'estock buy `stock` `amount`\'')
            return

        stock = await stocks.get_stock(r.group(1).upper())
        amount = int(r.group(2)) if r.group(2) else 1

        if stock:
            await buy(ctx, stock, amount)

        else:
            await ctx.reply('Stock not found!')
            return
    
        return
    
    # sell
    if content.startswith(prefix + 'sell '):
        r = re.match(f'{prefix}sell ' + r'(.+)(?: (\d+))?', content)

        if not r:
            await ctx.reply('To sell a stock, type \'estock sell `stock` `amount`\'')
            return

        stock = await stocks.get_stock(r.group(1).upper())
        amount = int(r.group(2)) if r.group(2) else 1

        if stock:
            await sell(ctx, stock, amount)

        else:
            await ctx.reply('Stock not found!')
            return
        
        return
        

async def view(ctx, stock):
    symbol = stock['symbol']
    price = stock['price']
    full_price_change = get_price_change(stock['history'])
    price_change = get_price_change(stock['history'][-288:])
    trend = get_trend(price_change)

    volatility = stock['variance']
    ev = stock['EV']

    desc = stock['desc']
    graph = discord.File(await stocks.to_graph(symbol), f'{symbol} graph.png')

    positive = '+' if price_change > 0 else ''

    await ctx.reply(f"**{symbol}** ({trend})\nValuation: {price} bits\n\nShort Trend: {price_change}%\nLong Trend: {positive}{full_price_change}%\n\nVolatility: {volatility}\nDrift: {ev}\n\n'*{desc}*'", file=graph)


async def buy(ctx, stock, amount):
    userid = ctx.author.id
    balance = await userdata.get_data(userid, 'money')

    symbol = stock['symbol']
    price = stock['price']

    cost = round(price * amount)

    if cost > balance:
        await ctx.reply('You do not have enough bits!')
        return
    
    await userdata.set_data(userid, money=balance - cost)
    await userdata.adjust_inventory(userid, 'portfolio', symbol, amount)
    await stocks.set_stock(symbol, owners=list(set(stock['owners'] + [userid])))

    await ctx.reply(f'Purchased {amount} shares of {symbol} for {cost} bits!')


async def sell(ctx, stock, amount):
    userid = ctx.author.id
    data = await userdata.get_data(userid)

    balance = data['money']
    portfolio = data['inventory']['portfolio']

    symbol = stock['symbol']
    price = stock['price']

    owned = portfolio[symbol]

    if symbol in portfolio and owned >= amount:
        profit = round(price * amount)

        await userdata.set_data(userid, money=balance + profit)
        await userdata.adjust_inventory(userid, 'portfolio', symbol, -amount)

        if owned == amount:
            await stocks.set_stock(symbol, owners=stock['owners'].remove(userid))

        await ctx.reply(f'Sold {amount} shares of {symbol} for {profit} bits')

    else:
        await ctx.reply(f'You do not own {amount} shares of {symbol}!')


async def market_str():
    stocks_list = []
    crypto_list = []
    misc_list = []

    for symbol in stocks.get_all_stocks():
        stock = await stocks.get_stock(symbol)

        if stock['type'] == 'stock':
            stocks_list.append(stock)

        elif stock['type'] in ['crypto', 'coin']:
            crypto_list.append(stock)

        else:
            misc_list.append(stock)

    d_str = '# **Stock Market**\n'

    def add_stock(stock):
        symbol = stock['symbol']
        price = stock['price']
        
        price_change = get_price_change(stock['history'][-288:])
        trend = get_trend(price_change)

        positive = '+' if price_change > 0 else ''

        nonlocal d_str
        d_str += f'{trend} **{symbol}** - {price} ({positive}{price_change}%)\n'


    d_str += '**Stocks:**\n'

    if len(stocks_list) == 0:
        d_str += '*No stocks available at the moment...*\n'

    for stock in stocks_list:
        add_stock(stock)

    d_str += '-# Stocks endorsed by the EIS as stable, quality assured investments. Please invest responsibly.\n\n'
    d_str += '**Crypto:**\n'

    if len(crypto_list) == 0:
        d_str += '*No shitcoins available at the moment...*\n'

    for coin in crypto_list:
        add_stock(coin)

    d_str += '-# Cryptocurrencies are extremely volatile securities which will expire once valuation drops below 1 bit. Upon expiry, all owned shares will be lost. Please invest responsibly.\n\n'

    if len(misc_list) != 0:
        d_str += '**Miscellaneous:**\n\n'

        for misc in misc_list:
            add_stock(misc)

        d_str += '-# Miscellaneous stocks operate under unique mechanics. View each stock to learn more.\n\n'

    d_str += 'Use \'estock view `symbol`\' to learn more about each stock. Use \'estock buy `symbol` `amount`\' to buy stocks'

    return d_str


def get_price_change(history):
    window_size = 20
    smoothed_history = np.convolve(history, np.ones(window_size)/window_size, mode='valid')

    ransac = RANSACRegressor()
    time_steps = np.arange(len(smoothed_history)).reshape(-1, 1)
    ransac.fit(time_steps, smoothed_history)
        
    price_change = (smoothed_history[-1] - smoothed_history[0]) / smoothed_history[0] * 100

    return round(price_change, 2)


def get_trend(price_change):
    trend = None
    
    if price_change > 50:
            trend = '🚀'
    elif price_change > 20:
        trend = '<:upup:1335519841570000917>'
    elif price_change > 5:
        trend = '<:up:1335519831813914634>'
    elif price_change > -5:
        trend = '🔹'
    elif price_change > -20:
        trend = '<:down:1335519822691303455>'
    elif price_change > -50:
        trend = '<:downdown:1335519812956327936>'
    else:
        trend = '💥'

    return trend