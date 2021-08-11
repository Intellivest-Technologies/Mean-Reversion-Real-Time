FROM python:3.7-slim-buster
ENV TZ="America/Phoenix"
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
CMD ["real_time_mean_reversion.py"]
ENTRYPOINT ["python3"]