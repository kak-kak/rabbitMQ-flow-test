FROM python:3.9-slim

# pikaをインストール
RUN pip install pika fastapi uvicorn

# Pythonのソースコードをコピー
COPY web.py /usr/src/web.py

# 実行コマンド
CMD ["sh", "-c", "sleep 5 && python /usr/src/web.py"]