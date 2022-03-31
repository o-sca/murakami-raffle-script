import time
import requests
import queue
import threading
import asyncio
import scripts.tools as tools


class Register(tools.Tools):
    def __init__(self, task):    
        super().__init__()
        self.capM = task['key']
        self.link = task['link']
        self.wallet = task['wallet']
        self.fname = self.random_name('fname')
        self.password = self.random_string(16)
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
        self.register_wallet()


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
            response = self.session.get(self.link, headers = headers, proxies = self.proxy)
            if response.status_code != 200:
                raise Exception(response.status_code)
            self.csrf_token = response.text.split('authenticity_token" value="')[1].split('"')[0]
            self.email = response.text.split('Email</span></div><div class="p-accountForm__itemContent"><input readonly="readonly" type="text" value="')[1].split('"')[0]
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


    def register_wallet(self):
        global success, failed
        if self.check_task_status(): return
        params = {
            "authenticity_token": self.csrf_token,
            "user[email]": self.email,
            "user[name]": self.fname,
            "user[metamask_wallet_address]": self.wallet,
            "user[password]": self.password,
            "user[password_confirmation]": self.password,
            "g-recaptcha-response": self.captcha_answer,
            "t": self.link.split('t=')[1].split('&u')[0],
            "u": self.link.split('u=')[1],
            "commit":"Confirm"
        }
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en-CA;q=0.9,en-GB;q=0.8,en;q=0.7",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded",
            "Dnt": "1",
            "Origin": "https://murakamiflowers.kaikaikiki.com",
            "Referer": self.link,
            "Sec-Ch-Ua": "'Not A;Brand';v='99', 'Chromium';v='99', 'Google Chrome';v='99'",
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36"
        }
        try:
            self.update_status('Submitting wallet', 4)
            #self.print_dict(params)
            response = self.session.post('https://murakamiflowers.kaikaikiki.com/register/register', data = params, headers = headers, proxies = self.proxy)
            if response.status_code != 200:
                print(response.status_code)
                raise Exception(response.text)
            if 'Thank you for your registering.' in response.text:
                self.update_status('Wallet submitted', 5)
                success += 1
            q.get()
            q.task_done()
            return
        except Exception as e:
            self.update_status(e, 2)
            failed += 1
            q.get()
            q.task_done()
            return


def main():
    global q, success, failed
    tools.print_logo()
    wallets = tools.open_json('wallets')
    emails = tools.open_txt('emails')
    if len(wallets) != len(emails):
        print('Incorrect ratio of emails to wallets')
        print(f"Wallets: {len(wallets)} || Emails: {len(emails)}")
        return
    config_file = tools.open_json('config')
    success, failed = 0, 0
    q = queue.Queue(maxsize = config_file["max_threads"])

    for index in range(len(emails)):
        config_object = {
            "key": config_file['captcha_keys']['capmonster'],
            "link": emails[index],
            "wallet": wallets[index]["address"],
            "webhook": config_file['webhook']
        }
        Register(config_object)
    q.join()
    print("All tasks completed")
    print(f"Amount: {len(wallets)} | Success: {success} | Failed: {failed}")  
    discord_object = {
        "email_type": "Wallet Submission",
        "domain": "_ _",
        "amount": len(wallets),
        "success": success,
        "failed": failed,
        "webhook": config_file['webhook']
    }
    tools.send_webhook(discord_object)