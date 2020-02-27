from ics import Calendar, Event

c = Calendar()


# e.name = "Digital World"
# e.begin = '2020-02-01 00:00:00'
# e.end = '2020-02-01 02:00:00'
# e.description = 'Oka'
# e.location = 'Singapore University of Technology and Design'`


def addEvent(name, time, description, location):
    e = Event()
    e.name = name
    e.begin = time[0]
    e.end = time[1]
    e.description = description
    e.location = location
    c.events.add(e)


addEvent(
    "Event 1",
    ("2020-02-01 00:00:00", "2020-02-01 02:00:00"),
    "description test 1",
    "LT1",
)
addEvent(
    "Event 2",
    ("2020-02-01 04:00:00", "2020-02-01 05:00:00"),
    "description test 2",
    "LT2",
)


with open("my.ics", "w") as my_file:
    my_file.writelines(c)
