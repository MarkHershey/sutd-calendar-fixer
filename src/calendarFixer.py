from pathlib import Path
from typing import List, Dict, Tuple
from markkk.logger import logger
from pprint import pprint
from collections import OrderedDict


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
            "SUMMARY": None,
            "DESCRIPTION": None,
            "LOCATION": None,
            "DTSTART": None,
            "DTEND": None,
            "UID": None,
            "RRULE": None,
            "EXDATE": None,
        }
    )

    for line in event_lines:
        colon_index = line.find(":")
        key = line[:colon_index]
        if key not in event:
            continue
        line_value = line[colon_index + 1 :]
        event[key] = line_value

    # correct summary
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

    unused = []
    for key in event.keys():
        if not event.get(key):
            unused.append(key)

    for key in unused:
        event.pop(key)

    return event


def parse_event_list(event_list: List[List[str]]) -> List[Dict]:
    parsed_event_list = []
    for event in event_list:
        parsed_event = parse_single_event(event)
        parsed_event_list.append(parsed_event)
    return parsed_event_list


def generate_new_content_to_write(parsed_event_list: List[Dict]) -> str:
    lines_to_write: List[str] = []
    for event in parsed_event_list:
        start = "BEGIN:VEVENT"
        lines_to_write.append(start)
        for key, value in event.items():
            line = f"{key}:{value}"
            lines_to_write.append(line)
        end = "END:VEVENT"
        lines_to_write.append(end)

    lines_to_write.insert(0, "BEGIN:VCALENDAR")
    lines_to_write.append("VERSION:2.0\nEND:VCALENDAR")

    string_to_write = "\n".join(lines_to_write)
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


if __name__ == "__main__":
    fix("tests/resources/original_ics/term4.ics")
