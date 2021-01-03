from .rpc import BitcoinRPC
from .service import MiningService
from .subscription import MiningSubscription
from twisted.internet import defer
import time


@defer.inlineCallbacks
def setup(on_startup):
    from .interfaces import Interfaces

    # Let's wait until share manager and worker manager boot up
    (yield Interfaces.share_manager.on_load)
    (yield Interfaces.worker_manager.on_load)

    bitcoin_rpc = BitcoinRPC(host="18.179.58.207", port=18444, username="kryptos", password="x")

    on_startup.callback(True)
