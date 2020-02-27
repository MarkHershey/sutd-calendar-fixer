import string

path = "REPLACE_ME"

requiredLines = ("BEGIN:VEVENT", "SUMMARY:", "DTSTART:", "DTEND:", "UID:", "END:VEVENT")


def find_2nd(string, substring):
    return string.find(substring, string.find(substring) + 1)


def modifyEvent(event: list) -> list:

    # If SUMMARY break into 2 lines
    if len(event) == len(requiredLines) + 1:
        # remove \n for SUMMARY
        event[1] = event[1][0:-1]
        # join the second line into SUMMARY
        event[1] += event[2].strip()
        # delete second line
        del event[2]

    # find location information at original SUMMARY line
    location_start = event[1].find("ROOM:")

    # if location info is not found in SUMMARY
    if location_start == -1:
        # do nothing
        pass
    # location info is found
    else:
        # offset start point from before 'ROOM:' to after
        location_start += 6
        # create LOCATION line
        location = "LOCATION:" + event[1][location_start:] + "\n"
        # insert LOCATION line into the event
        event.insert(2, location)

    # determine the string slicing end point at SUMMARY line
    summary_end = find_2nd(event[1], ":") - 3
    # only if the slicing point is found
    if summary_end != -4:
        # slice the SUMMARY line to keep module name only
        event[1] = event[1][0:summary_end] + "\n"

    # return formatted event
    return event


def main():

    # open ics file in read mode
    try:
        original = open(path, "r")
    except:
        print("--- ics file path invalid ---")
        return

    # a large list of events
    Events = []
    # a list to store one event as lines of strings
    event = []

    n = 0
    # traverse original ics file line by line
    for line in original:

        # collecting useful lines for one event
        if requiredLines[n] in line:
            event.append(line)
            if n <= len(requiredLines) - 2:
                n += 1
            elif n == len(requiredLines) - 1:
                Events.append(event)
                event = []
                n = 0
            else:
                pass
        elif requiredLines[n] not in line and n == 2:
            event.append(line)
        else:
            pass

    # New big list of events
    new_events = []

    # traverse all events
    for event in Events:
        # clean up event
        event = modifyEvent(event)
        # append to new big list
        new_events.append(event)

    # print to verify
    for index, event in enumerate(new_events):
        print(f"{index+1}: {event}")
    print()
    print(f"Total {len(new_events)} events")
    print()

    # create long string for ics
    newContent = "BEGIN:VCALENDAR\n"
    for event in new_events:
        for line in event:
            newContent += line
    newContent += "VERSION:2.0\nEND:VCALENDAR"

    # create a new ics file
    with open("new.ics", "w") as the_file:
        # write title
        the_file.write(newContent)

    return len(new_events)


if __name__ == "__main__":
    main()
