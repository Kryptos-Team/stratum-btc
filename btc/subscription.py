from stratum.pubsub import Pubsub, Subscription
from btc.interfaces import Interfaces

import logzero
from logzero import logger


class MiningSubscription(Subscription):
    """This subscription object implements logic for broadcasting new jobs
        to the clients
    """
    event = "mining.notify"

    @classmethod
    def on_template(cls, is_new_block):
        """This is called when TemplateRegistry registers new block which
            we have to broadcast clients
        """
        start = Interfaces.timestamper.time()

        clean_jobs = is_new_block
        job_id, previous_hash, coinb1, coinb2, merkle_branch, version, nbits, ntime, _ = Interfaces.template_registry.get_last_broadcasr_args()

        # Push new job to subscribed clients
        cls.emit(job_id, previous_hash, coinb1, coinb2, merkle_branch, version, nbits, ntime, clean_jobs)

        cnt = Pubsub.get_subscription_count(cls.event)
        logger.info(f"Broadcasted to {cnt} connections in {Interfaces.timestamper.time() - start} seconds")

    def _finish_after_subscribe(self, result):
        """Send new job to newly subscribed client"""
        try:
            job_id, previous_hash, coinb1, coinb2, merkle_branch, version, nbits, ntime = Interfaces.template_registry.get_last_broadcasr_args()
        except Exception:
            logger.error("Template not ready yet")
            return result

        # Force set higher difficulty
        self.connection_ref().rpc("mining.set_difficulty", [2, ], is_notification=True)
        self.connection_ref().rpc("client.get_version", [])

        # Force client to remove previous jobs if any eg from previous connection
        clean_jobs = True
        self.emit_single(job_id, previous_hash, coinb1, coinb2, merkle_branch, version, nbits, ntime, True)

        return result

    def after_subscribe(self, *args, **kwargs):
        """This will send new job to the client *after* he receive subscription details
            on_finish callback solve the issue that job is broadcasted *during* the
            subscription request and client receive messages in wrong order
        """
        self.connection_ref().on_finish.addCallback(self._finish_after_subscribe)
