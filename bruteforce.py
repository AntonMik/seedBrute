import binascii
import hashlib
import sys
from typing import List
from web3 import Web3
from itertools import permutations
from random import choices, shuffle
import random
import os
from math import factorial
from multiprocessing import Process, cpu_count, Pool
import time
from datetime import datetime
import os


w3 = Web3()
w3.eth.account.enable_unaudited_hdwallet_features()

if "WEB3_PROVIDER_URI_HTTP" in os.environ:
    w3_connection = Web3(Web3.HTTPProvider(os.environ["WEB3_PROVIDER_URI_HTTP"]))
else:
    w3_connection = Web3(Web3.HTTPProvider("http://192.168.1.4:8545"))

assert w3_connection.isConnected()


address_to_find = "0xC399bd88A3471bfD277966Fef8e5110857e827Fc"

bip39_wordslist = []
wordlist_nums = {}

with open("bip39_wordslist_en.txt") as file:
    i = 0
    for w in file.readlines():
        word = w.strip().decode("utf8") if sys.version < "3" else w.strip()
        bip39_wordslist.append(word)
        wordlist_nums[word] = i
        i += 1


gaurenteed_words_1 = [
    "police",
]


possible_words_1 = list(
    set(
        [
            "gaze",
            "observe",
            "such",
            "very",
            "seek",
            "uniform",
            "appear",
            "picture",
            "injury",
            "photo",
            "detail",
            "quality",
        ]
    )
)

gaurenteed_words_2 = [
    "gossip",
]

possible_words_2 = [
    "woman",
    "girl",
    "young",
    "youth",
    "cute",
    "surprise",
    "speak",
    "chat",
    "canvas",
    "beauty",
    "pretty",
    "talk",
]

gaurenteed_words_3 = ["drum"]

possible_words_3 = [
    "wedding",
    "marriage",
    "arrange",
    "couple",
    "dance",
    "festival",
    "history",
    "ritual",
    "ancient",
]


either_word_4 = ["movie", "game", "cover", "book", "media"]

possible_words_4 = list(
    set(
        [
            "action",
            "actual",
            "because",
            "define",
            "detail",
            "cover",
            "journey",
            "essence",
            "evoke",
            "glare",
            "label",
            "myth",
            "release",
            "style",
            "text",
            "sign",
            "title",
            "unique",
            "way",
            "wisdom",
            "real",
        ]
    )
)

either_word_5 = [
    "flower",
    "color",
    "vivid",
    "bright",
    "wonder",
    "dream",
]
possible_words_5 = [
    "woman",
    "girl",
    "pretty",
    "sister",
    "daughter",
    "beauty",
    "young",
    "youth",
]


gaurenteed_words_6 = ["window"]
possible_words_6 = possible_words_5 = list(
    set(
        [
            "nature",
            "wild",
            "life",
            "season",
            "normal",
            "view",
            "scene",
            "segment",
            "broken",
            "sight",
            "silent",
            "theme",
            "then",
            "there",
            "this",
            "despair",
            "then",
            "hope",
            "engage",
            "day",
            "what",
            "wonder",
            "world",
            "observe",
            "such",
            "very",
        ]
    )
)


def drain_eth(reciever: str, public_key: str, private_key: str):

    balance = w3_connection.eth.get_balance(public_key)
    gas_price = int(w3_connection.eth.gas_price * 1.2)
    cost = 21000 * (gas_price + Web3.toWei(5, "gwei"))

    if balance - cost <= 0:
        raise Exception("No Ether!")

    transaction = {
        "value": balance - cost - 1,
        "to": reciever,
        "gas": 21000,
        "maxFeePerGas": gas_price,
        "maxPriorityFeePerGas": Web3.toWei(5, "gwei"),
        "nonce": w3_connection.eth.getTransactionCount(public_key),
        "chainId": 1,  # Must have chainID if not using registrar
    }
    signed_tx = w3_connection.eth.account.sign_transaction(
        transaction,
        private_key,
    )

    tx_hash = w3_connection.eth.send_raw_transaction(signed_tx.rawTransaction)
    print(tx_hash)


def n_from_k(k: int, n: int):
    return factorial(k) / factorial(k - n)


#
def verify_checksum(wordlist: List[str]):
    N = 0
    for w in wordlist:
        N = (N << 11) + wordlist_nums[w]

    nhex = format(N, "033x")  # include leading zero if needed

    h = hashlib.sha256(binascii.unhexlify(nhex[:-1])).hexdigest()

    return h[0] == nhex[-1]


def find_correct_seed():

    count = 0

    random_seed = (os.getpid() * int(time.time())) % 123456789
    random.seed(random_seed)
    print(f"Random seed: {random_seed}")

    avg_attempts = (
        factorial(2) ** 6  # Pick 6 sets of 2
        # Pick 1 from each set - guaretneed words are accounted for
        * n_from_k(len(possible_words_1), 1)
        * n_from_k(len(possible_words_2), 1)
        * n_from_k(len(possible_words_3), 1)
        * n_from_k(len(either_word_4), 1)
        * n_from_k(len(possible_words_4), 1)
        * n_from_k(len(either_word_5), 1)
        * n_from_k(len(possible_words_5), 1)
        * n_from_k(len(possible_words_6), 1)
    )

    print(f"Expected attempts: {avg_attempts:,}")

    while True:

        count += 1
        if count % 100000 == 0:
            print(f"{count} searched. {datetime.now().isoformat()}")

        # Use RNG to make script easily changeable. Iterating through permutations would be reset with
        # any changes to the wordset

        qtr_1 = gaurenteed_words_1 + choices(possible_words_1, k=1)
        qtr_2 = gaurenteed_words_2 + choices(possible_words_1, k=1)
        qtr_3 = gaurenteed_words_3 + choices(possible_words_3, k=1)
        qtr_4 = choices(either_word_4, k=1) + choices(possible_words_4, k=1)
        qtr_5 = choices(either_word_5, k=1) + choices(possible_words_5, k=1)
        qtr_6 = gaurenteed_words_6 + choices(possible_words_6, k=1)

        shuffle(qtr_1)
        shuffle(qtr_2)
        shuffle(qtr_3)
        shuffle(qtr_4)
        shuffle(qtr_5)
        shuffle(qtr_6)

        perm = qtr_1 + qtr_2 + qtr_3 + qtr_4 + qtr_5 + qtr_6

        if not verify_checksum(perm):
            continue

        perm_str = " ".join(perm)

        account = w3.eth.account.from_mnemonic(
            perm_str, account_path="m/44'/60'/0'/0/0"
        )

        if account.address == address_to_find:

            print(account.address)
            print(account.key.hex())
            print(perm_str)

            drain_eth(
                reciever="YOUR ADDRESS",
                public_key=account.address,
                private_key=account.key.hex(),
            )

            break


def main():
    find_correct_seed()


def main():
    processes = []

    for _ in range(cpu_count() - 2):

        p = Process(target=find_correct_seed)
        p.start()
        processes.append(p)


if __name__ == "__main__":
    main()
