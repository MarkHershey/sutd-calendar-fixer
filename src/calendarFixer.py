from collections import OrderedDict
from pathlib import Path
from typing import Dict, List, Tuple

from puts import get_logger

LOGGER = get_logger()


def fix_broken_lines(event_lines_list: List[str]) -> List[str]:
    """Fix broken lines if any"""

    # list of expected keywords in SUTD-generated ics files
    KEYWORDS = (
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

    fixed: List[str] = []

    for line in event_lines_list:
        line = line.strip()
        colon_index = line.find(":")
        if colon_index != -1:
            key = line[:colon_index]
            if key in KEYWORDS:
                fixed.append(line)
            else:
                # this is a broken line
                # it should join with the previous line
                fixed[-1] = fixed[-1] + line
        else:
            # this is a broken line too
            # it should join with the previous line
            fixed[-1] = fixed[-1] + line

    return fixed


def get_event_list(ics_path: str) -> List[List[str]]:
    ics_path = Path(ics_path)
    if not ics_path.is_file():
        LOGGER.error("File does not exist.")

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
        LOGGER.error("Invalid Event")
        return

    event = OrderedDict(
        {
            "SUMMARY": None,  # Title
            "DESCRIPTION": None,  # Description
            "LOCATION": None,  # Location
            "DTSTART": None,  # Date Start
            "DTEND": None,  # Date End
            "UID": None,  # Unique Identifier
            "RRULE": None,  # Recurrence Rule
            "EXDATE": None,  # Exception Date
        }
    )

    for line in event_lines:
        """Each line looks like 'KEY:LINE_VALUE'"""

        # find the index of the colon separating KEY and LINE_VALUE
        colon_index = line.find(":")
        # get KEY literal
        key = line[:colon_index]
        # skip unnecessary keys
        if key not in event:
            continue
        # get LINE_VALUE literal
        line_value = line[colon_index + 1 :]
        # store LINE_VALUE in event dict
        event[key] = line_value

    # 'Summary' fix
    original_summary = event.get("SUMMARY")
    # LOGGER.info(original_summary)
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

    # Fix useless recurrence rules
    if event.get("RRULE"):
        rrule_value: str = event.get("RRULE")
        # check when the recurrence rule ends
        if "UNTIL=" in rrule_value:
            s_idx = rrule_value.find("UNTIL=")
            e_idx = rrule_value.find(";", s_idx)
            s_idx += 6
        recurring_until = rrule_value[s_idx:e_idx]
        # if the recurrence rule ends the same time as the event end time,
        # it is a redundant recurrence rule
        if recurring_until == event.get("DTEND"):
            event["RRULE"] = None
            event["EXDATE"] = None

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


def fix(ics_path: str) -> Tuple[Path, int]:
    ics_path = Path(ics_path)
    if not ics_path.is_file():
        LOGGER.error(f"Invalid ics_path path: '{ics_path}'")
        raise Exception(f"Invalid ics_path path: '{ics_path}'")
    else:
        ics_path = ics_path.resolve()

    if str(ics_path)[-4:] != ".ics":
        LOGGER.error(f"'{ics_path}' is not an '.ics' ics_path")
        raise Exception(f"'{ics_path}' is not an '.ics' ics_path")

    event_list = get_event_list(ics_path)
    parsed_event_list = parse_event_list(event_list)
    new_content = generate_new_content_to_write(parsed_event_list)

    # create a new ics ics_path
    folder: Path = ics_path.parent
    export_fp: Path = folder / (ics_path.stem + "_new.ics")
    with export_fp.open(mode="w") as f:
        f.write(new_content)

    LOGGER.info(f"Successfully exported: {export_fp}")
    return export_fp, len(parsed_event_list)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Fix ics file")
    parser.add_argument(
        "ics_path",
        type=str,
        help="specify ics file path",
    )
    args = parser.parse_args()
    fix(args.ics_path)
