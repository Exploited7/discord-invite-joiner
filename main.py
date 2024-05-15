import websocket
import json
import jwt
import concurrent.futures
from colorama import Fore, init
init()
import httpx

import requests
proxy = "" #FILL THIS  USER:PASS@IP:PORT ( WE ARE USING PROXIES TO AVOID RATE LIMIT )
api_key = "" # FCAP API KEY 


print(f'''{Fore.RESET}
{Fore.LIGHTBLUE_EX}


                ░░░░░██╗░█████╗░██╗███╗░░██╗███████╗██████╗░
                ░░░░░██║██╔══██╗██║████╗░██║██╔════╝██╔══██╗
                ░░░░░██║██║░░██║██║██╔██╗██║█████╗░░██████╔╝
                ██╗░░██║██║░░██║██║██║╚████║██╔══╝░░██╔══██╗
                ╚█████╔╝╚█████╔╝██║██║░╚███║███████╗██║░░██║
                ░╚════╝░░╚════╝░╚═╝╚═╝░░╚══╝╚══════╝╚═╝░░╚═╝
                github.com/Exploited7/discord-invite-joiner
''')




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

            result = requests.post("https://api.fcaptcha.lol/api/createTask", headers=headers, json=payload)
            task_id = result.json()["task"]["task_id"]
            payload = {"task_id": task_id}
            while True:
                result = requests.get(f"https://api.fcaptcha.lol/api/getTaskData", headers=headers, json=payload)
                data = result.json()
                if data["task"]["state"] == "processing":
                    continue
               
                capkey = data["task"]["captcha_key"]
                return capkey
        except Exception as e:
            print(f"Failed to solve -> {e}")                                
def makeJWT(guildID,channel):

    header = {
    "location": "Invite Button Embed",
    "location_guild_id": None,
    "location_channel_id": channel,
    "location_channel_type": 1,
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
def getFingerPrint(proxy):
    try:
        session = httpx.Client(proxies=f'http://{proxy}')

        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
            "Host": "discord.com",
            "sec-ch-ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        }

        resp2 = session.get('https://discord.com/',headers=headers)
        coo = resp2.cookies
        cookies = {
                        '__dcfduid': coo.get('__dcfduid'),
                        '__sdcfduid': coo.get('__sdcfduid'),
                        '__cfruid': coo.get('__cfruid'),
                        'locale': 'en-US',
        }
        
        return cookies
    except Exception as e :
        print(e)
        print("Error in getting FingerPrint , Cookies ")

def main(tokens, invite):
    session = httpx.Client(proxies=f'http://{proxy}')

    for token in tokens:
           for invite in invites:

                import json

                get = session.get(f"https://discord.com/api/v9/invites/{invite}?inputValue={invite}&with_counts=true&with_expiration=true")
                if get.status_code == 200:
                    try:
                        data = get.json()
                        guild = data["guild"]["id"]
                        channel = data["channel"]["id"]
                    except json.JSONDecodeError as e:
                        print(f"Error decoding JSON: {e}")


                    sessionID = GetSessionID(token)
                    print(f"{Fore.RESET}({Fore.LIGHTBLUE_EX}INFO{Fore.RESET}) {Fore.LIGHTYELLOW_EX} Grabbed Session ID : ",sessionID)
                    jwtMaded = makeJWT(guild,channel)
                    data = {
                        "session_id":sessionID
                    }
                    cookies = getFingerPrint(proxy)
                    headers = {
                    "authority": "discord.com",
                        "method": "POST",
                        "path": f"/api/v9/invites/{invite}",
                        "scheme": "https",
                        "Accept": "*/*",
                        "Accept-Encoding": "gzip, deflate, br, zstd",
                        "Accept-Language": "en-US,en;q=0.9",
                        "Authorization": token,
                        "Content-Length": str(len(json.dumps(data))),
                        "Content-Type": "application/json",
                        "Cookie":  '; '.join([f"{k}={v}" for k, v in cookies.items() if v is not None]),
                        "Origin": "https://discord.com",
                        "Priority": "u=1, i",
                        "Referer": "https://discord.com/channels/@me/1239540925538107463",
                        "Sec-Ch-Ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
                        "Sec-Ch-Ua-Mobile": "?0",
                        "Sec-Ch-Ua-Platform": '"Windows"',
                        "Sec-Fetch-Dest": "empty",
                        "Sec-Fetch-Mode": "cors",
                        "Sec-Fetch-Site": "same-origin",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                        "X-Context-Properties": "eyJsb2NhdGlvbiI6Ikludml0ZSBCdXR0b24gRW1iZWQiLCJsb2NhdGlvbl9ndWlsZF9pZCI6bnVsbCwibG9jYXRpb25fY2hhbm5lbF9pZCI6IjEyMzk1NDA5MjU1MzgxMDc0NjMiLCJsb2NhdGlvbl9jaGFubmVsX3R5cGUiOjEsImxvY2F0aW9uX21lc3NhZ2VfaWQiOiIxMjQwMDgyMDM5NDU4MzY5NTk4In0=",
                        "X-Debug-Options": "bugReporterEnabled",
                        "X-Discord-Locale": "en-GB",
                        "X-Discord-Timezone": "Africa/Cairo",
                        "X-Super-Properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzEyNC4wLjAuMCBTYWZhcmkvNTM3LjM2IiwiYnJvd3Nlcl92ZXJzaW9uIjoiMTI0LjAuMC4wIiwib3NfdmVyc2lvbiI6IjEwIiwicmVmZXJyZXIiOiJodHRwczovL2Rpc2NvcmQuY29tL2NoYW5uZWxzL0BtZSIsInJlZmVycmluZ19kb21haW4iOiJkaXNjb3JkLmNvbSIsInJlZmVycmVyX2N1cnJlbnQiOiIiLCJyZWZlcnJpbmdfZG9tYWluX2N1cnJlbnQiOiIiLCJyZWxlYXNlX2NoYW5uZWwiOiJzdGFibGUiLCJjbGllbnRfYnVpbGRfbnVtYmVyIjoyOTMzNjIsImNsaWVudF9ldmVudF9zb3VyY2UiOm51bGwsImRlc2lnbl9pZCI6MH0="
                        }
                    join = session.post(f"https://discord.com/api/v9/invites/{invite}",headers=headers,json=data)
                    if join.status_code == 200:
                        print(f"{Fore.RESET}({Fore.LIGHTGREEN_EX}SUCCESS{Fore.RESET}) {Fore.LIGHTYELLOW_EX} Joined . ")

                    elif "captcha_rqdata" in join.text:
                        print(f"{Fore.RESET}({Fore.LIGHTRED_EX}CAPTCHA{Fore.RESET}) {Fore.LIGHTYELLOW_EX} Captcha Required , Solving in progress.")
                        r = join.json()
                        rqdata = r['captcha_rqdata']
                        capkey = solveCaptcha(rqdata)
                        

                    
                        headers = {
                    "authority": "discord.com",
                        "method": "POST",
                        "path": "/api/v9/invites/K4jkdZzu",
                        "scheme": "https",
                        "Accept": "*/*",
                        "Accept-Encoding": "gzip, deflate, br, zstd",
                        "Accept-Language": "en-US,en;q=0.9",
                        "Authorization": token,
                        "Content-Length": str(len(json.dumps(data))),
                        "Content-Type": "application/json",
                        "Cookie":  '; '.join([f"{k}={v}" for k, v in cookies.items() if v is not None]),
                        "Origin": "https://discord.com",
                        "Priority": "u=1, i",
                        "Referer": "https://discord.com/channels/@me/1239540925538107463",
                        "Sec-Ch-Ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
                        "Sec-Ch-Ua-Mobile": "?0",
                        "Sec-Ch-Ua-Platform": '"Windows"',
                        "Sec-Fetch-Dest": "empty",
                        "Sec-Fetch-Mode": "cors",
                        "Sec-Fetch-Site": "same-origin",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                        "X-Context-Properties": "eyJsb2NhdGlvbiI6Ikludml0ZSBCdXR0b24gRW1iZWQiLCJsb2NhdGlvbl9ndWlsZF9pZCI6bnVsbCwibG9jYXRpb25fY2hhbm5lbF9pZCI6IjEyMzk1NDA5MjU1MzgxMDc0NjMiLCJsb2NhdGlvbl9jaGFubmVsX3R5cGUiOjEsImxvY2F0aW9uX21lc3NhZ2VfaWQiOiIxMjQwMDgyMDM5NDU4MzY5NTk4In0=",
                        "X-Debug-Options": "bugReporterEnabled",
                        "X-Discord-Locale": "en-GB",
                        "X-Discord-Timezone": "Africa/Cairo",
                        "X-Captcha-Key":capkey,
                        "X-Captcha-Rqtoken":r['captcha_rqtoken'],
                        "X-Super-Properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzEyNC4wLjAuMCBTYWZhcmkvNTM3LjM2IiwiYnJvd3Nlcl92ZXJzaW9uIjoiMTI0LjAuMC4wIiwib3NfdmVyc2lvbiI6IjEwIiwicmVmZXJyZXIiOiJodHRwczovL2Rpc2NvcmQuY29tL2NoYW5uZWxzL0BtZSIsInJlZmVycmluZ19kb21haW4iOiJkaXNjb3JkLmNvbSIsInJlZmVycmVyX2N1cnJlbnQiOiIiLCJyZWZlcnJpbmdfZG9tYWluX2N1cnJlbnQiOiIiLCJyZWxlYXNlX2NoYW5uZWwiOiJzdGFibGUiLCJjbGllbnRfYnVpbGRfbnVtYmVyIjoyOTMzNjIsImNsaWVudF9ldmVudF9zb3VyY2UiOm51bGwsImRlc2lnbl9pZCI6MH0="
                        }

                        response2 = session.post(f"https://discord.com/api/v9/invites/{invite}",json={"session_id":sessionID
                        },headers=headers)
                        if response2.status_code != 200 : 
                            print(F'{Fore.RESET}[{Fore.LIGHTRED_EX}FAILED{Fore.RESET}] {Fore.LIGHTYELLOW_EX} Joining failed after solving captcha, with status code : ',{response2.status_code})
                        else:
                            print(f"{Fore.RESET}({Fore.LIGHTGREEN_EX}SUCCESS{Fore.RESET}) {Fore.LIGHTYELLOW_EX} Joined . ")
                    elif join.status_code == 429:
                        print(" RateLimited !")
                    else:
                        print(f" Failed : {join.text}")
                else:
                    print(" Invalid Invite.")


def main_concurrent(tokens, invite):
    with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
        futures = [executor.submit(main, [token], invite) for token in tokens]

        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()  
            except Exception as e:
                c = None
                # print(f" An error occurred: {e}")




def read_proxies(file_path):
    with open(file_path, 'r') as file:
        invites = file.readlines()
    return [invite.strip() for invite in invites]

invites = read_proxies('invites.txt')
if __name__ == "__main__":
    # invite = input(f"{Fore.RESET}[{Fore.LIGHTBLUE_EX}INFO{Fore.RESET}] Enter Invite Link without the dis.gg :  ")
    with open('./tokens.txt', 'r') as f:
        tokens = f.read().splitlines()

    main_concurrent(tokens, invites)
