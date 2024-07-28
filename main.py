import os
import sys
import time
import json
import random
import argparse
from curl_cffi import requests
import json
from json import dumps as dp, loads as ld
from datetime import datetime
from colorama import *
from urllib.parse import unquote, parse_qs
from base64 import b64decode

init(autoreset=True)

merah = Fore.LIGHTRED_EX
putih = Fore.LIGHTWHITE_EX
hijau = Fore.LIGHTGREEN_EX
kuning = Fore.LIGHTYELLOW_EX
biru = Fore.LIGHTBLUE_EX
reset = Style.RESET_ALL
hitam = Fore.LIGHTBLACK_EX

class Popptod:
  garis = putih + "=" * 51

  def data_parsing(self, data):
    return {k: v[0] for k, v in parse_qs(data).items()}
  
  def renewAccessToken(self, query_id) :
    headers = {
      'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0",
      'Accept': "application/json",
      'Accept-Encoding': "gzip, deflate, br, zstd",
      'sec-ch-ua': "\"Not/A)Brand\";v=\"8\", \"Chromium\";v=\"126\", \"Microsoft Edge\";v=\"126\", \"Microsoft Edge WebView2\";v=\"126\"",
      'content-type': "application/json;charset=utf-8",
      'sec-ch-ua-mobile': "?0",
      'sec-ch-ua-platform': "\"Windows\"",
      'Origin': "https://planet.popp.club",
      'Sec-Fetch-Site': "same-site",
      'Sec-Fetch-Mode': "cors",
      'Sec-Fetch-Dest': "empty",
      'Referer': "https://planet.popp.club/",
      'Accept-Language': "en-US,en;q=0.9"
    }

    url = "https://moon.popp.club/pass/login"
    user = self.data_parsing(query_id)
    parse = json.loads(user["user"])
    if "chat_instance" not in user.keys():
     chat_instance = "Null"
    else :
      chat_instance = user["chat_instance"]

    payload = json.dumps({
      "initData": query_id,
      "initDataUnSafe": {
        "user": {
          "id": int(parse["id"]),
          "first_name": parse['first_name'],
          "last_name": "",
          "username": parse['username'],
          "language_code": "en",
          "allows_write_to_pm": True
        },
        "chat_instance": chat_instance,
        "chat_type": "supergroup",
        "start_param": "6944804952",
        "auth_date": user["auth_date"],
        "hash": user["hash"]
      },
      "inviteUid": "6944804952"
    })

    response = requests.post(url, data=payload, headers=headers)
    if response.json()["code"] != "00":
      self.log(f"{merah}'token' is not found in response, check you data !!")
      return False
    access_token = response.json()["data"]["token"]
    self.log(f"{hijau}success get access token ")
    return access_token
  
  def get_local_token(self, userid):
    if not os.path.exists("tokens.json"):
        open("tokens.json", "w").write(json.dumps({}))
    tokens = json.loads(open("tokens.json", "r").read())
    if str(userid) not in tokens.keys():
        return False

    return tokens[str(userid)]
  
  def log(self, message):
    now = datetime.now().isoformat(" ").split(".")[0]
    print(f"{hitam}[{now}]{reset} {message}")

  def save_local_token(self, userid, token):
    tokens = json.loads(open("tokens.json", "r").read())
    tokens[str(userid)] = token
    open("tokens.json", "w").write(json.dumps(tokens, indent=4))

  def save_failed_token(self,userid,data):
    file = "auth_failed.json"
    if not os.path.exists(file):
        open(file,"w").write(json.dumps({}))
    
    acc = json.loads(open(file,'r').read())
    if str(userid) in acc.keys():
        return
    
    acc[str(userid)] = data
    open(file,'w').write(json.dumps(acc,indent=4))
  
  def countdown(self, t):
    while t:
        menit, detik = divmod(t, 60)
        jam, menit = divmod(menit, 60)
        jam = str(jam).zfill(2)
        menit = str(menit).zfill(2)
        detik = str(detik).zfill(2)
        print(f"{kuning}waiting until {jam}:{menit}:{detik} ", flush=True, end="\r")
        t -= 1
        time.sleep(1)
    print("                          ", flush=True, end="\r")

  def signin(self, token):
    url = "https://moon.popp.club/moon/sign/in"
    headers = {
      'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0",
      'Accept': "application/json",
      'Accept-Encoding': "gzip, deflate, br, zstd",
      'sec-ch-ua': "\"Not/A)Brand\";v=\"8\", \"Chromium\";v=\"126\", \"Microsoft Edge\";v=\"126\", \"Microsoft Edge WebView2\";v=\"126\"",
      'content-type': "application/json;charset=utf-8",
      'sec-ch-ua-mobile': "?0",
      'Authorization': token,
      'sec-ch-ua-platform': "\"Windows\"",
      'Origin': "https://planet.popp.club",
      'Sec-Fetch-Site': "same-site",
      'Sec-Fetch-Mode': "cors",
      'Sec-Fetch-Dest': "empty",
      'Referer': "https://planet.popp.club/",
      'Accept-Language': "en-US,en;q=0.9"
    }

    response = requests.post(url, headers=headers)
    print(response.text)

  def getAssets(self, token):
    url = "https://moon.popp.club/moon/asset"
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0",
        'Accept': "application/json",
        'Accept-Encoding': "gzip, deflate, br, zstd",
        'sec-ch-ua': "\"Not/A)Brand\";v=\"8\", \"Chromium\";v=\"126\", \"Microsoft Edge\";v=\"126\", \"Microsoft Edge WebView2\";v=\"126\"",
        'content-type': "application/json;charset=utf-8",
        'sec-ch-ua-mobile': "?0",
        'Authorization': token,
        'sec-ch-ua-platform': "\"Windows\"",
        'Origin': "https://planet.popp.club",
        'Sec-Fetch-Site': "same-site",
        'Sec-Fetch-Mode': "cors",
        'Sec-Fetch-Dest': "empty",
        'Referer': "https://planet.popp.club/",
        'Accept-Language': "en-US,en;q=0.9"
    }

    
    response = requests.get(url, headers=headers)
    if response.json()["code"] == "00":
        data = response.json()["data"]
        self.log(f"{hijau}Balance: {data['sd']} SD | {data['probe']} PROBE | {data['eth']} ETH")
    else:
        self.log(f"{merah}Failed get assets !")



  def getPlanets(self, token):
    url = "https://moon.popp.club/moon/planets"
    headers = {
      'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0",
      'Accept': "application/json",
      'Accept-Encoding': "gzip, deflate, br, zstd",
      'sec-ch-ua': "\"Not/A)Brand\";v=\"8\", \"Chromium\";v=\"126\", \"Microsoft Edge\";v=\"126\", \"Microsoft Edge WebView2\";v=\"126\"",
      'content-type': "application/json;charset=utf-8",
      'sec-ch-ua-mobile': "?0",
      'Authorization': token,
      'sec-ch-ua-platform': "\"Windows\"",
      'Origin': "https://planet.popp.club",
      'Sec-Fetch-Site': "same-site",
      'Sec-Fetch-Mode': "cors",
      'Sec-Fetch-Dest': "empty",
      'Referer': "https://planet.popp.club/",
      'Accept-Language': "en-US,en;q=0.9"
    }

    response = requests.get(url, headers=headers)
    if response.json()["code"] == "00":
      data = response.json()["data"]
      for no, data in enumerate(data):
        planetsId = data["id"]
        self.log(f"{kuning}Opening planet {planetsId}" )
        return self.explorer(token, planetsId)
    else:
      self.log(f"{merah}Failed get planets !")
      
  def explorer(self, token, planetId):
    url = "https://moon.popp.club/moon/explorer"

    params = {
      'plantId': planetId
    }

    headers = {
      'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0",
      'Accept': "application/json",
      'Accept-Encoding': "gzip, deflate, br, zstd",
      'sec-ch-ua': "\"Not/A)Brand\";v=\"8\", \"Chromium\";v=\"126\", \"Microsoft Edge\";v=\"126\", \"Microsoft Edge WebView2\";v=\"126\"",
      'content-type': "application/json;charset=utf-8",
      'sec-ch-ua-mobile': "?0",
      'Authorization': token,
      'sec-ch-ua-platform': "\"Windows\"",
      'Origin': "https://planet.popp.club",
      'Sec-Fetch-Site': "same-site",
      'Sec-Fetch-Mode': "cors",
      'Sec-Fetch-Dest': "empty",
      'Referer': "https://planet.popp.club/",
      'Accept-Language': "en-US,en;q=0.9"
    }

    response = requests.get(url, params=params, headers=headers)
    if response.json()["code"] == "00":
      data = response.json()["data"]
      self.log(f"{kuning}Opening planet {planetId} got {data['amount']} {data['award']}")
    else:
      self.log(f"{merah}Failed opening planets !")

  def claimFarming(self, token):
    url = "https://moon.popp.club/moon/claim/farming"
    headers = {
      'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0",
      'Accept-Encoding': "gzip, deflate, br, zstd",
      'sec-ch-ua': "\"Not/A)Brand\";v=\"8\", \"Chromium\";v=\"126\", \"Microsoft Edge\";v=\"126\", \"Microsoft Edge WebView2\";v=\"126\"",
      'content-type': "application/json;charset=utf-8",
      'sec-ch-ua-mobile': "?0",
      'Authorization': token,
      'sec-ch-ua-platform': "\"Windows\"",
      'Origin': "https://planet.popp.club",
      'Sec-Fetch-Site': "same-site",
      'Sec-Fetch-Mode': "cors",
      'Sec-Fetch-Dest': "empty",
      'Referer': "https://planet.popp.club/",
      'Accept-Language': "en-US,en;q=0.9"
    }

    response = requests.get(url, headers=headers)
    if response.json()["code"] == "00":
      self.log(f"{hijau}Success claim farming !!" )
    else:
      self.log(f"{merah}Failed to claim !")

  def startFarming(self, token):
    url = "https://moon.popp.club/moon/farming"

    headers = {
      'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0",
      'Accept-Encoding': "gzip, deflate, br, zstd",
      'sec-ch-ua': "\"Not/A)Brand\";v=\"8\", \"Chromium\";v=\"126\", \"Microsoft Edge\";v=\"126\", \"Microsoft Edge WebView2\";v=\"126\"",
      'content-type': "application/json;charset=utf-8",
      'sec-ch-ua-mobile': "?0",
      'Authorization': token,
      'sec-ch-ua-platform': "\"Windows\"",
      'Origin': "https://planet.popp.club",
      'Sec-Fetch-Site': "same-site",
      'Sec-Fetch-Mode': "cors",
      'Sec-Fetch-Dest': "empty",
      'Referer': "https://planet.popp.club/",
      'Accept-Language': "en-US,en;q=0.9"
    }

    response = requests.get(url, headers=headers)
    if response.json()["code"] == "00":
      self.log(f"{hijau}Success start farming !!" )
    else:
      self.log(f"{merah}Failed to start farming !")

  def claimReff(self, token):
    url = "https://moon.popp.club/moon/claim/invite"
    headers = {
      'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0",
      'Accept-Encoding': "gzip, deflate, br, zstd",
      'sec-ch-ua': "\"Not/A)Brand\";v=\"8\", \"Chromium\";v=\"126\", \"Microsoft Edge\";v=\"126\", \"Microsoft Edge WebView2\";v=\"126\"",
      'content-type': "application/json;charset=utf-8",
      'sec-ch-ua-mobile': "?0",
      'Authorization': token,
      'sec-ch-ua-platform': "\"Windows\"",
      'Origin': "https://planet.popp.club",
      'Sec-Fetch-Site': "same-site",
      'Sec-Fetch-Mode': "cors",
      'Sec-Fetch-Dest': "empty",
      'Referer': "https://planet.popp.club/",
      'Accept-Language': "en-US,en;q=0.9"
    }

    response = requests.get(url, headers=headers)
    if response.json()["code"] == "00":
      self.log(f"{hijau}Success claim ref bonus !!" )
    else:
      self.log(f"{merah}Failed to claim ref bonus !")


  def main(self):
    datas = open("data.txt", "r").read().splitlines()
    self.log(f"{hijau}total account : {putih}{len(datas)}")
    if len(datas) <= 0:
        self.log(f"{merah}add data account in Query first")
        sys.exit()

    self.log(self.garis)
    while True:
      for no, data in enumerate(datas):
        self.log(f"{hijau}account number - {putih}{no + 1}")
        data_parse = self.data_parsing(data)
        user = json.loads(data_parse["user"])
        userid = user["id"]
        self.log(f"{hijau}login as : {putih}{user['first_name']}")
        access_token = self.get_local_token(userid)
        if access_token is False:
          access_token = self.renewAccessToken(data)
          if access_token is False:
            self.save_failed_token(userid, data)
            continue
          self.save_local_token(userid, access_token)

          self.countdown(5)
        # self.signin(access_token)
        self.getAssets(access_token)
        self.getPlanets(access_token)
        self.claimFarming(access_token)
        self.countdown(5)
        self.startFarming(access_token)
        self.claimReff(access_token)
        self.countdown(5)
        self.garis = merah + "=" * 51
      self.countdown(370)



if __name__ == "__main__":
  app = Popptod()
  try:
    app.main()
  except Exception as e:
    # 
    print(e)