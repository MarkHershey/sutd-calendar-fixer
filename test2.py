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


print(Events)
