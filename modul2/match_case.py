month = 6
day = 2

match day:
    case 1 | 3 | 5 | 7 if month == 6:
        print('we are at day odd')
    case 2 | 4 | 6 if month == 5:
        print('we are at day even')
    case _:
        print('all other cases')