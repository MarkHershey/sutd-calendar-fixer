import string
from pathlib import Path
from typing import List, Dict, Tuple
from markkk.logger import logger

requiredLines = (
    "BEGIN:VEVENT",
    "SUMMARY:",
    "DTSTART:",
    "DTEND:",
    "UID:",
    "END:VEVENT",
)


def find_2nd(string: str, substring: str):
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


def fix(file: str) -> Tuple[str, int]:

    # open ics file in read mode
    file = Path(file)
    if not file.is_file():
        logger.error(f"Invalid file path: '{file}'")
        raise Exception(f"Invalid file path: '{file}'")
    else:
        file = file.resolve()

    if str(file)[-4:] != ".ics":
        logger.error(f"'{file}' is not an '.ics' file")
        raise Exception(f"'{file}' is not an '.ics' file")

    with file.open() as f:
        original = f.readlines()

    # a large list of events
    Events = []
    # a list to store one event as lines of strings
    event = []

    key_index = 0
    # traverse original ics file line by line
    for line in original:
        # collecting useful lines for one event
        if requiredLines[key_index] in line:
            event.append(line)
            if key_index <= len(requiredLines) - 2:
                key_index += 1
            elif key_index == len(requiredLines) - 1:
                Events.append(event)
                event = []
                # reset key_index
                key_index = 0
            else:
                pass
        elif requiredLines[key_index] not in line and key_index == 2:
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

    # # print to verify
    # for index, event in enumerate(new_events):
    #     print(f"{index+1}: {event}")
    # print()
    # print(f"Total {len(new_events)} events")
    # print()

    # create the final long string for ics
    newContent = "BEGIN:VCALENDAR\n"
    for event in new_events:
        for line in event:
            newContent += line
    newContent += "VERSION:2.0\nEND:VCALENDAR"

    # create a new ics file
    folder: Path = file.parent
    export_fp: Path = folder / (file.stem + "_new.ics")
    with export_fp.open(mode="w") as f:
        f.write(newContent)

    logger.debug(f"Successfully exported: {export_fp}")

    return export_fp, len(new_events)
