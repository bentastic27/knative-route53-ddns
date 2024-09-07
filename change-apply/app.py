import json

import boto3
from flask import Flask, request
from cloudevents.http import from_http


app = Flask(__name__)
r53client = boto3.client('route53')


@app.route("/", methods=["POST"])
def main():
  try:
    event = from_http(request.headers, request.get_data()).get_data()

    r53client.change_resource_record_sets(
      HostedZoneId=event["hosted_zone_id"],
      ChangeBatch={
        "Changes": [{
          "Action": "UPSERT",
          "ResourceRecordSet": {
            "Name": event["record_name"],
            "Type": event["record_type"],
            "TTL": int(event["record_ttl"]),
            "ResourceRecords": [{
              "Value": event["wan_ip"]
            }]
          }
        }]
      }
    )
    return "", 204

  except Exception as e:
    print(e)
    return "", 500


@app.route("/health", methods=["POST"])
def health():
  return "", 200


if __name__ == "__main__":
  app.run(port=8080)
