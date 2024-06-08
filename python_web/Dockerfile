FROM python:3.9-slim

RUN pip install pika fastapi uvicorn

# COPY . /usr/src/web.py
# copy all files in cd
COPY . /usr/src

CMD ["sh", "-c", "sleep 5 && cd /usr/src && python web.py"]