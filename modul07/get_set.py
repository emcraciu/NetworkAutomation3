class Triangle(object):
    def __init__(self, a: int, b: int, c: int):
        self.a = a
        self.b = b
        self.c = c

    def __setattr__(self, key, value):
        # x = getattr(self, key, None)
        super().__setattr__(key, value + 1) # change assigned value
        # print(dir(self))
        # print(key)

    def __delattr__(self, key):
            super().__delattr__(key)

    def __getattribute__(self, key):
        return super().__getattribute__(key)


t = Triangle(1, 1, 1)

change = input('Provide len for new side ex: (a: 2)').strip('( )').strip(':')
key, value  = list(map(lambda _: int(_.strip()) if _.strip().isdigit() else _.strip(),  change.split(':')))
print(type(key), type(value))

# if key == 'a':
#     t.a = 2

t.__setattr__('example', 'value')

setattr(t, key, value)
# t.__setattr__(key, value)
print(getattr(t, key))
# print(t.__getattribute__(key))

print(t.a)
delattr(t, key)
# t.__delattr__(key)
print(t.a)
