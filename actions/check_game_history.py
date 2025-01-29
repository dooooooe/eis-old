from storage import userdata

async def run(ctgame, id):
    name = ctgame.guild.get_member(id).name

    data = await userdata.get_data(id)
    games = data['game_history']

    games_str = ''
    wins = 0
    losses = 0

    for game in games:
        if game == 'W':
            wins += 1
            games_str += ':green_square:'

        elif game == 'L':
            losses += 1
            games_str += ':red_square:'

        else: 
            games_str += ':black_large_square:'

    played = wins + losses

    if played == 0:
        await ctgame.reply(f'{name} has not played any games! \n{games_str}')
    else:
        winrate = round(wins/played * 100, 1)
        await ctgame.reply(f'{name} has a {winrate}% winrate: \n{games_str}')