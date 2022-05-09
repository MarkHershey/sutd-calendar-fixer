# SUTD `schedule.ics` Fixer

[![](https://img.shields.io/badge/license-MIT-blue)](https://github.com/MarkHershey/sutd-calendar-fixer/blob/master/LICENSE)
[![](https://img.shields.io/badge/code%20style-black-black)](https://github.com/psf/black)

---

Do you know that you can import your class schedule into your Google Calendar?

You can download a `schedule.ics` file from [mymobile.sutd.edu.sg](http://mymobile.sutd.edu.sg/), but the original file is badly formatted and it won't look good on your calendar App.

This bot helps you clean up the mess in the `schedule.ics` file so that you will get a neat calendar view.

|                       Before                       |                       After                       |
| :------------------------------------------------: | :-----------------------------------------------: |
| <img src="imgs/before.png" height=auto width=auto> | <img src="imgs/after.png" height=auto width=auto> |

## Usage

### Interactive:

Just talk to [**this telegram bot (@sutd_ics_bot)**](https://t.me/sutd_ics_bot) and follow the step-by-step instructions from there.

### Manual:

In case the telegram bot is not working, you can also do it manually by following the steps below:

1. clone this repository to your local machine
    ```bash
    git clone https://github.com/MarkHershey/sutd-calendar-fixer.git
    ```
2. install dependencies:
    ```bash
    cd sutd-calendar-fixer
    python3 -m pip install -r requirements.txt
    ```
3. run the following command:
    ```bash
    python3 src/calendarFixer.py "path/to/your/schedule.ics"
    ```

## Report issues

If the bot isn't working as you expected, please [Create a New issue](https://github.com/MarkHershey/calendar-generator/issues).

---

## Development

Pull requests, issue reporting, feature requests are very welcomed.

### Dependencies

-   Python 3.x & [requirements.txt](requirements.txt)
    ```bash
    pip install -r requirements.txt
    ```
-   [docker](https://docs.docker.com/engine/install/) & [docker-compose](https://docs.docker.com/compose/install/)

### Run in Docker

1. Modify `docker-compose.yml` file, substitute your own Telegram `BOT_TOKEN`.
2. run `docker-compose build`
3. run `docker-compose up -d`

### Check logs

```bash
cat "logs/debug.txt"
```

## License

[MIT LICENSE - Copyright (c) 2020-2022 Mark Huang](LICENSE)
