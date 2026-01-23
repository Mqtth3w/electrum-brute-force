'''
@author Mqtth3w https://github.com/mqtth3w
@license GPL-3.0
'''

import os
import hmac
import hashlib

with open("english.txt", encoding="utf-8") as f:
    WORDLIST = [w.strip() for w in f if w.strip()]

N = 2048

SEED_PREFIXES = {
    "standard": "01",
    "segwit": "100",
}

def mnemonic_encode(data: bytes):
    """Encode bytes into Electrum mnemonic (base-2048)."""
    num = int.from_bytes(data, "big")
    words = []
    while num:
        num, idx = divmod(num, N)
        words.append(WORDLIST[idx])
    return " ".join(words)

def seed_version(mnemonic: str) -> str:
    return hmac.new(
        b"Seed version",
        mnemonic.encode(),
        hashlib.sha512
    ).hexdigest()

def generate_electrum_seed(seed_type="segwit", entropy_bytes=16):
    prefix = SEED_PREFIXES[seed_type]
    while True:
        entropy = os.urandom(entropy_bytes)
        mnemonic = mnemonic_encode(entropy)
        if seed_version(mnemonic).startswith(prefix):
            return mnemonic

if __name__ == "__main__":
    for _ in range(100):
        print(generate_electrum_seed("segwit"), end="\n\n")

