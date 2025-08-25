# iterator

# Elvis
class DayIterator:
    def __init__(self, month_name, nr_days):
        self.month_name = month_name
        self.nr_days = nr_days
        self.current_day = 1

    def __iter__(self):
        return self

    def __next__(self):
        if self.current_day <= self.nr_days:
            value = f"{self.month_name} {self.current_day}"
            self.current_day += 1
            return value
        else:
            raise StopIteration


class Month:
    def __init__(self, name: str, days: int):
        self.name = name
        self.days = days

    def __iter__(self):
        return DayIterator(month_name=self.name, nr_days=self.days)

# Razvan

class EpisodeIterator():
    def __init__(self, show_name, total_episodes):
        self.show_name = show_name
        self.current_episode = 1
        self.total_episodes = total_episodes

    def __iter__(self):
        return self

    def __next__(self):
        if self.current_episode <= self.total_episodes:
            episode = f"{self.show_name} - episode {self.current_episode}"
            self.current_episode += 1
            return episode
        else:
            raise StopIteration
        return value

class Serial():
    def __init__(self, name: str, total_episodes: int):
        self.name = name
        self.total_episodes = total_episodes

    def __iter__(self):
        return EpisodeIterator(self.name, self.total_episodes)


serial = Serial("Dexter", 6)

for ep in serial:
    print(ep)


# Bogdan Rad
class BuildingIterator:
    def __init__(self, year, rooms, owners):
        self.year = year
        self.rooms = rooms
        self.owners = owners
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.index < len(self.owners):
            value = self.owners[self.index]
            self.index += 1
            return value
        else:
            raise StopIteration



class Building:
    def __init__(self, year: int, rooms: int, owners: list):
        self.year = year
        self.rooms = rooms
        self.owners = owners

    def __iter__(self):
        return BuildingIterator(year = self.year, rooms = self.rooms, owners = self.owners)

building = Building(1999, 14, ["A","B","C","D","E","F","G"])

for c in building:
    print(c)

#Ionela
class BookIterator:
    def __init__(self, pages):
        self.pages = pages
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.index < len(self.pages):
            value = self.pages[self.index]
            self.index += 1
            return value
        else:
            raise StopIteration


class Book:
    def __init__(self, title, pages):
        self.title = title
        self.pages = pages

    def __iter__(self):
        return BookIterator(self.pages)


book = Book("About flowers", ["Page 1", "Page 2", "Page 3"])
for page in book:
    print(page)

book_iter = book.__iter__()
print(next(book_iter))
print(next(book_iter))
print(next(book_iter))
print(next(book_iter))
print(next(book_iter))

# Beni
class MonthIterator():
    def __init__(self, months: list, index=0):
        self.months = months
        self.index = index

    def __iter__(self):
        return self

    def __next__(self):
        if self.index >= len(self.months):
            raise StopIteration

        current_month = self.months[self.index]
        self.index += 1

        return current_month


class Months():
    def __init__(self, months: list, index=0):
        self.months = months
        self.index = index

    def __iter__(self):
        return MonthIterator(self.months, self.index)


months_list = Months(["January", "February", "March", "April"], 0)

for month in months_list:
    print(month)


