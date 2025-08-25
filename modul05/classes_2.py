import random


class Car(object):
    class_var = "generic_car"
    color = "red"

    def __init__(self,  speed):
        print('car id is:', id(self))
        self.speed = speed

    def drive(some_object):
        print('ID in drive of object', id(some_object))
        print('driving car at speed', some_object.speed)

    def paint_car(self, color):
        print('painting car', color)
        self.color = color

    @staticmethod
    def print_something():
        print(f'something random: {random.randint(0, 100)}')

    @classmethod
    def get_default_car_color(cls):
        return cls.color

    def __str__(self):
        return f'{self.__class__.__name__} with speed {self.speed} and color {self.color}'

    def __repr__(self):
        return f'{self.__class__.__name__}-{self.speed}-{self.color}'






car = Car(200)
car.print_something()
print(car.color)
car.paint_car('blue')
print('Default color:', car.get_default_car_color())
print(car.__class__)
print(car)

var1 = str(car)
print(var1)
# var1 = "test"
# print(var1)

car1 = Car(201)
car2 = Car(202)
car3 = Car(203)

garage = [str(car1), car2, car3]
print(garage)



