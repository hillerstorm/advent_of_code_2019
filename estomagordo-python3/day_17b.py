import re

from heapq import heappop, heappush
from collections import Counter, defaultdict
from intcode import Computer


def get_grid(computer):
    grid = []
    row = []

    while True:
        retcode, retval = computer.get_output()

        if retcode == -1:
            break

        if retval == 10:
            grid.append(row)
            row = []

        else:
            row.append(retval)

    if row:
        grid.append(row)
    
    if not grid[-1]:
        grid = grid[:-1]
    
    height = len(grid)
    width = len(grid[0])

    return grid, height, width


def get_start(grid, height, width):
    by, bx = -1, -1    
    direction = -1

    for y in range(height):
        for x in range(width):
            if grid[y][x] in (35, 46):
                continue

            by = y
            bx = x

            botchar = chr(grid[y][x])
            
            if botchar == '^':
                direction = 0
            elif botchar == '>':
                direction = 1
            elif botchar == '<':
                direction = 2
            else:
                direction = 3

            return by, bx, direction


def get_scaffolds(grid, height, width):
    scaffolds = set()

    for y in range(height):
        for x in range(width):
            if grid[y][x] != 46:
                scaffolds.add((y, x))

    return scaffolds


def get_moves(grid, height, width):
    directions = ((-1, 0), (0, 1), (1, 0), (0, -1))
    
    by, bx, direction = get_start(grid, height, width)
    currdir = directions[direction]
    scaffolds = get_scaffolds(grid, height, width)

    seen = { by, bx }
    moves = []

    while len(seen) != len(scaffolds):
        ny, nx = by + currdir[0], bx + currdir[1]
        n2y, n2x = by + 2 * currdir[0], bx + 2 * currdir[1]

        if 0 <= ny < height and 0 <= nx < width and (ny, nx) in scaffolds and ((ny, nx) not in seen or (n2y, n2x) not in seen):
            seen.add((ny, nx))
            moves.append('F')
            by, bx = ny, nx
            continue

        ry, rx = by + directions[(direction + 1) % 4][0], bx + directions[(direction + 1) % 4][1]
        ly, lx = by + directions[(direction - 1) % 4][0], bx + directions[(direction - 1) % 4][1]

        right_good = 0 <= ry < height and 0 <= rx < width and (ry, rx) in scaffolds and (ry, rx) not in seen
        left_good = 0 <= ly < height and 0 <= lx < width and (ly, lx) in scaffolds and (ly, lx) not in seen

        if right_good:
            moves.append('R')
            direction = (direction + 1) % 4
            currdir = directions[direction]
            continue
        if left_good:
            moves.append('L')
            direction = (direction - 1) % 4
            currdir = directions[direction]
            continue
    moves += 'F' #Fugly hack.
    return moves


def infuse_numbers(moves):
    new = []
    currlen = 0

    for c in moves:
        if c in 'RL':
            if currlen > 0:
                lens = str(currlen)
                for cc in list(lens):
                    new.append(cc)
                new.append(',')
                currlen = 0
            new.append(c)
            new.append(',')
        else:
            currlen += 1

    if currlen > 0:
        lens = str(currlen)
        for cc in list(lens):
            new.append(cc)

    if new[-1] == ',':
        new = new[:-1]
   
    return ''.join(new)


def programify(infused):
    for alen in range(5, 21):
        a = infused[:alen]

        atimes = infused.count(a)

        if atimes < 2:
            continue

        infprime = str(infused)

        while a in infprime:
            infprime = infprime.replace(a, 'A,')

        if infprime[-1] == ',':
            infprime = infprime[:-1]

        bstart = 0
        while infprime[bstart] not in 'FLR':
            bstart += 1

        for blen in range(5, 21):
            b = infprime[bstart:bstart + blen]

            btimes = infprime.count(b)

            if btimes < 2:
                continue

            infbis = str(infprime)

            while b in infbis:
                infbis = infbis.replace(b, 'B,')

            if infbis[-1] == ',':
                infbis = infbis[:-1]

            cstart = 0
            while infbis[cstart] not in 'FLR':
                cstart += 1

            clen = 5

            while cstart + clen < len(infbis) - 1 and infbis[cstart + clen + 1] not in 'AB':
                clen += 1

            c = infbis[cstart:cstart + clen]

            inftris = str(infbis)

            while c in inftris:
                inftris = inftris.replace(c, 'C,')

            if all(char in  'ABC,' for char in inftris):
                if inftris[-1] == ',':
                    inftris = inftris[:-1]
                return inftris.replace(',,', ','), a, b, c


def solve(d):
    exploreputer = Computer(d, 1)

    grid, height, width = get_grid(exploreputer)
    moves = get_moves(grid, height, width)

    movement, funca, funcb, funcc = programify(infuse_numbers(moves))

    inputs = []

    for c in movement:
        inputs.append(ord(c))

    inputs.append(10)

    for c in funca:
        inputs.append(ord(c))

    inputs.append(10)

    for c in funcb:
        inputs.append(ord(c))

    inputs.append(10)

    for c in funcc:
        inputs.append(ord(c))

    inputs.append(10)

    inputs.append(ord('n'))
    inputs.append(10)

    moveputer = Computer(d, inputs[0], 2)
    inppos = 1
    retcode, retval = 0, 0
    dust = 0

    while retcode != -1:
        retcode, retval = moveputer.step()

        if retcode == 0 and retval == 3:
            if inppos < len(inputs):
                moveputer.set_input(inputs[inppos])
            inppos += 1

        if retcode == 1:
            dust = retval

    return dust
    

def read_and_solve():
    with open('input_17.txt') as f:
        data = list(map(int, f.readline().split(',')))
        return solve(data)

if __name__ == '__main__':
    print(read_and_solve())