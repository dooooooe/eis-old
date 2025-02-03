import json
import os
import pathlib
import aiofiles

# make sure to update if updating fields: 
# user init params
# setdata params


class Inventory:
    def __init__(self, items: dict={}, portfolio: dict={}):
        self.items = items
        self.portfolio = portfolio

    
    def to_dict(self):
        return {key: value for key, value in vars(self).items()}


class User:
    def __init__(self, userid: int=-1, name: str=None, nickname: str=None, money: int=10, ingame: bool=False, gambling: bool=False, game_history: list=['D' for _ in range(50)], last_worked: float=0, last_stolen: float=0):
        self.userid = userid
        self.name = name
        self.nickname = nickname
        self.money = money
        self.ingame = ingame
        self.gambling = gambling
        self.game_history = game_history
        self.last_worked = last_worked
        self.last_stolen = last_stolen
        
        self.inventory = {
            'items': dict(), 
            'portfolio': dict()
                          }


    def to_dict(self):
        return {key: value for key, value in vars(self).items()}


def user_path(userid):
    folder_path = os.path.join(os.path.dirname(__file__), 'userdata')

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    return os.path.join(folder_path, f'{userid}.json')


async def init_user(userid):
    user_file = user_path(userid)

    if not os.path.exists(user_file):
        user = User(userid)

        async with aiofiles.open(user_file, 'w') as f:
            await f.write(json.dumps(user.to_dict(), indent=4))


async def get_data(userid, to_get=None):
    await init_user(userid)
    user_file = user_path(userid)

    async with aiofiles.open(user_file, 'r') as f:
        content = await f.read()
        data = json.loads(content)

    # check if correct fields exist
    u = User()
    default_dict = u.to_dict()
    default_fields = default_dict.keys()
    fields = data.keys()

    if fields != default_fields:
        missing_fields = default_fields - fields
        extraneous_fields = fields - default_fields

        for field in missing_fields:
            data[field] = default_dict[field]
        
        for field in extraneous_fields:
            print(f'user {userid} has extraneous data \'{field}\' with value {data[field]}')
    
    if to_get is None:
        return data

    else:
        return data.get(to_get)


async def set_data(userid, name: str=None, nickname: str=None, money: int=None, ingame: bool=None, gambling: bool=None, game_history: list=None, last_worked: float=None, last_stolen: float=None, inventory: dict=None):
    new_data = {key: value for key, value in locals().items() if key != "userid" and value is not None}

    await init_user(userid)
    user_file = user_path(userid)

    data = await get_data(userid)

    for key, value in new_data.items():
        data[key] = value

    async with aiofiles.open(user_file, 'w') as f:
        await f.write(json.dumps(data, indent=4))


async def adjust_inventory(userid, category, item, amount):
    data = await get_data(userid)
    inventory = data['inventory']

    if not inventory.get(category):
        inventory[category] = {}

    if not inventory[category].get(item):
        inventory[category][item] = 0

    inventory[category][item] += amount

    if inventory[category][item] == 0:
        del inventory[category][item]

    await set_data(userid, inventory=inventory)


async def update_history(userid, history_type, entry):
    data = await get_data(userid)
    history = data[history_type]
    
    if len(history) == 50:
        del history[0]

    history.append(entry)

    data[history_type] == history

    async with aiofiles.open(user_path(userid), 'w') as f:
        await f.write(json.dumps(data, indent=4))


async def get_all_users():
    userids = [int(file.stem) for file in pathlib.Path("./storage/userdata").glob("*.json")]

    return userids 