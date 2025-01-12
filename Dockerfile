FROM python:3.11
# set work directory
WORKDIR /app
COPY ./requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
ENV BOT_TOKEN = $BOT_TOKEN
COPY ./app.py ./
COPY ./test.jpg ./

# run app
CMD ["python", "app.py"]
