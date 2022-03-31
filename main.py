import scripts.entries as entry
import scripts.emails as email
import scripts.register as register


def main():
    user_input = int(input('[1] Submit Entries\n[2] Fetch Emails\n[3] Register Wallet\n[4] Exit\n\n'))
    match user_input:
        case 1:
            entry.main()
            return
        case 2:
            email.main()
            return
        case 3:
            register.main()
        case 4:
            return


if __name__ == "__main__":
    main()