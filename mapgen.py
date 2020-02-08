from colorama import Fore, Back, Style
import sys
from time import sleep
import json

# Pretty Printing for debugging
from pprint import PrettyPrinter
pp = PrettyPrinter().pprint

## GENERATE TEST WORLD #######################################################
'''
import random
size = 13

world_grid = [[None] * size for n in range(size)]
for y in range(size):
    for x in range(size):
        world_grid[y][x] = {
                'title': x,
                'exits': [],
                'items': [],
                'players': [],
                'coordinates': (x, y)
                }
for y in range(size - 1):
    for x in range(size):
        if random.random() < 0.8:
            world_grid[y][x]['exits'].append('s')
for y in range(size):
    for x in range(size - 1):
        if random.random() < 0.8:
            world_grid[y][x]['exits'].append('e')
# example loot room:
x = random.randint(0, size - 1)
y = random.randint(0, size - 1)
world_grid[y][x]['items'] = ['some', 'stuff']
# example other player: (maybe shouldn't bother since players move)
x = random.randint(0, size - 1)
y = random.randint(0, size - 1)
world_grid[y][x]['players'] = ['Bob']
# example special room:
x = random.randint(0, size - 1)
y = random.randint(0, size - 1)
world_grid[y][x]['title'] = 'Shop'

# player object
player = {
    'name': 'Alice',
    'true name': False,
    'x': 2,
    'y': 2
}
'''
player = {'x': 50, 'y': 50}
## LOAD FROM FILE ############################################################

def get_world(mapfile):
    with open(mapfile, 'r') as f:
        world_map = json.load(f)

    world_grid = [[None] * 100 for n in range(100)]

    for room_id, room in world_map.items():
        xstr, ystr = room['coordinates'].strip('()').split(',')
        x = int(xstr)
        y = int(ystr)
        world_grid[y][x] = room

    world_grid.reverse()

    return world_grid


## CREATE DISPLAY REPRESENTATION #############################################
# symbols for grid squares
symbols = {}
# you are here
symbols['player'] = Fore.BLACK + Back.CYAN + ':)'
# maybe true name status should just be represented in another way
symbols['true name'] = Fore.BLACK + Back.MAGENTA + ':D'
# empty room / area
symbols['empty'] = Fore.BLACK + Back.WHITE + '[]'
# void doesn't represent anything in the world, they're just margin space
symbols['void'] = Back.BLACK + '  '
# north-south door
symbols['||'] = Fore.GREEN + Back.WHITE + '||'
# east-west door
symbols['=='] = Fore.GREEN + Back.WHITE + '=='
# room has items in it, higher priority than `has player`
symbols['has item'] = Fore.BLACK + Back.RED + '$!'
# room has players in it (maybe don't bother, players move a lot)
symbols['has player'] = Fore.BLACK + Back.WHITE + ':)'
# special rooms: (names might be wrong)
symbols['Shop'] = Fore.BLACK + Back.GREEN + '$$'
symbols['Shrine'] = Fore.BLACK + Back.YELLOW + 'SH'
symbols['Wishing Well'] = Fore.CYAN + Back.BLUE + '()'

def room_repr(room):
    if room is None:
        return symbols['void']
    elif f"{player['x']},{player['y']})" == room['coordinates']:
        return symbols['player']
    elif room['title'] in symbols:
        return symbols[room['title']]
    elif len(room['items']) > 0:
        return symbols['has item']
    # elif len(room['players']) > 0:
    #     return symbols['has player']
    else:
        return symbols['empty']

def build_visual(world_grid):
    sizex = len(world_grid[0])
    sizey = len(world_grid)

    # initialize grid for display, twice the size in order to show doors
    show_grid = []

    # fill main grid
    for y in range(sizey - 1):
        top_row = []
        bottom_row = []
        for x in range(sizex - 1):
            loc = world_grid[y][x]
            # room square first
            top_row.append(room_repr(loc))
            # void rooms need void doors
            if loc is None:
                top_row.append(symbols['void'])
                bottom_row.append(symbols['void'])
            else: # real room, do real doors
                # east door
                if 'e' in loc['exits']:
                    top_row.append(symbols['=='])
                else:
                    top_row.append(symbols['void'])
                # south door
                if 's' in loc['exits']:
                    bottom_row.append(symbols['||'])
                else:
                    bottom_row.append(symbols['void'])
            # unused void square in corner
            bottom_row.append(symbols['void'])
        show_grid.extend([top_row, bottom_row])

    # the right edge will never have eastern doors
    for y in range(sizey - 1):
        loc = world_grid[y][-1]
        show_grid[y * 2].append(room_repr(loc))

        if loc is not None and 's' in loc['exits']:
            show_grid[y * 2 + 1].append(symbols['||'])
        else:
            show_grid[y * 2 + 1].append(symbols['void'])

    # the bottom edge will never have southern doors
    show_grid.append([])
    for x in range(sizex - 1):
        loc = world_grid[-1][x]
        show_grid[-1].append(room_repr(loc))
        if loc is not None and 'e' in world_grid[-1][x]['exits']:
            show_grid[-1].append(symbols['=='])
        else:
            show_grid[-1].append(symbols['void'])

    # the room in the bottom left corner will never have south or east doors
    show_grid[-1].append(room_repr(world_grid[-1][-1]))

    return show_grid

## MAIN ######################################################################

mapfile = sys.argv[1]
period = sys.argv[2] if len(sys.argv) >= 3 else 30

while True:
    for name, symbol in symbols.items():
        print(symbol + Style.RESET_ALL, name)
    world_grid = get_world(mapfile)
    trimy = world_grid[15:55]
    trimmed = [row[40:80] for row in trimy]
    for row in build_visual(trimmed):
        print(''.join(row) + Style.RESET_ALL)
    sleep(period)
