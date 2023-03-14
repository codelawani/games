from termcolor import colored, cprint
""" def dice(chance):
    print("".center(9, "_"))

    print("|", end="")
    if chance == 4 or chance == 6 or chance == 5:
        print("*   *".center(7), end="")
    elif chance == 2:
        print("*".center(7), end="")
    elif chance == 3:
        print("*".rjust(7), end="")
    elif chance == 1:
        print("".rjust(7), end="")
    print("|")

    print("|", end="")
    if chance == 4 or chance == 6:
        print("*   *".center(7), end="")
    elif chance == 3 or chance == 5:
        print("*".center(7), end="")
    elif chance == 2 or chance == 1:
        print("*".center(7), end="")
    print("|")

    if chance != 4 and chance != 2:
        print("|", end="")
        if chance == 5 or chance == 6:
            print("*   *".center(7), end="")
        elif chance == 1:
            print("".center(7), end="")
        elif chance == 3:
            print("*".ljust(7), end="")
        print("|")

    print("".center(9, "-"), "\n") """


def dice(chance):
    dots = {1: ["     ", "  *  ", "     "],
            2: ["*    ", "     ", "    *"],
            3: ["*    ", "  *  ", "    *"],
            4: ["*   *", "     ", "*   *"],
            5: ["*   *", "  *  ", "*   *"],
            6: ["*   *", "*   *", "*   *"]}

    print("".center(9, "_"))
    for i in range(3):
        print("|", end="")
        cprint(dots[chance][i].center(7), "yellow", attrs=["bold"], end="")
        print("|")
    print("".center(9, "-"), "\n")


""" print(tc.colored(dots[chance][i].center(7), "yellow",
                 None, attrs=["bold"]), end="")
print(dots[chance][i].center(7), end="") """
dice(1)
# players:{'nico': ['*', 1], 'dav': ['#', 1]}
# beed_place:{1: ['*', '#']}
