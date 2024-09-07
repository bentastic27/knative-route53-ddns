from os import environ
from time import sleep

import boto3
from requests import get, post
from cloudevents.conversion import to_structured
from cloudevents.http import CloudEvent

r53client = boto3.client('route53')

if not environ.get("RECORD_NAME", "example.com.").endswith("."):
  record_name = environ.get("RECORD_NAME", "example.com.") + "."
else:
  record_name = environ.get("RECORD_NAME", "example.com.")

ce_attributes = {
  "type": "r53-wan-ip-mismatch",
  "source": environ.get("CE_EVENT_SOURCE", "knative-route53-dns")
}

while(True):
  list_resource_record_sets = r53client.list_resource_record_sets(
    HostedZoneId=environ.get("HOSTED_ZONE_ID"),
    StartRecordName=record_name,
    StartRecordType="A",
    MaxItems="300"
  )

  filtered = list(filter(
    lambda d: d["Name"] == record_name and d["Type"] == "A",
    list_resource_record_sets["ResourceRecordSets"]
  ))

  r53_ip = filtered[0]["ResourceRecords"][0]["Value"]
  wan_ip = get('https://api.ipify.org').content.decode('utf8')

  if r53_ip != wan_ip:
    print(f"wan_ip: {wan_ip} r53_ip: {r53_ip} mismatch, sending event")
    cd_data = {"r53_ip": r53_ip, "wan_ip": wan_ip}
    event = CloudEvent(ce_attributes, cd_data)
    headers, body = to_structured(event)
    post(environ.get("K_SINK", "http://localhost:8080/"), data=body, headers=headers)
  else:
    print(f"wan_ip: {wan_ip} r53_ip: {r53_ip} matched")

  sleep(int(environ.get("SLEEP_INTERVAL", "300")))