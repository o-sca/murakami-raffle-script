from datetime import datetime
from colorama import Fore
import time
import json
import random
import string
import requests


class Tools():
    def __init__(self):
        self.task_stopped = False


    def check_task_status(self):
        if self.task_stopped: return True
        return False


    def update_status(self, status, status_colour = 1):
        task_status = f"[{datetime.now()}] {status}"
        match status_colour:
            case 1: # Normal
                return print(f"{Fore.WHITE}{task_status}")
            
            case 2: # Error
                return print(f"{Fore.LIGHTRED_EX}{task_status}")
            
            case 3: # Warning
                return print(f"{Fore.LIGHTCYAN_EX}{task_status}")
            
            case 4: # Processing
                return print(f"{Fore.LIGHTYELLOW_EX}{task_status}")
            
            case 5: # Success
                return print(f"{Fore.LIGHTGREEN_EX}{task_status}")


    def print_dict(self, object):
        json_object = json.dumps(object, indent = 4)
        print(json_object)


    def random_string(self, length):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


    def random_email(self):
        return f"{self.random_name('fname')}_{self.random_name('lname')}{self.random_string(6)}"


    def random_name(self, name_type):
        with open(f'./scripts/names/{name_type}.txt') as name_file:
            names = name_file.read().split('\n')
        return random.choice(names)


    def save_counter(self, file_name, account):
        with open(f'./{file_name}.txt', 'a') as f:
            f.write(account + '\n')


    def get_proxy(self):
        with open('./proxies.txt') as file:
            proxy_list = file.read().split('\n')
        
        if proxy_list == '':
            return 'localhost'

        proxy = random.choice(proxy_list)
        
        match (len(proxy.split(':'))):
            case 2:
                return {
                    'https' : f'https://{proxy}',
                    'http' : f'http://{proxy}' 
                }
            
            case 4:
                split_proxy = proxy.split(':')
                return {
                    'https' : f"http://{split_proxy[2]}:{split_proxy[3]}@{split_proxy[0]}:{split_proxy[1]}"
                }


    def send_captcha(self):
        if self.check_task_status(): return
        params = {
            "clientKey": self.capKey,
            "task":
                {
                    "type":"NoCaptchaTaskProxyless",
                    "websiteURL":"https://murakamiflowers.kaikaikiki.com/",
                    "websiteKey":"6LeoiQ4eAAAAAH6gsk9b7Xh7puuGd0KyfrI-RHQY"
                }
        }
        try: 
            self.update_status('Fetching captcha')
            response = self.session.post("https://api.capmonster.cloud/createTask", json = params)
            if "taskId" not in response.text:
                raise Exception(response.json())
            self.taskId = response.json().get('taskId')
            return
        except Exception as e:
            self.update_status(e)
            self.task_stopped = True
            return


    def get_captcha_answer(self, count = 0):
        if self.check_task_status(): return
        params = {
            "clientKey": self.capKey,
            "taskId": self.taskId
        }
        try:
            self.update_status(f'Solving captcha [{count}]', 3)
            response = requests.post('https://api.capmonster.cloud/getTaskResult', json = params)
            if response.json().get('errorId') != 0:
                raise Exception(response.json().get('errorCode'))
            if response.json().get('status') == 'processing':
                count += 1
                time.sleep(5)
                return self.get_captcha_answer(count)
            data = response.json()
            self.captcha_answer = data['solution']['gRecaptchaResponse']
            return
        except Exception as e: 
            self.update_status(e, 2)


def print_logo():
        print(f"""{Fore.GREEN}

   _   __ _ __ ___    _   _     _   _   __ __
  / \,' //// // o | .' \ / //7.' \ / \,' // /
 / \,' // U //  ,' / o //  ,'/ o // \,' // / 
/_/ /_/ \_,'/_/`_\/_n_//_/\\/_n_//_/ /_//_/  
                                             
   ___    _   ____ ____ __   ___             
  / o | .' \ / __// __// /  / _/             
 /  ,' / o // _/ / _/ / /_ / _/              
/_/`_\/_n_//_/  /_/  /___//___/              
                                             

            
        """)


def open_json(file_name):
    with open(f'./{file_name}.json') as file:
        data = json.load(file)
    return data


def open_txt(file_name):
    with open(f'./{file_name}.txt', 'r') as file:
        data = file.read().split('\n')
    return data


def send_webhook(discord_object):
        data = {
            "username": "oscar's murakami raffle script"
        }
        data["embeds"] = [
                {
                    "title" : "✅ Task Finished",
                    "timestamp": f"{str(datetime.utcnow())}",
                    "footer": {
                        "icon_url": "https://cdn.discordapp.com/attachments/884303450911961088/889703287694172200/WhatsApp_Image_2021-09-20_at_7.34.26_PM.jpeg",
                        "text": "oscar's murakami raffle script"
                    },
                    "fields": [
                        {
                            "name": "Email Type",
                            "value": f"```{discord_object['email_type']}```",
                            "inline": True
                        },
                        {
                            "name": "Domain",
                            "value": f"```{discord_object['domain']}```",
                            "inline": True
                        },
                        {
                            "name": "Amount",
                            "value": f"```{discord_object['amount']}```",
                            "inline": False
                        },
                        {
                            "name": "Success",
                            "value": f"```{discord_object['success']}```",
                            "inline": True
                        },
                        {
                            "name": "Failed",
                            "value": f"```{discord_object['failed']}```",
                            "inline": True
                        }            
                    ]
                    
                }
            ]
        try:
            if discord_object['webhook'] == "": raise Exception('No webhook value')
            response = requests.post(discord_object['webhook'], json = data)   
            if response.status_code == 429 and response.json().get('message') == 'You are being rate limited.':
                time.sleep(response.json().get('retry_after'))
                return send_webhook(discord_object)
        except Exception as e: return print(e)