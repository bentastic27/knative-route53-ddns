## TODO: add cm configs for pods

Required envs:

```
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
RECORD_NAME
HOSTED_ZONE_ID
```

Creat cm and secrets:

```
kubectl -n knative-route53-ddns create configmap knative-route53-ddns --from-literal RECORD_NAME=sometest.beansnet.net --from-literal HOSTED_ZONE_ID=Z0466241UWHPLQN701UT

kubectl create secret generic -n knative-route53-ddns aws-creds --from-literal AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID --from-literal AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY
```