"""This module contains classes used by pool core to interact wiht thr rest of the
    pool. Default implementation does nothing here
"""

import time
from twisted.internet import reactor, defer
import logzero
from logzero import logger


class WorkerManagerInterface(object):
    def __init__(self):
        # Fire deferred when manager is ready
        self.on_load = defer.Deferred()
        self.on_load.callback(True)

    def authorize(self, worker_name, worker_password):
        return True


class ShareLimiterInterface(object):
    """Implement difficulty adjustments here"""

    def submit(self, connection_ref, current_difficulty, timestamp):
        """
        :param connection_ref: weak reference to Protocol interface
        :param current_difficulty: difficulty of the connection
        :param timestamp: submission time of current share
        """
        pass


class ShareManagerInterface(object):
    def __init__(self):
        # Fire deferred when manager is ready
        self.on_load = defer.Deferred()
        self.on_load.callback(True)

    def on_network_block(self, previous_hash):
        """Prints when there is new blocking coming from the network"""
        pass

    def on_submit_share(self, worker_name, block_header, block_hash, timestamp, is_valid):
        logger.info(f"{block_hash} {'valid' if is_valid else 'invalid'} {worker_name}")

    def on_submit_block(self, is_accepted, worker_name, block_header, block_hash, timestamp):
        logger.info(f"Block {block_hash} {'accepted' if is_accepted else 'rejected'}")


class TimestamperInterface(object):
    """This is the only source for current time in the application"""

    def time(self):
        return time.time()


class PredictableTimestamperInterface(TimestamperInterface):
    """Predictable timestamper may be useful for unit testing"""
    start_time = 1345678900
    delta = 0

    def time(self):
        self.delta += 1
        return self.start_time + self.delta


class Interfaces(object):
    worker_manager = None
    share_manager = None
    share_limiter = None
    timestamper = None
    template_registry = None

    @classmethod
    def set_worker_manager(cls, manager):
        cls.worker_manager = manager

    @classmethod
    def set_share_manager(cls, manager):
        cls.share_manager = manager

    @classmethod
    def set_share_limiter(cls, limiter):
        cls.share_limiter = limiter

    @classmethod
    def set_timestamper(cls, manager):
        cls.timestamper = manager

    @classmethod
    def set_template_registry(cls, registry):
        cls.template_registry = registry
