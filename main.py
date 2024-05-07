import tls_client
import websocket
import json
import jwt
import concurrent.futures

session = tls_client.Session(

    client_identifier="chrome112",

    random_tls_extension_order=True

)
proxy = "", #FILL THIS  USER:PASS@IP:PORT ( WE ARE USING PROXIES TO AVOID RATE LIMIT )
api_key = "" # FCAP API KEY 

def solveCaptcha(rqdata):
        try:
            if api_key == "" or api_key == None:
                print("Please add your FCAP api Key in the code .")
            headers = {
                'content-type': 'application/json',
                "authorization": api_key,
                }
            payload = {
                "sitekey":"a9b5fb07-92ff-493f-86fe-352a2803b3df",
                "host":"https://discord.com",
                "proxy": proxy,  
                "rqdata":rqdata
            }

            result = session.post("https://api.fcaptcha.lol/api/createTask", headers=headers, json=payload)
            task_id = result.json()["task"]["task_id"]
            payload = {"task_id": task_id}
            while True:
                result = session.get(f"https://api.fcaptcha.lol/api/getTaskData", headers=headers, json=payload)
                data = result.json()
                if data["task"]["state"] == "processing":
                    continue
               
                capkey = data["task"]["captcha_key"]
                return capkey
        except Exception as e:
            print(f"Failed to solve -> {e}")                                
def makeJWT(guildID,channel):

    header = {
    "location": "Join Guild",
    "location_guild_id": guildID,
    "location_channel_id": channel,
    "location_channel_type": 0
    }

    encoded_header = jwt.encode(header, key=None, algorithm='none')
    encoded_header = encoded_header.split(".")[1]
    return encoded_header

def GetSessionID(token):
    ws = websocket.WebSocket()
    ws.connect("wss://gateway.discord.gg/?v=9&encoding=json")
    x = json.loads(ws.recv())
    auth = {
        "op": 2,
        "d": {
            "token": token,
            "properties": {
                "$os": "windows",
            },
        }
    }
    ws.send(json.dumps(auth))
    res = json.loads(ws.recv())
    return res["d"]["session_id"]

def main(tokens, invite):
    if proxy != None and proxy != "":
        session.proxies = {
            "http":f"http://{proxy}",
            "https":f"http://{proxy}"
        }
    for token in tokens:
        get = session.get(f"https://discord.com/api/v9/invites/{invite}?inputValue={invite}&with_counts=true&with_expiration=true")
        if get.status_code == 200:
            
            guild = get.json()["guild"]['id']
            channel = get.json()["channel"]['id']

            sessionID = GetSessionID(token)
            print(" Grabbed Session ID : ",sessionID)
            jwtMaded = makeJWT(guild,channel)
            headers = {
                "Authority": "discord.com",
                "Accept": "*/*",
                "Authorization": token,
                "Cookie": "__dcfduid=f79a8b70f86511eea3ac5543e51156ec; __sdcfduid=f79a8b71f86511eea3ac5543e51156ec4a8a17ce9dab680fdf43763805212efc87fb1ce0dc8f1f297dc4c9b42d699765; _ga=GA1.1.1933564394.1712943226; OptanonConsent=isIABGlobal=false&datestamp=Fri+Apr+12+2024+19%3A33%3A47+GMT%2B0200+(Eastern+European+Standard+Time)&version=6.33.0&hosts=; _ga_YL03HBJY7E=GS1.1.1712943225.1.0.1712943232.0.0.0; _ga_5CWMJQ1S0X=GS1.1.1712957577.2.0.1712957577.0.0.0; __cfruid=9d8247042f51c8e3f87ad23406df0c5188426e70-1715019047; _cfuvid=.cEUQRcCnqdisFzvLoXINyVieT7jpvdCQjSibBbxaNc-1715019047584-0.0.1.1-604800000; cf_clearance=atXQAnjsUsc.bL9PHSmFkHGQnsYr8MSFuqHl36cwnVY-1715019201-1.0.1.1-DWJsXrcVBznvxDETLtKVnqDKMQ7n5X4BNxrrSn8VemLYDfKiPCpMCnbHOncxMR6wDhHSfLMFphGGU41_GL2pKw; locale=en-US",
                "Origin": "https://discord.com",
                "Priority": "u=1, i",
                "Referer": "https://discord.com/channels/@me",
                "Sec-Ch-Ua": "\"Chromium\";v=\"124\", \"Google Chrome\";v=\"124\", \"Not-A.Brand\";v=\"99\"",
                "Sec-Ch-Ua-Mobile": "?0",
                "Sec-Ch-Ua-Platform": "\"Windows\"",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "X-Context-Properties": jwtMaded,
                "X-Debug-Options": "bugReporterEnabled",
                "X-Discord-Locale": "en-US",
                "X-Discord-Timezone": "Africa/Cairo",
                "X-Super-Properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzEyNC4wLjAuMCBTYWZhcmkvNTM3LjM2IiwiYnJvd3Nlcl92ZXJzaW9uIjoiMTI0LjAuMC4wIiwib3NfdmVyc2lvbiI6IjEwIiwicmVmZXJyZXIiOiJodHRwczovL2Rpc2NvcmQuY29tL2NoYW5uZWxzL0BtZSIsInJlZmVycmluZ19kb21haW4iOiJkaXNjb3JkLmNvbSIsInJlZmVycmVyX2N1cnJlbnQiOiIiLCJyZWZlcnJpbmdfZG9tYWluX2N1cnJlbnQiOiIiLCJyZWxlYXNlX2NoYW5uZWwiOiJzdGFibGUiLCJjbGllbnRfYnVpbGRfbnVtYmVyIjoyOTA4MTAsImNsaWVudF9ldmVudF9zb3VyY2UiOm51bGwsImRlc2lnbl9pZCI6MH0="
            }
            join = session.post(f"https://discord.com/api/v9/invites/{invite}",headers=headers,json={
                "session_id":sessionID
            })
            if join.status_code == 200:
                print(" Successfully Joined . ")

            elif "captcha_rqdata" in join.text:
                print(" Captcha Required , Solving in progress.")
                r = join.json()
                rqdata = r['captcha_rqdata']
                capkey = solveCaptcha(rqdata)
                

                headers['X-Captcha-Key']: capkey
                headers['X-Captcha-Rqtoken']: r['captcha_rqtoken']


                response2 = session.post(f"https://discord.com/api/v9/invites/{invite}",json={"session_id":sessionID
                },headers=headers)
                if response2.status_code != 200 : 
                    print(' Joining failed after solving captcha, with status code : ',{response2.status_code})
                else:
                    print(" Successfully Joined , With captcha . ",response2.text)
            elif join.status_code == 429:
                print(" RateLimited !")
            else:
                print(f" Failed : {join.text}")
        else:
            print(" Invalid Invite.")


def main_concurrent(tokens, invite):
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(main, [token], invite) for token in tokens]

        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()  
            except Exception as e:
                print(f" An error occurred: {e}")


if __name__ == "__main__":
    invite = input(" Enter Invite Link without the dis.gg :  ")
    with open('./tokens.txt', 'r') as f:
        tokens = f.read().splitlines()

    main_concurrent(tokens, invite)