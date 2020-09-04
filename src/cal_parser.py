from pathlib import Path
from typing import List, Dict, Tuple
from markkk.logger import logger
from pprint import pprint


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

    event = {
        "SUMMARY": None,
        "DESCRIPTION": None,
        "DTSTART": None,
        "DTEND": None,
        "UID": None,
        "RRULE": None,
        "EXDATE": None,
    }

    for line in event_lines:
        colon_index = line.find(":")
        key = line[:colon_index]
        if key not in event:
            continue
        line_value = line[colon_index + 1 :]
        event[key] = line_value

    return event


def parse_event_list(event_list: List[List[str]]) -> List[Dict]:
    parsed_event_list = []
    for event in event_list:
        parsed_event = parse_single_event(event)
        parsed_event_list.append(parsed_event)
    return parsed_event_list


if __name__ == "__main__":
    event_list = get_event_list("tests/resources/original_ics/term4.ics")
    parsed_event_list = parse_event_list(event_list)
    pprint(parsed_event_list)
