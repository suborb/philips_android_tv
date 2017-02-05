from base64 import b64encode,b64decode
from datetime import datetime
import json
import sys
import requests
import random
import string
from Crypto.Hash import SHA, HMAC
from requests.auth import HTTPDigestAuth
import argparse

# Key used for generated the HMAC signature
secret_key="ZmVay1EQVFOaZhwQ4Kv81ypLAZNczV9sG4KkseXWn1NEk6cXmPKO/MCa9sryslvLCFMnNe4Z4CPXzToowvhHvA=="

def createDeviceId():
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for _ in range(16))


def create_signature(secret_key, to_sign):
    sign = HMAC.new(secret_key, to_sign, SHA)
    return b64encode(sign.hexdigest())

def getDeviceSpecJson(config):
    device_spec =  { "device_name" : "heliotrope", "device_os" : "Android", "app_name" : "ApplicationName", "type" : "native" }
    device_spec['app_id'] = config['application_id']
    device_spec['id'] = config['device_id']
    return device_spec


def pair(config):
    config['application_id'] = "app.id"
    config['device_id'] = createDeviceId()
    data = { 'scope' :  [ "read", "write", "control"] }
    data['device']  = getDeviceSpecJson(config)
    print("Starting pairing request")
    r = requests.post("https://" + config['address'] + ":1926/6/pair/request", json=data, verify=False)
    response = r.json()
    auth_Timestamp = response["timestamp"]
    config['auth_key'] = response["auth_key"]
    auth_Timeout = response["timeout"]

    pin = input("Enter onscreen passcode: ")

    auth = { "auth_AppId" : "1" }
    auth ['pin'] = str(pin)
    auth['auth_timestamp'] = auth_Timestamp
    auth['auth_signature'] = create_signature(b64decode(secret_key), str(auth_Timestamp) + str(pin))

    grant_request = {}
    grant_request['auth'] = auth
    grant_request['device']  = getDeviceSpecJson(config)

    print("Attempting to pair")
    r = requests.post("https://" + config['address'] +":1926/6/pair/grant", json=grant_request, verify=False,auth=HTTPDigestAuth(config['device_id'], config['auth_key']))
    print(r.json())
    print("Username for subsequent calls is: " + config['device_id'])
    print("Password for subsequent calls is: " + config['auth_key'])

def get_command(config):
    r = requests.get("https://" + config['address'] + ":1926/" + config['path'], verify=False,auth=HTTPDigestAuth(config['device_id'], config['auth_key']))
    print(r)
    print(r.url)
    print(r.text)
    print(r.json())


def post_command(config):
    r = requests.post("https://" + config['address'] + ":1926/" + config['path'], json=config['body'], verify=False,auth=HTTPDigestAuth(config['device_id'], config['auth_key']))
    print(r)


def main():
    config={}
    parser = argparse.ArgumentParser(description='Control a HuaFan WifiSwitch.')
    parser.add_argument("--host", dest='host', help="Host/address of the TV")
    parser.add_argument("--user", dest='user', help="Username")
    parser.add_argument("--pass", dest='password', help="Password")
    parser.add_argument("command",  help="Command to run (pair/get_volume/get/standby)")

    args = parser.parse_args()

    config['address'] = args.host
 
    if args.command == "pair":
        pair(config)

    config['device_id'] = args.user
    config['auth_key'] = args.password

    if args.command == "get_volume":
        config['path'] = "6/audio/volume"
        get_command(config)

    if args.command == "get":
        # All working commands
        config['path'] = "6/channeldb/tv"
        config['path'] = "6/applications"
        config['path'] = "6/ambilight/mode"
        config['path'] = "6/ambilight/topology"
        config['path'] = "6/recordings/list"
        config['path'] = "6/powerstate"
        config['path'] = "6/ambilight/currentconfiguration"
        config['path'] = "6/channeldb/tv/channelLists/all"
        config['path'] = "6/system/epgsource"
        config['path'] = "6/system"
        config['path'] = "6/system/storage"
        config['path'] = "6/system/timestamp"
        config['path'] = "6/menuitems/settings/structure"
        config['path'] = "6/ambilight/cached"
      
        get_command(config)

    if args.command == "standby":
        config['path'] = "6/input/key"
        config['body'] = { "key" : "Standby" }
        post_command(config)

main()




