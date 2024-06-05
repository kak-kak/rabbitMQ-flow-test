FROM python:3.9-slim

# pikaをインストール
RUN pip install pika

# Pythonのソースコードをコピー
COPY subscriber.py /usr/src/subscriber.py

# 実行コマンド
CMD ["sh", "-c", "sleep 5 && python /usr/src/subscriber.py"]