import string


def find_2nd(string, substring):
    return string.find(substring, string.find(substring) + 1)


def modifyEvent(event: list) -> list:

    # If SUMMARY break into 2 lines
    if len(event) == 8:
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
        original = open("schedule.ics", "r")
    except:
        print("--- ics file path invalid ---")
        return

    # collect events from original ics file
    collectEvent = False
    # a large list of events
    Events = []
    # a list to store one event as lines of strings
    event = []
    # traverse original ics file line by line
    for line in original:
        # skip useless lines
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

        # collecting useful lines for one event
        if "BEGIN:VEVENT" in line:
            collectEvent = True
        if collectEvent == True:
            event.append(line)
        if "END:VEVENT" in line:
            collectEvent = False
            Events.append(event)
            event = []

    # New big list of events
    new_events = []

    # traverse all events
    for event in Events:
        # clean up event
        event = modifyEvent(event)
        # append to new big list
        new_events.append(event)

    # print to verify
    for i in new_events:
        print(i)

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


if __name__ == "__main__":
    main()
