FROM python:3.11
# set work directory
WORKDIR /app
COPY ./requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
ENV BOT_TOKEN=YOUR_TOKEN
ENV GIGA_TOKEN=YOUR_TOKEN
COPY ./app.py ./
COPY ./petia.png ./
# run app
CMD ["python", "app.py"]
