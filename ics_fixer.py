from regexTest import modifyEvent

original = open("schedule.ics", "r")

collectEvent = False
Events = []
event = []

for line in original:
    if line == "":
        continue
    if "DTSTAMP" in line:
        continue
    if "CREATED" in line:
        continue
    if "LAST-MODIFIED" in line:
        continue
    if "SEQUENCE" in line:
        continue
    if "RRULE" in line:
        continue
    if "EXDATE" in line:
        continue
    if "DESCRIPTION" in line:
        continue

    if "BEGIN:VEVENT" in line:
        collectEvent = True
    if collectEvent == True:
        event.append(line)
    if "END:VEVENT" in line:
        collectEvent = False
        Events.append(event)
        event = []

new_events = []

for event in Events:
    event = modifyEvent(event)
    new_events.append(event)

for i in new_events:
    print(i)


with open('new.ics', 'a') as the_file:
    the_file.write("BEGIN:VCALENDAR\n")
    for event in new_events:
        for line in event:
            the_file.write(line)
    the_file.write("VERSION:2.0\n END:VCALENDAR")
