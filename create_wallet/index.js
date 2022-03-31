const Web3 = require('web3');
const fs = require('fs');


const web3 = new Web3("ws://localhost:8545");

var walletArr = []


function readConfig() {
    let file = fs.readFileSync('./config.json')
    return JSON.parse(file)
}


function saveWallets(walletArr) {
    fs.writeFileSync('./wallets.json', JSON.stringify(walletArr))
    console.log(`${walletArr.length} wallet(s) created and stored succesfully`)
    return
}


(async () => {
    let config = readConfig()
    for (i = 0; i < config.gen_amount; i++) {
        let wallet = await web3.eth.accounts.create()
        walletArr.push(wallet)
        console.log(`[${i + 1} / ${config.gen_amount}] || ${wallet.address}`)
    }
    saveWallets(walletArr)
})();