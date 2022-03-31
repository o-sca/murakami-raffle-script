import time
import requests
import queue
import threading
import asyncio
import scripts.tools as tools


class Murakami(tools.Tools):
    def __init__(self, task, email=None):    
        super().__init__()
        self.email = f'{self.random_email()}@{task["domain"]}' if email == None else email
        self.capM = task["captcha_keys"]['capmonster']
        q.put(self)
        t = threading.Thread(target = self.run)
        t.start()


    def run(self):
        asyncio.run(self.init())


    async def init(self):
        self.proxy = self.get_proxy()
        self.session = requests.Session()
        self.update_status('Session created')
        self.fetch_csrf_token()
        self.send_captcha()
        self.get_captcha_answer()
        self.register_account()


    def fetch_csrf_token(self):
        if self.check_task_status(): return
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sc-ch-ua-platform": '"macOS"',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36"
        }
        try:
            self.update_status('Fetching auth token')
            response = self.session.get('https://murakamiflowers.kaikaikiki.com/register/new', headers = headers, proxies = self.proxy)
            if response.status_code != 200:
                raise Exception(response.status_code)
            self.csrf_token = response.text.split('csrf-token" content="')[1].split('"')[0]
            return
        except Exception as e:
            self.update_status(e, 2)
            self.session.cookies.clear()
            self.proxy = self.get_proxy()
            return self.fetch_csrf_token()


    def send_captcha(self):
        if self.check_task_status(): return
        params = {
            "clientKey": self.capM,
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
            if "taskId" in response.text:
                self.taskId = response.json().get('taskId')
                return True
        except:
            self.update_status(response.json())
            return


    def get_captcha_answer(self, count = 0):
        if self.check_task_status(): return
        params = {
            "clientKey": self.capM,
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


    def register_account(self):
        global success, failed
        if self.check_task_status(): return
        params = {
            "authenticity_token": self.csrf_token,
            "t": "new",
            "email": self.email,
            "g-recaptcha-response": self.captcha_answer,
            "commit": "SEND+REGISTRATION+MAIL"
        }
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sc-ch-ua-platform": '"macOS"',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "Origin": "https://murakamiflowers.kaikaikiki.com",
            "Content-Length": "693",
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": "https://murakamiflowers.kaikaikiki.com/register/new",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36"
        }
        try:
            self.update_status('Submitting account', 4)
            response = self.session.post('https://murakamiflowers.kaikaikiki.com/register/new_account', headers = headers, data = params, proxies = self.proxy)
            #self.print_dict(params)
            if 'Thank you for submission.' in response.text:
                self.update_status(f'Account created', 5)
                success += 1
                self.save_counter('success', self.email)
                q.get()
                q.task_done()
                return
            else:
                raise Exception('Error creating account')
        except Exception as e:
            self.update_status(e, 2)
            failed += 1
            self.save_counter('failed', self.email)
            q.get()
            q.task_done()
            return


def main():
    global q, success, failed
    tools.print_logo()
    config_file = tools.open_json('config')
    success, failed = 0, 0
    q = queue.Queue(maxsize = config_file["max_threads"])
    if config_file['email_type'].lower() == 'raffle':
        with open('./emails.txt', 'r') as file:
            emails = file.read().split('\n')
            amount = len(emails)
            domain = False
        for email in emails:
            Murakami(config_file, email)
        q.join()
    elif config_file['email_type'].lower() == 'catchall':   
        amount = config_file['gen_amount']
        domain = config_file['domain']
        for _ in range(amount):
            Murakami(config_file)
        q.join()
    else:
        print('Invalid value in "email_type".')
        return
    print("All tasks completed")
    print(f"Amount: {amount} | Success: {success} | Failed: {failed}")
    discord_object = {
        "email_type": config_file['email_type'],
        "domain": domain,
        "amount": amount,
        "success": success,
        "failed": failed,
        "webhook": config_file['webhook']
    }
    tools.send_webhook(discord_object)