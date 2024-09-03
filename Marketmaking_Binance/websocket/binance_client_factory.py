# -*- coding: utf-8 -*-
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(os.path.abspath(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))))))

import logging
from autobahn.twisted.websocket import WebSocketClientFactory
from twisted.internet.protocol import ReconnectingClientFactory
from Spot_trading.websocket.binance_client_protocol import BinanceClientProtocol


class BinanceReconnectingClientFactory(ReconnectingClientFactory):
    initialDelay = 0.1
    maxDelay = 50
    maxRetries = 10000


class BinanceClientFactory(WebSocketClientFactory, BinanceReconnectingClientFactory):
    def __init__(self, *args, payload=None, **kwargs):
        WebSocketClientFactory.__init__(self, *args, **kwargs)
        self.protocol_instance = None
        self.connectionStatus = None
        self.base_client = None
        self.payload = payload
        self._logger = logging.getLogger(__name__)

    _reconnect_error_payload = {"e": "error", "m": "Max reconnect retries reached"}

    def startedConnecting(self, connector):
        self.connectionStatus = True
        self._logger.info("Start to connect....")

    def clientConnectionFailed(self, connector, reason):
        self.connectionStatus = False
        self._logger.error(
            "Can't connect to server. Reason: {}.".format(
                reason
            )
        )
        # self.retry(connector)
        # if self.retries > self.maxRetries:
        #     self.callback(self._reconnect_error_payload)

    def clientConnectionLost(self, connector, reason):
        self.connectionStatus = False
        self._logger.error(
            "Lost connection to Server. Reason: {}.".format(
                reason
            )
        )

        # self.retry(connector)
        # if self.retries > self.maxRetries:
        #     self.callback(self._reconnect_error_payload)

    def buildProtocol(self, addr):
        return BinanceClientProtocol(self, payload=self.payload)




