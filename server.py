from twisted.internet import defer
from btc import setup
from btc.interfaces import Interfaces, WorkerManagerInterface, TimestamperInterface, ShareLimiterInterface, \
    ShareManagerInterface

# Run when mining service is ready
on_startup = defer.Deferred()

Interfaces.set_share_manager(ShareManagerInterface())
Interfaces.set_share_limiter(ShareLimiterInterface())
Interfaces.set_worker_manager(WorkerManagerInterface())
Interfaces.set_timestamper(TimestamperInterface())

setup(on_startup)
