import logging
import unittest

import logaugment

from mconf_aggr.aggregator.aggregator import Channel


class TestChannel(unittest.TestCase):
    def setUp(self):
        logger = logging.getLogger("test_channel")
        logaugment.set(
            logger, code="", site="TestChannel", server="", event="", keywords="null"
        )
        self.channel = Channel("test_channel", maxsize=5, logger=logger)

    def test_publish(self):
        self.channel.publish(1)
        self.assertEqual(self.channel.pop(), 1)

        self.channel.publish(2)
        self.channel.publish(3)
        self.assertEqual(self.channel.pop(), 2)
        self.assertEqual(self.channel.pop(), 3)

        self.channel.publish(4)
        self.assertEqual(self.channel.pop(), 4)

        self.channel.publish(5)
        self.assertEqual(self.channel.pop(), 5)

    def test_qsize(self):
        for i in range(5):
            self.channel.publish(i)

        self.assertEqual(self.channel.qsize(), 5)

    def test_empty(self):
        self.assertTrue(self.channel.empty())

    def test_full(self):
        for i in range(5):
            self.channel.publish(i)

        self.assertTrue(self.channel.full())

    def test_size_after(self):
        self.channel.publish(1)
        self.assertEqual(self.channel.pop(), 1)

        self.channel.publish(2)
        self.channel.publish(3)
        self.assertEqual(self.channel.pop(), 2)

        self.assertEqual(self.channel.qsize(), 1)

    def test_empty_after(self):
        self.channel.publish(1)
        self.channel.pop()

        self.channel.publish(2)
        self.channel.publish(3)
        self.channel.pop()
        self.channel.pop()

        self.assertTrue(self.channel.empty())

    def test_log_unwritten(self):
        # Enable log generation. It is disabled by tests.py by default.
        logging.disable(logging.NOTSET)

        self.channel.publish(1)
        with self.assertLogs(self.channel.logger, level="DEBUG") as cm:
            self.channel.close()
        self.assertIn(
            "WARNING:test_channel:There are data not consumed in channel {}.".format(
                self.channel.name
            ),
            cm.output,
        )

        # Disable log generation again.
        logging.disable(logging.CRITICAL)
