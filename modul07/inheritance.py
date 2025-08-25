class Vehicle(object):
    def __init__(self, model, year):
        self.model = model
        self.year = year

    def drive(self):
        print('Driving')

class Car(Vehicle):
    def __init__(self, model, year, hand_break = True):
        super().__init__(model, year)
        self.hand_break = hand_break

    def drive(self):
        print(f'Driving Car with {self.hand_break}')

class Airplane(Vehicle):
    def __init__(self, model, year, max_altitude):
        super().__init__(model, year)
        self.max_altitude = max_altitude

    def drive(self):
        print('Flying')
        # print("Drive care in Airplane", Car.drive(self)) # airplane has no hand break


a = Airplane('Airbus', 2000, 20000)
print(a.model)
a.drive()

delattr(Airplane, 'drive')
print(getattr(a, 'drive'))
# .drive()