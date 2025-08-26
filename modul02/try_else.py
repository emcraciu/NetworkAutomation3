try:
    print('running')
    raise KeyboardInterrupt
    # while True:
    #     print('do something')
    # print(1/0)
    # assert False, "This is an assertion message" # this will rase AssertionError for falsish objects
    x + y
except (ZeroDivisionError, AssertionError) as e:
    print('something went wrong', f'"{e}"')
except Exception as e:
    print(e)
# except BaseException:
#     print('This is worst case')
#     raise
else:
    print('all is good')
finally:
    print('This will always be printed')