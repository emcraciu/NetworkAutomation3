class CarIterator():
    def __init__(self, model, year, whiles):
        self.model = model
        self.year = year
        self.whiles = whiles

    def __iter__(self):
        return self
    def __next__(self):
        if self.whiles:
            value = self.whiles
            self.whiles -= 1
        else:
            raise StopIteration
        return value

class Car():
    def __init__(self, model: str, year: int, whiles: int):
        self.model = model
        self.year = year
        self.whiles = whiles

    def __iter__(self):
        return CarIterator(model=self.model, year=self.year, whiles=self.whiles)


car = Car('Mercede', 2019, 4)

for c in car:
    print(c)


# steps for the for loop
car_iter = car.__iter__()
print(next(car_iter))
print(next(car_iter))
print(next(car_iter))
print(next(car_iter))
# print(next(car_iter))