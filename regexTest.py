import string

# event = [
# 'BEGIN:VEVENT\n',
# 'SUMMARY:Modelling the Systems World 11:00 AM-12:00 PM ROOM: Lecture Theatre\n',
# '  2 (1.203)\n',
# 'DTSTART:20200203T110000\n',
# 'DTEND:20200203T120000\n',
# 'UID:203b3dcb53db056f7306f0acf7e08b04@mymobile.sutd.edu.sg\n',
# 'STATUS:CONFIRMED\n',
# 'END:VEVENT\n']

def modifyEvent(event):

    if len(event) == 8:
        event[1] = event[1][0:-1]
        event[1] += event[2].strip()
        del event[2]

    # not_for_use = [
    # 'BEGIN:VEVENT\n',
    # 'SUMMARY:Modelling the Systems World 11:00 AM-12:00 PM ROOM: Lecture Theatre  2 (1.203)\n',
    # 'DTSTART:20200203T110000\n',
    # 'DTEND:20200203T120000\n',
    # 'UID:203b3dcb53db056f7306f0acf7e08b04@mymobile.sutd.edu.sg\n',
    # 'STATUS:CONFIRMED\n',
    # 'END:VEVENT\n']

    location_start = event[1].find("ROOM:")

    if location_start == -1:
        pass
    else:
        location_start += 6
        location = "LOCATION:" + event[1][location_start:-1] + "\n"
        event.insert(2,location)

    summary_end = 0

    for index, i in enumerate(event[1]):
        if i in string.digits:
            summary_end = index - 1
            break

    event[1] = event[1][0:summary_end] + "\n"
    return event

# not_for_use = [
# 'BEGIN:VEVENT\n',
# 'SUMMARY:Modelling the Systems World\n',
# 'LOCATION:Lecture Theatre  2 (1.203)\n',
# 'DTSTART:20200203T110000\n',
# 'DTEND:20200203T120000\n',
# 'UID:203b3dcb53db056f7306f0acf7e08b04@mymobile.sutd.edu.sg\n',
# 'STATUS:CONFIRMED\n',
# 'END:VEVENT\n']
