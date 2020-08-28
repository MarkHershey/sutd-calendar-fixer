FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# VOLUME ["/usr_data"]

CMD ["python", "src/bot.py"]
