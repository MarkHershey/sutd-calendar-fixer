# SUTD `schedule.ics` Fixer

<img src="https://img.shields.io/github/license/MarkHershey/calendar-generator?style=plastic">

---

Do you know that you can import your class schedule into your Google Calendar?

You can download a `schedule.ics` file from [mymobile.sutd.edu.sg](http://mymobile.sutd.edu.sg/), but the original file is badly formatted and it won't look good on your calendar App.

This bot helps you clean up the mess in the `schedule.ics` file so that you will get a neat calendar view.

| Before | After |
| :---: | :---: |
| <img src="imgs/before.png" height=auto width=auto> | <img src="imgs/after.png" height=auto width=auto> |


## Usage

Just talk to [**this telegram bot (@sutd_ics_bot)**](https://t.me/sutd_ics_bot) and follow the step-by-step instructions from there.

## Report issues

If the bot isn't working as you expected, please [Create a New issue](https://github.com/MarkHershey/calendar-generator/issues).


---

## Development

### Dependencies

- Python 3.x & [requirements.txt](requirements.txt)
    ```bash
    pip install -r requirements.txt
    ```
- [docker](https://docs.docker.com/engine/install/) & [docker-compose](https://docs.docker.com/compose/install/)

### Run in Docker

1. Modify `docker-compose.yml` file, substitute your own Telegram `BOT_TOKEN`.
2. run `docker-compose build`
3. run `docker-compose up -d`

### Check logs

```bash
cat "logs/debug.txt"
```

### TODOs

- [x] Timezone Info Injection
- [ ] Recurring Event Validation

Pull requests, issue reporting, feature requests are very welcomed.

## License

[MIT LICENSE - Copyright (c) 2020-2021 Mark Huang](LICENSE)
