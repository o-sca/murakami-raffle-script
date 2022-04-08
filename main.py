import scripts.entries as entry
import scripts.emails as email
import scripts.register as register
import scripts.tools as tools
global success, failed, total
success = 0
failed = 0
total = 0


def get_input():
    tools.print_logo()
    user_input = int(input('[1] Submit Entries\n[2] Fetch Emails\n[3] Register Wallet\n[4] Exit\n\n'))
    config = tools.open_json('config')
    match user_input:
        case 1:
            entry.main(config)
            return
        case 2:
            email.main(config)
            return
        case 3:
            wallets = tools.open_json('wallets')
            links = tools.open_txt('links')
            register.main(config, wallets, links)
            return
        case 4:
            print('Exiting')
            return


def main():
    try:
        get_input()
    except ValueError:
        print('Invalid input')
        main()


if __name__ == "__main__":
    main()