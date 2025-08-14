dict(key=1) # calls constructor of class dict

class SomeObject:
    pass

def some_function(self):
    print('some_function', id(self))

class Car(object):
    class_var = "generic_car"

    def __init__(self, color, speed):
        print('car id is:', id(self))
        self.color = color
        self.speed = speed

    def drive(some_object):
        print('ID in drive of object', id(some_object))
        print('driving car at speed', some_object.speed)


car = Car('blue', 200)
print(id(car))

print(car.color)
print(car.speed)
print(car.class_var)
print(Car.class_var)
print(Car.drive)
# object_with_speed = 'test'
# object_with_speed.speed = 200 # cannot be changed for built ins
so = SomeObject()
so.speed = 50
so.x = some_function
so.x(so)

print("Some object id: ", id(so))
Car.drive(so)

print('Car id:', id(car))
print(car.drive)
car.drive()




# print(id(Car.class_var))
# print(id(car.class_var))