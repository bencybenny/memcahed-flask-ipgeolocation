import os
import requests
import json
import memcache
from flask import Flask, jsonify
import boto3


def get_secret(*, secret_name=None, secret_key=None, region_name=None):
    secrets_client = boto3.client(service_name="secretsmanager", region_name=region_name)
    response = secrets_client.get_secret_value(SecretId=secret_name)
    ipgeolocation_secrets = json.loads(response['SecretString'])
    return ipgeolocation_secrets[secret_key]


def get_from_cache(*, host=None):
    try:
        mc = memcache.Client(['memc:11211'])
        cached_result = mc.get(host)
        if cached_result:
            output = json.loads(cached_result)
            output["cached"] = "True"
            return output
        else:
            return False
    except:
        return "Error in get_from_cache function."


def set_to_cache(*, host=None, ipgeolocation_key=None):
    try:
        mc = memcache.Client(['memc:11211'])
        ipgeolocation_url = "https://api.ipgeolocation.io/ipgeo?apiKey={}&ip={}".format(ipgeolocation_key, host)
        geodata = requests.get(url=ipgeolocation_url)
        geodata = geodata.json()
        geodata["cached"] = "False"
        mc.set(host, json.dumps(geodata), time=3600)
        return geodata
    except:
        return "Error in set_to_cache function."


app = Flask(__name__)


@app.route('/api/v1/<ip>')
def ipstack(ip=None):
    output = get_from_cache(host=ip)
    if output:
        return jsonify(output)
    output = set_to_cache(host=ip, ipgeolocation_key=ipgeolocation_key)
    return jsonify(output)


if __name__ == "__main__":
    app_port = os.getenv("APP_PORT", "8080")
    ipgeolocation_key = os.getenv("API_KEY", None)
    ipgeolocation_key_from_secrets = os.getenv("API_KEY_FROM_SECRETSMANAGER", False)
    ipgeolocation_key_secret_name = os.getenv("SECRET_NAME", None)
    ipgeolocation_key_name = os.getenv("SECRET_KEY", None)
    aws_region = os.getenv("REGION_NAME", None)

    if ipgeolocation_key_from_secrets == "True":
        ipgeolocation_key = get_secret(secret_name=ipgeolocation_key_secret_name,
                                       secret_key=ipgeolocation_key_name,
                                       region_name=aws_region)

    app.run(port=app_port, host="0.0.0.0", debug=True)
