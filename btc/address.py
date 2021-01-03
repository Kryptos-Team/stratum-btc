from twisted.internet import defer
from logzero import logger


class BitcoinAddress(object):
    def __init__(self, rpc, address):
        # Fire callback when ready
        self.on_load = defer.Deferred()

        self.address = address
        # Verify if pool can use this address
        self.is_valid = False
        self.rpc = rpc

        self._validate()

    def _validate(self):
        d = self.rpc.validateaddress(self.address)
        d.addCallback(self._address_check)
        d.addErrback(self._failure)

    def _address_check(self, result):
        if result["isvalid"] and result["ismine"]:
            self.is_valid = True
            logger.info(f"Address {self.address} is valid")

            if not self.on_load.called:
                self.on_load.callback(True)
        else:
            self.is_valid = False
            logger.error(f"Address {self.address} is not valid")

    def _failure(self, failure):
        logger.error(f"Cannot validate address {self.address}")
        raise

    def get_script_pubkey(self):
        if not self.is_valid:
            self._validate()
            raise Exception("Address is not validated")
        return self.address
