FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt /app/
COPY app.py /app/

RUN pip install -r requirements.txt --no-cache-dir --no-compile

RUN groupadd --gid 1000 appuser && \
  useradd --uid 1000 --gid 1000 -M appuser -s /sbin/nologin -d /app && \
  chown -R 1000.1000 /app

USER appuser

ENTRYPOINT ["/usr/local/bin/python", "/app/app.py"]