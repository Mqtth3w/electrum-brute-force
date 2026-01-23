'''
@author Mqtth3w https://github.com/mqtth3w
@license GPL-3.0
'''

import subprocess
import sys
import os
import hmac
import hashlib
import json
import time
from electrum_seed import *

def run(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stderr)
        sys.exit(1)
    return result.stdout.strip()

def create_wallet(wallet_number):
    print("\n\n")
    print("Creating wallet from seed...")
    seed = generate_electrum_seed("segwit")
    print(seed)
    wallet_path = f"/home/mqtth3w/.electrum/wallets/wallet_{wallet_number}"
    run([
        "electrum",
        "restore",
        seed,
        "-w",
        wallet_path
    ])
    print("Wallet created at:", wallet_path)
    return seed, wallet_path

def electrum(info, wallet_path, args):
    print(info)
    result = run([
            "electrum",
            "-w",
            wallet_path
        ] + args)
    return result

def print_balance(cbtc, ubtc):
    green = "\033[92m"
    red = "\033[91m"
    reset = "\033[0m"
    if btc > 0:
        print(f"{green}Confirmed BTC: {cbtc}{reset}")
        print(f"{green}Unconfirmed BTC: {ubtc}{reset}")
    elif btc > 1:
        print(f"{red}Confirmed BTC: {cbtc}{reset}")
        print(f"{red}Unconfirmed BTC: {ubtc}{reset}")
    else:
        print(f"Confirmed BTC: {btc}")

if __name__ == "__main__":
    print("Starting electrum...")
    run([
            "electrum",
            "daemon",
            "-d"
        ])
    for i in range(226, 300):
        seed, wallet = create_wallet(i)
        electrum("Loading wallet...", wallet, ["load_wallet"])
        balance = json.loads(electrum("Getting balance...", wallet, ["getbalance"]))
        confirmed = int(balance["confirmed"]) / 1e8
        unconfirmed = int(balance.get("unconfirmed", 0)) / 1e8
        print_balance(confirmed)
        print_balance(unconfirmed)
        if confirmed + unconfirmed > 0:
            with open("./relevant_seeds.txt", "a", encoding="utf-8") as f:
                f.write(f"\n\n{seed}\nBalance BTC: {confirmed + unconfirmed}")
            time.sleep(10)
    print("Finished, stopping electrum...")
    run([
            "electrum",
            "stop"
        ])
