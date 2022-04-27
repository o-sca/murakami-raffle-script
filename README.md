# Murakami Raffle Script

## Requirements

### Python Dependencies
```
requests==2.27.1
colorama==0.4.4
imap-tools==0.53.0
```

### NodeJS Dependencies
```
Web3
```

## Running The Script
**Generating Wallets**

`node create_wallet/index.js`

_The amount value of wallets generated are parsed from the config.json "gen_amount" value._


**Running The Main Script**

`python3 / python main.py`

_You will be given a simple CLI user input prompt with 4 choices to choose from_


![image](https://user-images.githubusercontent.com/97479266/165455832-8ec66158-f34b-4bbb-b9e7-88a58e1403fe.png)

**[1] Submit Entries**: this will be the script that submits emails to the site

**[2] Fetch Emails**: this will be the script to fetch the activation links from your inbox

**[3] Register Wallet**: this will be the script to submit your wallet to the each activation link fetched from your inbox

**[4] Exit**: exits out the CLI  
