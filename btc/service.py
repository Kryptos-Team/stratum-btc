import binascii
from twisted.internet import defer
from stratum.services import GenericService
from stratum.pubsub import Pubsub
from .interfaces import Interfaces
from .subscription import MiningSubscription
from .exceptions import SubmitException

import logzero
from logzero import logger


class MiningService(GenericService):
    """This service provides public API for stratum mining proxy"""

    service_type = "mining"
    service_vendor = "stratum"
    is_default = True

    def update_block(self):
        """Connect this RPC call to `bitcoind -blocknotify` for instant
            notification about new block on the network.
        """
        logger.info("New block notification received")
        Interfaces.template_registry.update_block()
        return True

    def authorize(self, worker_name, worker_password):
        """Authorize worker on this connection"""
        session = self.connection_ref().get_session()
        session.setdefault("authorized", {})

        if Interfaces.worker_manager.authorize(worker_name, worker_password):
            session["authorized"][worker_name] = worker_password
            return True
        else:
            if worker_name in session["authorized"]:
                del session["authorized"][worker_name]

            return False

    def subscribe(self, *args):
        """Subscribe for receiving mining jobs. This will return subscription
            details, extranonce1_hex and extranonce2_size
        """
        extranonce1 = Interfaces.template_registry.get_new_extranonce1()
        extranonce2_size = Interfaces.template_registry.extranonce2_size
        extranonce1_hex = binascii.hexlify(extranonce1)

        session = self.connection_ref().get_session()
        session["extranonce1"] = extranonce1
        session["difficulty"] = 1

        return Pubsub.subscribe(self.connection_ref(), MiningSubscription()) + (extranonce1_hex, extranonce2_size)

    def submit(self, worker_name, job_id, extranonce2, ntime, nonce):
        """Try to solve block candidate using given parameters"""

        session = self.connection_ref().get_session()
        session.setdefault("authorized", {})

        # Check if worker is authorized to submit shares
        if not Interfaces.worker_manager.authorize(worker_name, session["authorized"].get(worker_name)):
            raise SubmitException("Worker is not authorized")

        # Check if extranonce1 is in connection session
        extranonce1_bin = session.get("extranonce1", None)
        if not extranonce1_bin:
            raise SubmitException("Eonnection is not subscribed for mining")

        difficulty = session["difficulty"]
        submit_time = Interfaces.timestamper.time()

        Interfaces.share_limiter.submit(self.connection_ref, difficulty, submit_time)

        # This checks if submitted share meet all requirements
        # and it is valid proof of work
        try:
            block_header, block_hash, on_submit = Interfaces.template_registry.submit_share(job_id, worker_name,
                                                                                            extranonce1_bin,
                                                                                            extranonce2, ntime, nonce,
                                                                                            difficulty)
        except SubmitException:
            # block header and block_hash are None when submitted data are corrupted
            Interfaces.share_manager.on_submit_share(worker_name, None, None, difficulty, submit_time, False)

            raise SubmitException("block_header and block_hash are None")

        Interfaces.share_manager.on_submit_share(worker_name, block_header, block_hash, difficulty, submit_time, True)

        if on_submit != None:
            # Pool performs submitblock() to bitcoind. Hook this to result and report to share_manager
            on_submit.addCallback(Interfaces.share_manager.on_submit_share, worker_name, block_header, block_hash,
                                  submit_time)

        return True

    # Service documentation for remote discovery
    update_block.help_text = "Notify stratum server about new block on the network"
    update_block.params = [("password", "string", "Administrator password"), ]

    authorize.help_text = "Authorize worker for submitting shares on this connection"
    authorize.params = [("worker_name", "string", "Name of the worker"),
                        ("worker_password", "string", "Worker password")]

    subscribe.help_text = "Subscribes current connection for receiving new mining jobs"
    subscribe.params = []

    submit.help_text = "Submit solved share back to the server. Excessive sending of invalid shares" \
                       "or shares above indicated target may lead to temporary or permanent ban of" \
                       "user, worker or IP address"
    submit.params = [("worker_name", "string", "Name of the worker"),
                     ("job_id", "string", "Job ID received by 'mining.notify'"),
                     ("extranonce2", "string",
                      "hex-encoded big-endian extranonce2, length depends on extranonce2_size from 'mining.notify'"),
                     ("ntime", "string",
                      "UNIX timestamp (32bit integer, big-endian, hex-encoded), must be >= ntime provided by "
                      "mining.notify and <= current time"),
                     ("nonce", "string", "32 bit integer, hex-encoded, big-endian")]
