from collections import OrderedDict
from pathlib import Path
from typing import Dict, List

from markkk.logger import logger


def fix_broken_lines(event_lines_list: List):
    keywords = (
        "BEGIN",
        "DESCRIPTION",
        "SUMMARY",
        "DTSTART",
        "DTEND",
        "DTSTAMP",
        "UID",
        "CREATED",
        "LAST-MODIFIED",
        "SEQUENCE",
        "STATUS",
        "RRULE",
        "EXDATE",
        "END",
    )
    fixed = []
    for line in event_lines_list:
        line = line.strip()
        colon_index = line.find(":")
        if colon_index != -1:
            key = line[:colon_index]
            if key in keywords:
                fixed.append(line)
            else:
                fixed[-1] = fixed[-1] + line
        else:
            fixed[-1] = fixed[-1] + line
    return fixed


def get_event_list(ics_path: str) -> List[List[str]]:
    ics_path = Path(ics_path)
    if not ics_path.is_file():
        logger.error("File does not exist.")

    with ics_path.open() as f:
        lines = f.readlines()

    reading_event: bool = False

    event_list: List[List[str]] = []
    current_event_lines: List[str] = []

    for line in lines:
        line: str = line.strip()

        if line.startswith("BEGIN:VEVENT"):
            reading_event = True

        if reading_event:
            current_event_lines.append(line)

        if line.startswith("END:VEVENT"):
            reading_event = False
            event_list.append(fix_broken_lines(current_event_lines))
            # reset
            current_event_lines = []

    return event_list


def parse_single_event(event_lines: List[str]) -> Dict[str, str]:
    if event_lines[0] == "BEGIN:VEVENT" and event_lines[-1] == "END:VEVENT":
        event_lines = event_lines[1:-1]
    else:
        logger.error("Invalid Event")
        return

    event = OrderedDict(
        {
            "SUMMARY": None,  # Title
            "DESCRIPTION": None,  # Description
            "LOCATION": None,  # Location
            "DTSTART": None,  # Date Start
            "DTEND": None,  # Date End
            "UID": None,  # Unique Identifier
            "RRULE": None,  # Recurring Rule
            "EXDATE": None,  # Exception Date
        }
    )

    for line in event_lines:
        """Each line looks like 'KEY:LINE_VALUE'"""

        # find the index of the colon separating KEY and LINE_VALUE
        colon_index = line.find(":")

        # Get KEY literal
        key = line[:colon_index]

        if key not in event:
            # skip unnecessary keys
            continue

        # Get LINE_VALUE literal
        line_value = line[colon_index + 1 :]

        # recurring rule fix
        if key == "RRULE":
            # Ref: https://www.kanzaki.com/docs/ical/recur.html
            # TODO: convert UNTIL field to GMT (add Z at the back as well)
            # TODO: recurring rule validation
            event[key] = line_value

        else:
            event[key] = line_value

    # 'Summary' fix
    original_summary = event.get("SUMMARY")
    logger.info(original_summary)
    if original_summary:
        room_index = original_summary.find("ROOM:")
        if room_index != -1:
            location_value = original_summary[room_index + 5 :]
            event["LOCATION"] = location_value.strip()
            original_summary = original_summary[:room_index]

        chop_index = original_summary.find(":")
        if chop_index != -1:
            chopped = original_summary[: chop_index - 2]
            event["SUMMARY"] = chopped.strip()

    if event.get("SUMMARY") == event.get("DESCRIPTION"):
        event.pop("DESCRIPTION")

    # get keys with 'None' value
    unused_keys = [key for key in event.keys() if not event.get(key)]
    # remove unused keys
    for key in unused_keys:
        event.pop(key)

    return event


def parse_event_list(event_list: List[List[str]]) -> List[dict]:
    parsed_event_list = []
    for event in event_list:
        parsed_event = parse_single_event(event)
        parsed_event_list.append(parsed_event)
    return parsed_event_list


def generate_new_content_to_write(parsed_event_list: List[dict]) -> str:
    lines_to_write: List[str] = []
    for event in parsed_event_list:
        start = "BEGIN:VEVENT"
        lines_to_write.append(start)
        for key, value in event.items():
            if key in ("DTSTART", "DTEND", "EXDATE"):
                # Timezone fix: enforce Asia/Singapore
                line = f"{key};TZID=Asia/Singapore:{value}"
            else:
                line = f"{key}:{value}"
            lines_to_write.append(line)
        end = "END:VEVENT"
        lines_to_write.append(end)

    begin_calendar_marker = "BEGIN:VCALENDAR"
    end_calendar_marker = "END:VCALENDAR"
    version_marker = "VERSION:2.0"

    # add timezone information
    timezone_information = [
        "BEGIN:VTIMEZONE",
        "TZID:Asia/Singapore",
        "BEGIN:DAYLIGHT",
        "TZOFFSETFROM:+0700",
        "DTSTART:19330101T000000",
        "TZNAME:GMT+8",
        "TZOFFSETTO:+0720",
        "RDATE:19330101T000000",
        "END:DAYLIGHT",
        "BEGIN:STANDARD",
        "TZOFFSETFROM:+0730",
        "DTSTART:19820101T000000",
        "TZNAME:SGT",
        "TZOFFSETTO:+0800",
        "RDATE:19820101T000000",
        "END:STANDARD",
        "END:VTIMEZONE",
    ]

    lines_to_write: List[str] = (
        [begin_calendar_marker]
        + timezone_information
        + lines_to_write
        + [version_marker, end_calendar_marker]
    )
    string_to_write: str = "\n".join(lines_to_write)
    return string_to_write


def fix(ics_path: str):
    ics_path = Path(ics_path)
    if not ics_path.is_file():
        logger.error(f"Invalid ics_path path: '{ics_path}'")
        raise Exception(f"Invalid ics_path path: '{ics_path}'")
    else:
        ics_path = ics_path.resolve()

    if str(ics_path)[-4:] != ".ics":
        logger.error(f"'{ics_path}' is not an '.ics' ics_path")
        raise Exception(f"'{ics_path}' is not an '.ics' ics_path")

    event_list = get_event_list(ics_path)
    parsed_event_list = parse_event_list(event_list)
    new_content = generate_new_content_to_write(parsed_event_list)

    # create a new ics ics_path
    folder: Path = ics_path.parent
    export_fp: Path = folder / (ics_path.stem + "_new.ics")
    with export_fp.open(mode="w") as f:
        f.write(new_content)

    logger.debug(f"Successfully exported: {export_fp}")
    return export_fp, len(parsed_event_list)


if __name__ == "__main__":
    fix("tests/resources/ics/term4.ics")
