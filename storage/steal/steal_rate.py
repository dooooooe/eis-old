with open('steal_log.txt', 'r') as f:
    results = f.read()

total = len(results)
wins = 0

for result in results:
    wins += int(result)

wl = round(wins/total * 100, 2)

print(f'Success rate for steals is {wins}/{total} ({wl}%)')