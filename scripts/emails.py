from imap_tools import MailBox, A
from scripts import tools


class Emails(tools.Tools):
    def __init__(self, task):
        super().__init__()
        self.domain = task['mail_domain']
        self.folder = task['email_folder_to_search'].upper()
        self.limit = task['amount_of_emails_to_check']
        self.email = task['login']['email']
        self.password = task['login']['password']
    

    def run(self):
        self.login()
        self.fetch_links()
        self.logout()


    def login(self):
        if self.check_task_status(): return
        self.update_status(f'Logging into {self.email}')
        try:
            self.email_init = MailBox(f'imap.{self.domain}.com')
            self.email_init.login(self.email, self.password, self.folder)
            self.update_status('Logged in successfully')
            return
        except Exception as e:
            self.update_status(f'Failed to log in: {e}', 2)
            self.task_stopped = True
            return


    def logout(self):
        if self.check_task_status(): return
        self.update_status('Logging out')
        self.email_init.logout()
        return

    
    def save_to_txt(self, link):
        with open('./emails.txt', 'a') as file:
            file.write(f'{link}\n')


    def fetch_links(self):
        global success
        for mail in self.email_init.fetch(criteria = A(from_ = 'tonari-no-news@kaikaikiki.co.jp'), reverse = True, mark_seen = True, limit = self.limit, bulk = True):
            activation_id = mail.text.split('https://murakamiflowers.kaikaikiki.com/register/register?')[1].split('\n')[0]
            self.save_to_txt(f'https://murakamiflowers.kaikaikiki.com/register/register?{activation_id}')
            success += 1
            self.update_status(f'Successfully parsed link {success} / {self.limit}')
        return


    def delete_seen(self):
        # Not tested lol
        self.email_init.delete([
            msg.uid for msg in self.email_init.fetch() if msg.flags == '\\Seen' and msg.from_ == 'tonari-no-news@kaikaikiki.co.jp'
        ])


def main():
    global success
    success = 0
    config = tools.open_json('config')
    Emails(config).run()
    print('Task Completed')
    print(f'Amount: {config["amount_of_emails_to_check"]} | Success: {success}')