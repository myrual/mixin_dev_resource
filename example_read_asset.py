# -*- coding: utf-8 -*-
import web
import json
import requests
import jwt
import datetime
import calendar
import hashlib
import base64
import Crypto
import time
import uuid
import random

from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
from Crypto import Random
from Crypto.Cipher import PKCS1_OAEP


private_key = """-----BEGIN RSA PRIVATE KEY-----
MIICXAIBAAKBgQDG+84eobu6hfDYYr+hsTOFi9w0ska988FB009yDgWBmSQA3TNI
jl6QKZVuJ0TwPijUfzkc1af6dfvJ60J4REPHLdhUghg0oVgWOjrYlYadb7XIqzw4
a9R+NH66dHyXhVnoHxEM+2c7eUvam3vvj1UFQFx3iNPCxYganLtGarkffwIDAQAB
AoGAJmepU74xhoGdh5YfmGykHg1tdfpGrxjh3vuS5NeR9n6BNW18HW/lDnwILFeF
9bx5kvHvKwKNxkiJTWKL1LyQPAT9h78IkNlrW7ayLAwaasKg23UU8V+htf0WczAd
YWQ7woWU4ADbigximpmCtQCpuH7V6vvel72ny8QxYDGXOWECQQDt7e8fPBWjyHOp
uRivZi3prhDgf+pUIEYb4Sm5NEOa/wi+v76ZbZgg792rBGktq1Lt06d4vY2UpGr+
771cns9RAkEA1hilnNE8J6IcPSAfgFD9vYhVX0J6kNTKfLUeINlt7hiYeRTxP9d0
60Jdt/6btKW6AHpoCjngWFgXPTFO6OptzwJBAIj2dLZIQjS8CUjkUj911Gw2VWTG
fb/brEAUR45jdZ9dvE0B19g+bFpZegMeUOWHP//D3R32D/BHDYifvSP6D2ECQG2O
LzEP4LhnPAwLZBNFXpKeMRGN8yopuXQXOlOU76vm6h8LmGgS2MGKNGry3rqSE5wr
BxI0i5ipezrVAIwvagECQCHgwaDAobG5UpflHlzamTSu4OURVF1gomqSnpZp2AM9
r9fVfWzUIFLuXFM/1eM+MbZrDs9J1WHyaRHK+F/3WKs=
-----END RSA PRIVATE KEY-----"""


mixin_pin_token = """csEaHIh5RuVcXqcJ9aNp/AoubC/0L9ZtGWn037XREiR5JlbAvDW52obceJ9wWxVB12V9QxmabGmGR59wLoyfhfQeSVer56jOIUrOgL4ZXaMq32Rsddp2wpydEsCJbIjDftKwHJJvfz0XFAsNeBCTC+OfouaLW86Q50g3p7razbM="""

urls = (
    '/', 'userEntrance',
    '/auth','auth',
    '/credit','userEntrance'
)

mixin_client_id = "a932cac1-e05b-4095-b662-f5ab284050bf"
mixin_client_secret = "1e0ad062c61b498ed53312818c0d3b4fe067d756c2fc3283adff0cfb41577d70"
mixin_pay_pin = '515532'
mixin_pay_sessionid = '25083eb4-adab-49f3-9600-81d244b7cbc4'

class userEntrance:
    def GET(self):
        raise web.seeother('https://mixin.one/oauth/authorize?client_id=a932cac1-e05b-4095-b662-f5ab284050bf&scope=PROFILE:READ+ASSETS:READ')



class auth:
    def GET(self):
        mixindata = web.input(code = "no")
	print(mixindata)
        if mixindata.code == "no":
            return "I don't know you, can not give your bonus"

        r = requests.post('https://api.mixin.one/oauth/token', json = {"client_id": mixin_client_id, "code": mixindata.code,"client_secret": mixin_client_secret})
        result = r.json()
	print(result)
        if "data" not in result or "access_token" not in result["data"]:
            return "I don't know you, can not give your bonus"
        access_token = result["data"]["access_token"]
        personinfo = requests.get('https://api.mixin.one/me', headers = {"Authorization":"Bearer " + access_token})
	userid = personinfo.json()["data"]["user_id"]
	print(personinfo.json())
        assets_of_user = requests.get('https://api.mixin.one/assets', headers = {"Authorization":"Bearer " + access_token})
	assets_info = assets_of_user.json()["data"]
        htmlbody = ""
        totalAssetInUSD = 0.0
        for singleAsset in assets_info:
            if singleAsset["price_usd"] != "0":
                print(singleAsset["name"] + " id " + singleAsset["asset_id"])

            if singleAsset["price_usd"] != "0" and singleAsset["balance"] != "0":
                totalAssetInUSD = totalAssetInUSD + float(singleAsset["balance"]) * float(singleAsset["price_usd"])
                print("totalAssetInUSD is :" + str(totalAssetInUSD))
                assetstring = "<img src=" + singleAsset["icon_url"] + ">" + singleAsset["name"] + " : " + singleAsset["balance"] 
                htmlbody = htmlbody + assetstring + "<br>"
                print(assetstring)
        sendmessage_body = {}


        credit = int(totalAssetInUSD/2.0)
        totalUSDString = "Your credit: $ " + str(credit)

        return """<!DOCTYPE html>
<html>
<head>
<title>""" + totalUSDString + """</title>
</head>
<body>
<h1> Contact me at mixin with mixin id 31367 to know more</h1>
<h1>Service provided by <a href="https://babelbank.io">Babel</a></h1>>
</body>
</html> """



if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()
