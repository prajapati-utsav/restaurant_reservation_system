FROM python:3.10
RUN mkdir /app
WORKDIR /app
COPY . .
COPY requirements.txt requirements.txt
RUN apt-get update -y && apt-get install -y default-libmysqlclient-dev gcc && rm -rf /var/lib/apt/lists/*
RUN pip install --upgrade pip && pip install -r requirements.txt
EXPOSE 6001
CMD ["python", "main.py"]