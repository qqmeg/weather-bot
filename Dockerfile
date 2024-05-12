FROM python:3.10-alpine
COPY requirements.txt .
RUN pip install -r requirements.txt
ADD weather.py .
CMD python weather.py
