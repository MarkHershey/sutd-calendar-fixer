# calendar-generator

## Usage
1. Go to [mymobile.sutd.edu.sg](mymobile.sutd.edu.sg)
2. Student Log In > Schedule > Top-right option icon > Download Schedule > Select Term 
3. You will get `schedule.ics` for your selected term
4. Download this Python file [`ics_fixer2.py`](https://github.com/MarkHershey/calendar-generator/blob/master/ics_fixer2.py)
5. Open `ics_fixer2.py` using any text editor and change the `path` variable to the path of your `schedule.ics`
6. Save and Run `python3 ics_fixer2.py`
7. `new.ics` will be generated, which is the cleaned version of your schedule.
8. import to your google calendar now!
