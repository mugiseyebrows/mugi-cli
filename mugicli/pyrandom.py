import argparse
import random

STAT = {"first": {"a": 1193, "b": 584, "c": 1346, "d": 855, "e": 887, "f": 635, "g": 396, "h": 394, "i": 823, "j": 211, "k":
171, "l": 462, "m": 780, "n": 484, "o": 441, "p": 1118, "q": 143, "r": 797, "s": 1420, "t": 872, "u": 332, "v": 371,
"w": 403, "x": 79, "y": 125, "z": 83}, "next": {"a": {"a": 77, "b": 259, "c": 442, "d": 272, "e": 56, "f": 51, "g": 245,
"h": 28, "i": 251, "j": 18, "k": 97, "l": 988, "m": 254, "n": 918, "o": 38, "p": 250, "q": 13, "r": 860, "s": 368, "t":
1314, "u": 90, "v": 139, "w": 50, "x": 61, "y": 126, "z": 42}, "b": {"a": 138, "b": 24, "c": 15, "d": 7, "e": 220, "f":
2, "g": 2, "h": 3, "i": 153, "j": 12, "k": 3, "l": 247, "m": 5, "n": 5, "o": 177, "p": 8, "q": 0, "r": 136, "s": 82,
"t": 29, "u": 90, "v": 9, "w": 6, "x": 4, "y": 25, "z": 7}, "c": {"a": 507, "b": 3, "c": 92, "d": 12, "e": 540, "f": 8,
"g": 2, "h": 342, "i": 354, "j": 1, "k": 148, "l": 176, "m": 10, "n": 10, "o": 803, "p": 5, "q": 7, "r": 207, "s": 57,
"t": 576, "u": 194, "v": 4, "w": 2, "x": 7, "y": 83, "z": 12}, "d": {"a": 144, "b": 11, "c": 14, "d": 41, "e": 683, "f":
6, "g": 24, "h": 8, "i": 608, "j": 14, "k": 1, "l": 47, "m": 17, "n": 22, "o": 113, "p": 14, "q": 4, "r": 98, "s": 140,
"t": 23, "u": 145, "v": 32, "w": 12, "x": 13, "y": 54, "z": 4}, "e": {"a": 505, "b": 46, "c": 541, "d": 1135, "e": 252,
"f": 146, "g": 155, "h": 31, "i": 129, "j": 23, "k": 19, "l": 574, "m": 272, "n": 1145, "o": 129, "p": 186, "q": 80,
"r": 1606, "s": 1331, "t": 503, "u": 54, "v": 161, "w": 61, "x": 244, "y": 91, "z": 28}, "f": {"a": 143, "b": 1, "c": 7,
"d": 6, "e": 178, "f": 98, "g": 3, "h": 7, "i": 282, "j": 3, "k": 1, "l": 106, "m": 3, "n": 8, "o": 200, "p": 8, "q": 2,
"r": 106, "s": 8, "t": 50, "u": 81, "v": 6, "w": 4, "x": 2, "y": 40, "z": 5}, "g": {"a": 154, "b": 4, "c": 9, "d": 8,
"e": 353, "f": 3, "g": 47, "h": 129, "i": 163, "j": 3, "k": 4, "l": 94, "m": 26, "n": 114, "o": 79, "p": 4, "q": 3, "r":
169, "s": 72, "t": 22, "u": 84, "v": 9, "w": 2, "x": 2, "y": 32, "z": 6}, "h": {"a": 326, "b": 9, "c": 5, "d": 9, "e":
439, "f": 3, "g": 8, "h": 9, "i": 215, "j": 2, "k": 7, "l": 19, "m": 21, "n": 17, "o": 255, "p": 4, "q": 2, "r": 54,
"s": 34, "t": 92, "u": 50, "v": 2, "w": 9, "x": 1, "y": 60, "z": 7}, "i": {"a": 316, "b": 140, "c": 733, "d": 260, "e":
376, "f": 202, "g": 230, "h": 29, "i": 35, "j": 13, "k": 46, "l": 374, "m": 307, "n": 2113, "o": 834, "p": 144, "q": 18,
"r": 231, "s": 626, "t": 645, "u": 60, "v": 259, "w": 24, "x": 40, "y": 9, "z": 167}, "j": {"a": 53, "b": 7, "c": 3,
"d": 4, "e": 77, "f": 1, "g": 2, "h": 2, "i": 26, "j": 4, "k": 3, "l": 1, "m": 3, "n": 2, "o": 61, "p": 3, "q": 1, "r":
3, "s": 3, "t": 9, "u": 51, "v": 2, "w": 2, "x": 1, "y": 4, "z": 1}, "k": {"a": 36, "b": 9, "c": 6, "d": 3, "e": 200,
"f": 2, "g": 4, "h": 9, "i": 85, "j": 2, "k": 6, "l": 26, "m": 1, "n": 26, "o": 17, "p": 5, "q": 0, "r": 15, "s": 63,
"t": 31, "u": 4, "v": 3, "w": 7, "x": 2, "y": 23, "z": 6}, "l": {"a": 588, "b": 11, "c": 28, "d": 81, "e": 879, "f": 17,
"g": 13, "h": 9, "i": 653, "j": 2, "k": 23, "l": 523, "m": 21, "n": 9, "o": 412, "p": 18, "q": 1, "r": 12, "s": 130,
"t": 132, "u": 169, "v": 47, "w": 12, "x": 5, "y": 554, "z": 4}, "m": {"a": 476, "b": 96, "c": 13, "d": 5, "e": 541,
"f": 10, "g": 16, "h": 3, "i": 404, "j": 0, "k": 2, "l": 19, "m": 103, "n": 21, "o": 241, "p": 312, "q": 1, "r": 15,
"s": 70, "t": 17, "u": 97, "v": 9, "w": 16, "x": 6, "y": 39, "z": 6}, "n": {"a": 435, "b": 14, "c": 402, "d": 483, "e":
691, "f": 75, "g": 1137, "h": 25, "i": 379, "j": 18, "k": 53, "l": 44, "m": 22, "n": 99, "o": 255, "p": 22, "q": 5, "r":
21, "s": 653, "t": 940, "u": 111, "v": 72, "w": 21, "x": 4, "y": 44, "z": 14}, "o": {"a": 95, "b": 102, "c": 177, "d":
165, "e": 91, "f": 63, "g": 126, "h": 26, "i": 119, "j": 12, "k": 56, "l": 372, "m": 369, "n": 1506, "o": 159, "p": 225,
"q": 6, "r": 749, "s": 329, "t": 300, "u": 391, "v": 125, "w": 166, "x": 50, "y": 40, "z": 16}, "p": {"a": 301, "b": 5,
"c": 8, "d": 9, "e": 507, "f": 10, "g": 7, "h": 169, "i": 201, "j": 1, "k": 3, "l": 292, "m": 10, "n": 9, "o": 368, "p":
159, "q": 5, "r": 405, "s": 92, "t": 117, "u": 104, "v": 9, "w": 6, "x": 6, "y": 29, "z": 6}, "q": {"a": 8, "b": 3, "c":
3, "d": 2, "e": 10, "f": 0, "g": 3, "h": 1, "i": 9, "j": 2, "k": 2, "l": 4, "m": 1, "n": 5, "o": 3, "p": 3, "q": 1, "r":
8, "s": 6, "t": 2, "u": 188, "v": 7, "w": 5, "x": 4, "y": 5, "z": 2}, "r": {"a": 906, "b": 49, "c": 115, "d": 145, "e":
1361, "f": 45, "g": 87, "h": 17, "i": 797, "j": 6, "k": 59, "l": 56, "m": 200, "n": 117, "o": 655, "p": 66, "q": 7, "r":
208, "s": 316, "t": 300, "u": 111, "v": 78, "w": 17, "x": 11, "y": 203, "z": 23}, "s": {"a": 165, "b": 18, "c": 199,
"d": 11, "e": 641, "f": 27, "g": 5, "h": 223, "i": 599, "j": 2, "k": 32, "l": 98, "m": 72, "n": 34, "o": 224, "p": 204,
"q": 14, "r": 21, "s": 348, "t": 883, "u": 283, "v": 8, "w": 46, "x": 4, "y": 78, "z": 7}, "t": {"a": 621, "b": 9, "c":
50, "d": 9, "e": 1382, "f": 19, "g": 4, "h": 382, "i": 1564, "j": 1, "k": 12, "l": 127, "m": 28, "n": 37, "o": 399, "p":
11, "q": 2, "r": 646, "s": 329, "t": 202, "u": 223, "v": 7, "w": 29, "x": 7, "y": 207, "z": 14}, "u": {"a": 158, "b":
89, "c": 186, "d": 78, "e": 118, "f": 20, "g": 74, "h": 3, "i": 129, "j": 6, "k": 4, "l": 298, "m": 244, "n": 366, "o":
27, "p": 121, "q": 3, "r": 323, "s": 344, "t": 206, "u": 5, "v": 9, "w": 4, "x": 12, "y": 16, "z": 13}, "v": {"a": 202,
"b": 6, "c": 4, "d": 7, "e": 575, "f": 2, "g": 5, "h": 5, "i": 258, "j": 4, "k": 2, "l": 5, "m": 2, "n": 3, "o": 91,
"p": 8, "q": 1, "r": 6, "s": 5, "t": 13, "u": 10, "v": 12, "w": 7, "x": 23, "y": 14, "z": 7}, "w": {"a": 157, "b": 4,
"c": 2, "d": 5, "e": 126, "f": 4, "g": 3, "h": 57, "i": 146, "j": 1, "k": 3, "l": 17, "m": 6, "n": 34, "o": 98, "p": 8,
"q": 1, "r": 32, "s": 37, "t": 25, "u": 3, "v": 5, "w": 5, "x": 7, "y": 11, "z": 1}, "x": {"a": 36, "b": 8, "c": 48,
"d": 2, "e": 53, "f": 4, "g": 3, "h": 6, "i": 69, "j": 4, "k": 5, "l": 5, "m": 1, "n": 4, "o": 18, "p": 84, "q": 2, "r":
4, "s": 4, "t": 51, "u": 4, "v": 10, "w": 3, "x": 31, "y": 15, "z": 5}, "y": {"a": 35, "b": 15, "c": 43, "d": 16, "e":
73, "f": 7, "g": 10, "h": 3, "i": 58, "j": 5, "k": 4, "l": 39, "m": 35, "n": 50, "o": 51, "p": 31, "q": 1, "r": 47, "s":
104, "t": 29, "u": 7, "v": 8, "w": 10, "x": 11, "y": 54, "z": 33}, "z": {"a": 59, "b": 4, "c": 1, "d": 2, "e": 142, "f":
1, "g": 4, "h": 2, "i": 44, "j": 3, "k": 4, "l": 9, "m": 5, "n": 4, "o": 21, "p": 3, "q": 2, "r": 6, "s": 6, "t": 3,
"u": 1, "v": 3, "w": 1, "x": 3, "y": 32, "z": 40}}, "last": {"a": 527, "b": 121, "c": 330, "d": 1340, "e": 2004, "f":
103, "g": 1020, "h": 263, "i": 320, "j": 44, "k": 179, "l": 669, "m": 280, "n": 1123, "o": 334, "p": 186, "q": 38, "r":
830, "s": 2732, "t": 1065, "u": 86, "v": 129, "w": 132, "x": 161, "y": 1234, "z": 154}}

FIRST = STAT['first']
NEXT = STAT['next']
LAST = STAT['last']

def rand_first(stat):
    r = random.randint(0, sum(stat.values())-1)
    x = 0
    for k, v in stat.items():
        x += v
        if x >= r:
            return k

def rand_next(next, last):
    r = random.randint(0, sum(next.values()) + last - 1)
    x = 0
    for k, v in next.items():
        x += v
        if x >= r:
            return k

def rand_word():
    f = rand_first(FIRST)
    res = [f]
    while True:
        c = rand_next(NEXT[res[-1]], LAST[res[-1]])
        if c is None:
            return "".join(res)
        res.append(c)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-w", "--words", action='store_true')
    parser.add_argument("-l", "--length", nargs=2, type=int)
    parser.add_argument("-n", "--number", type = int, default=1)
    parser.add_argument("-s", "--space", action='store_true')

    args = parser.parse_args()
    #print(args); exit(0)

    if args.words:
        if args.length:
            lmin, lmax = args.length
            if lmax < lmin:
                raise ValueError("--length min max")
            if lmax < 1:
                raise ValueError("lmax < 1")
            pred = lambda s: lmin <= len(s) <= lmax
        else:
            pred = lambda s: True
        
        number = args.number
        sep = " " if args.space else "\n"
        while number > 0:
            w = rand_word()
            if pred(w):
                number -= 1
                print(w, end=sep)
        if args.space:
            print()

if __name__ == "__main__":
    main()