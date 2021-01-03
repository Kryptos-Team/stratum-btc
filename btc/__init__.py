from twisted.internet import defer
import time
from logzero import logger
from stratum.rpc import Rpc
from .service import MiningService
from .subscription import MiningSubscription
from .address import BitcoinAddress


@defer.inlineCallbacks
def setup(on_startup):
    from .interfaces import Interfaces

    # Let's wait until share manager and worker manager boot up
    (yield Interfaces.share_manager.on_load)
    (yield Interfaces.worker_manager.on_load)

    bitcoin_rpc = Rpc(url="http://localhost")

    logger.info("Waiting for bitcoin rpc")

    while True:
        network_info = (yield bitcoin_rpc.getnetworkinfo())
        if isinstance(network_info, dict):
            break
        else:
            logger.warning("sleeping...")
            time.sleep(1)

    pool_address = BitcoinAddress(rpc=bitcoin_rpc, address="xxx")
    (yield pool_address.on_load)

    on_startup.callback(True)
