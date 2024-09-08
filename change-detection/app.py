from os import environ
from time import sleep
from pprint import pprint

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
  try:
    list_resource_record_sets = r53client.list_resource_record_sets(
      HostedZoneId=environ.get("HOSTED_ZONE_ID"),
      StartRecordName=record_name,
      StartRecordType=environ.get("RECORD_TYPE", "A"),
      MaxItems="300"
    )
    if not list_resource_record_sets:
      print("check your envs, r53 call returned nothing")
      exit(1)
  except Exception as e:
    print(e)
    exit(1)

  filtered = list(filter(
    lambda d: d["Name"] == record_name and d["Type"] == "A",
    list_resource_record_sets["ResourceRecordSets"]
  ))

  pprint(filtered)

  if len(filtered) > 0:
    r53_ip = filtered[0]["ResourceRecords"][0]["Value"]
  else:
    r53_ip = ""
  
  wan_ip = get('https://api.ipify.org').content.decode('utf8')

  if r53_ip != wan_ip:
    print(f"wan_ip: {wan_ip} r53_ip: {r53_ip} mismatch, sending event")

    cd_data = {
      "r53_ip": r53_ip,
      "wan_ip": wan_ip,
      "record_name": record_name,
      "record_type": environ.get("RECORD_TYPE", "A"),
      "hosted_zone_id": environ.get("HOSTED_ZONE_ID"),
      "record_ttl": environ.get("RECORD_TTL", "300")
    }

    pprint(cd_data)

    try:
      event = CloudEvent(ce_attributes, cd_data)
      headers, body = to_structured(event)
      print(post(environ.get("K_SINK", "http://localhost:8080/"), data=body, headers=headers).status_code)
    except Exception as e:
      print(e)
      exit(1)

  else:
    print(f"wan_ip: {wan_ip} r53_ip: {r53_ip} matched")

  sleep(int(environ.get("SLEEP_INTERVAL", "300")))