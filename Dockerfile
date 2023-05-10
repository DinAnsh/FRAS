FROM python:3.7.16
WORKDIR /FRAS

COPY requirements.txt .

RUN pip install --upgrade pip
RUN apt-get update && apt-get install -y python3-opencv
RUN pip install -r requirements.txt


COPY . .
WORKDIR /FRAS/testsite/

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]