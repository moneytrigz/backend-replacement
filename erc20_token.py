from config import HTTP_PROVIDER_URL
from decimal import Decimal
import json
from web3 import Web3, HTTPProvider

class ERC20Token:
    cache = {}

    def __init__(self, addr):
        if not ERC20Token.cache:
            with open("tokens.json") as f:
                ERC20Token.cache = dict([(t["addr"].lower(), t["decimals"])
                                            for t in json.load(f)])

        if isinstance(addr, bytes):
            addr = Web3.toHex(addr)
        self.addr = addr.lower()

    def normalize_value(self, value):
        if not isinstance(value, Decimal):
            value = Decimal(value)
        return value * Decimal(10 ** self.decimals)

    def denormalize_value(self, value):
        if not isinstance(value, Decimal):
            value = Decimal(value)
        return value * Decimal(10.0 ** -self.decimals)

    @property
    def decimals(self):
        cache = ERC20Token.cache

        if self.addr == "0x0000000000000000000000000000000000000000":
            return 18 # Not an actual ERC20 token
        elif self.addr not in cache:
            cache[self.addr] = self._call_decimals()

        return cache[self.addr]

    def _call_decimals(self):
        web3 = Web3(HTTPProvider(HTTP_PROVIDER_URL))
        method_hex = Web3.sha3(text="decimals()")[:10]
        retval = web3.eth.call({ "to": self.addr, "data": method_hex })
        if len(retval) != 66:
            error_msg = "Contract {} does not support method".format(self.addr) + \
                "`decimals()', returned '{}'".format(retval)
            raise ValueError(error_msg)
        return Web3.toInt(hexstr=retval)
