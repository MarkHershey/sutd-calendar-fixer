FROM python:3.12

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --upgrade pip wheel setuptools

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "src/bot.py"]
