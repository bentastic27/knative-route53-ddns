from flask import Flask, request

from cloudevents.http import from_http

app = Flask(__name__)


@app.route("/", methods=["POST"])
def home():
  event = from_http(request.headers, request.get_data())

  print(
    f"Found {event['id']} from {event['source']} with type "
    f"{event['type']} and specversion {event['specversion']}"
  )

  return "", 204


if __name__ == "__main__":
  app.run(port=8080)
