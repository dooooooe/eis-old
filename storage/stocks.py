import os
import json
import io
import random
import math
import string
import aiofiles
import asyncio
import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
import pandas as pd
from storage import userdata

class Stock:
    def __init__(self, symbol: str, price: float=10, variance: float=0.2, EV: float=0, type: str='stock', desc: str='', history: list=[], owners: list=[]):
        self.symbol = symbol.upper()
        self.price = price
        self.EV = EV
        self.variance = variance
        self.dt = 1 / 288 # tick every 5 minutes (24 * 60 / 5 = 288)
        self.type = type
        self.desc = desc
        self.history = [price] if len(history) == 0 else history
        self.owners = owners
    

    def tick(self):
        Z = random.gauss(0, 1)
        self.price = min(10000, max(0, round(self.price * math.exp((self.EV - 0.5 * self.variance**2) * self.dt + self.variance * math.sqrt(self.dt) * Z), 2)))

        if len(self.history) == 2017: # store 1 week of data
            self.history = self.history[1:]

        self.history.append(self.price)
    

    def plot(self, time_steps=None):
        self.history = self.history[-time_steps:] if time_steps else self.history

        time_steps = pd.date_range(start=pd.Timestamp.now().floor('5min'), periods=len(self.history), freq='5min')
        total_time = (time_steps[-1] - time_steps[0]).total_seconds()

        if total_time > 2 * 24 * 3600:
            time_units = [(t - time_steps[0]).total_seconds() / (24 * 3600) for t in time_steps]
            x_label = 'Day'
        else:
            time_units = [(t - time_steps[0]).total_seconds() / 3600 for t in time_steps]
            x_label = 'Hour'

        plt.figure(figsize=(10, 6))
        plt.gca().set_facecolor('none')

        # coloring !
        slope_threshold = self.variance * 0.02

        for i in range(1, len(self.history)):
            slope = (self.history[i] - self.history[i-1]) / self.history[i-1]
            
            if abs(slope) < slope_threshold:
                color = 'gray'

            elif slope >= 0:
                color = (0.0, 1.0, 0.0)

            else: 
                color = 'red'

            plt.plot(time_units[i-1:i+1], self.history[i-1:i+1], color=color)

        # title
        time_diff = time_steps[-1] - time_steps[0]

        days = time_diff.days
        hours = time_diff.seconds // 3600

        if days == 1 and hours < 4:
            time_label = 'Today'
        
        elif days == 7:
            time_label = 'This week'

        elif days >= 1:
            time_label = f'Last {days}d {hours}h'

        else:
            total_hours = time_diff.total_seconds() / 3600
            time_label = f'Last {total_hours:.0f}h'
        
        title = plt.title(f'{self.symbol} {time_label}', fontsize=20, weight='bold', pad=20)
        xlabel = plt.xlabel(x_label, fontsize=14, labelpad=14, weight='bold')
        ylabel = plt.ylabel('Bits', rotation=0, fontsize=14, labelpad=25, weight='bold')

        plt.xlim(left=0)
        plt.grid(True, color='white', linestyle='--', linewidth=0.5)

        # outline everything
        title_outline_effect = [path_effects.withStroke(linewidth=3, foreground='white')]
        title.set_path_effects(title_outline_effect)

        label_outline_effect = [path_effects.withStroke(linewidth=2, foreground='white')]

        xlabel.set_path_effects(label_outline_effect)
        ylabel.set_path_effects(label_outline_effect)

        outline_effect = [path_effects.withStroke(linewidth=1.5, foreground='white')]

        for label in plt.gca().get_xticklabels() + plt.gca().get_yticklabels():
            label.set_color('black')
            label.set_fontweight('bold')
            label.set_path_effects(outline_effect)

        ax = plt.gca()
        for spine in ax.spines.values():
            spine.set_color('white')

        plt.show()
        plt.close()


    def to_dict(self):
        return {
            'symbol': self.symbol,
            'price': self.price,
            'variance': self.variance,
            'EV': self.EV,
            'dt': self.dt,
            'type': self.type,
            'desc': self.desc,
            'history': self.history,
            'owners': self.owners
        }
    

def stock_path(symbol):
    folder_path = os.path.join(os.path.dirname(__file__), 'stocks')

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    return os.path.join(folder_path, f'{symbol.upper()}.json')


def get_all_stocks():
    folder_path = os.path.join(os.path.dirname(__file__), 'stocks')
    symbols = [f.split('.')[0] for f in os.listdir(folder_path) if f.endswith('.json')]

    return symbols


async def init_stock(symbol: str, price: float=10, variance: float=0.2, EV: float=0, type: str='stock', desc=''):
    stock_file = stock_path(symbol)

    if not os.path.exists(stock_file):
        stock = Stock(symbol, price, variance, EV, type, desc)

        async with aiofiles.open(stock_file, 'w') as f:
            await f.write(json.dumps(stock.to_dict(), indent=4))


async def get_stock(symbol):
    stock_file = stock_path(symbol)

    if not os.path.exists(stock_file):
        return None

    async with aiofiles.open(stock_file, 'r') as f:
        content = await f.read()
        data = json.loads(content)

    return data


async def set_stock(symbol, price=None, variance=None, EV=None, type=None, desc=None, history=None, owners=None):
    new_data = {key: value for key, value in locals().items() if key != "symbol" and value is not None}

    stock_file = stock_path(symbol)

    if not os.path.exists(stock_file):
        return

    data = await get_stock(symbol)

    for key, value in new_data.items():
        data[key] = value

    async with aiofiles.open(stock_file, 'w') as f:
        await f.write(json.dumps(data, indent=4))


async def tick_stock(symbol):
    stock = await to_stock(symbol)
    stock_file = stock_path(symbol)

    stock.tick()

    if stock.price < 1:
        if stock.type == 'stock':
            if random.randint(1,10) == 1:
                stock.price += random.randint(1, 20)

        elif stock.type in ['crypto', 'coin']:
            for owner in stock.owners:
                inventory = await userdata.get_data(owner, 'inventory')
                owned = inventory['portfolio'].get(symbol)
                

                await userdata.adjust_inventory(owner, 'portfolio', symbol, -owned)

            os.remove(stock_file)
            await gen_coin()
            return

    async with aiofiles.open(stock_file, 'w') as f:
        await f.write(json.dumps(stock.to_dict(), indent=4))


async def gen_coin(name=None):
    current = get_all_stocks()

    if name and name not in current:
        symbol = name

    else:
        while True:
            symbol = ''.join(random.choices(string.ascii_uppercase, k=random.randint(2, 4)))
            if symbol not in current:
                break

    price = random.randint(20, 120)
    variance = round(random.uniform(2, 10), 2)
    ev = round(random.uniform(-1, 5), 2)

    cope = [
    "not a loss till you sell",
    "WAGMI",
    "dip is temporary regret is forever.",
    "buy the dip",
    "ignore FUD dont shill invest in DYOR",
    "i survived 2018",
    "zoom out bro",
    "bear markets are where millionaires are made",
    "TO MOON TO MOON TO MOON TO MOON TO MOON TO MOON TO MOON TO MOON TO MOON TO MOON TO MOON",
    "always hold",
    "trust the process",
    "we are early",
    "i didnt lose money, i gained experience",
    "wait for mainstream bro",
    "you think billionaires are worried? exactly.",
    "the fundamentals havent changed",
    "bro its just market manipulation",
    "bitcoin was declared dead like a hundred times we're fine",
    "im just averaging down",
    "its just paper losses",
    "BUY DIP BUY DIP BUY DIP BUY DIP BUY DIP BUY DIP BUY DIP BUY DIP",
    "if youre scared youre doing it wrong",
    "its only down if you check the charts",
    "its not down until you check",
    "im here for the revolution, not the profits",
    "stay bullish, the bears cant win forever",
    "dont fomo into that shitcoin because shill bro DYOR",
    "lambo season is just around the corner",
    "its just crypto winter guys",
    "stop spreading FUD retard",
    "the rug isnt pulled until you sell",
    "the devs are doxxed, no rug here",
    "bro no one knows shit about fuck just HODL.",
    "dont get rekt",
    "TO DA MOOOOOOONN 🚀🚀🚀",
    "anytime my girlfriend threatens to break up with me i tell her to stop spreading FUD",
    "devs out for cigs",
    "buy high sell low",
    "do you want fries with that",
    "this is it gentlemen. just bought 10k.",
    "mister prime minister our economy is down 15%, i advise we invest on some more slurp juices",
    "remember nfts?"
    ]

    desc = random.choice(cope)

    await init_stock(symbol, price, variance, ev, 'coin', desc)


async def to_stock(symbol):
    await init_stock(symbol)

    data = await get_stock(symbol)
    stock = Stock(symbol, data['price'], data['variance'], data['EV'], data['type'], data['desc'], data['history'], data['owners'])

    return stock


async def to_graph(symbol, time_steps=None):
    await init_stock(symbol)
    stock_file = stock_path(symbol)

    async with aiofiles.open(stock_file, 'r') as f:
        content = await f.read()
        data = json.loads(content)

    history = data['history']
    history = history[-time_steps:] if time_steps else history

    time_steps = pd.date_range(start=pd.Timestamp.now().floor('5min'), periods=len(history), freq='5min')
    total_time = (time_steps[-1] - time_steps[0]).total_seconds()

    if total_time > 2 * 24 * 3600:
        time_units = [(t - time_steps[0]).total_seconds() / (24 * 3600) for t in time_steps]
        x_label = 'Day'

    else:
        time_units = [(t - time_steps[0]).total_seconds() / 3600 for t in time_steps]
        x_label = 'Hour'

    plt.figure(figsize=(10, 6))
    plt.gca().set_facecolor('none')

    # coloring !
    slope_threshold = data['variance'] * 0.02

    for i in range(1, len(history)):
        slope = (history[i] - history[i-1]) / history[i-1]
        
        if abs(slope) < slope_threshold:
            color = 'gray'

        elif slope >= 0:
            color = (0.0, 1.0, 0.0)

        else: 
            color = 'red'

        plt.plot(time_units[i-1:i+1], history[i-1:i+1], color=color)
    
    # title
    time_diff = time_steps[-1] - time_steps[0]

    days = time_diff.days
    hours = time_diff.seconds // 3600

    if days == 1 and hours < 4:
        time_label = 'Today'
    
    elif days == 7:
        time_label = 'This week'

    elif days >= 1:
        time_label = f'Last {days}d {hours}h'

    else:
        total_hours = time_diff.total_seconds() / 3600
        time_label = f'Last {total_hours:.0f}h'
    
    title = plt.title(f'{symbol} {time_label}', fontsize=20, weight='bold', pad=20)
    xlabel = plt.xlabel(x_label, fontsize=14, labelpad=14, weight='bold')
    ylabel = plt.ylabel('Bits', rotation=0, fontsize=14, labelpad=25, weight='bold')

    plt.xlim(left=0)
    plt.grid(True, color='white', linestyle='--', linewidth=0.5)

    # outline everything
    title_outline_effect = [path_effects.withStroke(linewidth=3, foreground='white')]
    title.set_path_effects(title_outline_effect)

    label_outline_effect = [path_effects.withStroke(linewidth=2, foreground='white')]

    xlabel.set_path_effects(label_outline_effect)
    ylabel.set_path_effects(label_outline_effect)

    outline_effect = [path_effects.withStroke(linewidth=1.5, foreground='white')]

    for label in plt.gca().get_xticklabels() + plt.gca().get_yticklabels():
        label.set_color('black')
        label.set_fontweight('bold')
        label.set_path_effects(outline_effect)

    ax = plt.gca()
    for spine in ax.spines.values():
        spine.set_color('white')

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', transparent=True)
    plt.close()
    
    buffer.seek(0)
    return buffer



'''
# SIMULATE STOCKS:

stock = Stock('SHT', 20, 4, 10, 'coin', 'shitcoin #4')

for i in range(2016):
    print(i)
    stock.tick()

    if stock.price < 1:
        break

stock.plot()    
'''


'''
# CREATE STOCKS:
asyncio.run(init_stock('NUNU', 5, 0.5, 0.1, 'stock', 'nuu willum'))
'''


'''
# GEN RANDOM COIN
asyncio.run(gen_coin())
'''