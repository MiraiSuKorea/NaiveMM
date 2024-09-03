# -*- coding: utf-8 -*-
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(os.path.abspath(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))))))

import json
import logging
import threading
from urllib.parse import urlparse
from twisted.internet import reactor, ssl
from twisted.internet.error import ReactorAlreadyRunning
from autobahn.twisted.websocket import WebSocketClientFactory, connectWS
from Spot_trading.websocket.binance_client_protocol import BinanceClientProtocol
from Spot_trading.websocket.binance_client_factory import BinanceClientFactory


class BinanceSocketManager(threading.Thread, BinanceClientFactory):
    def __init__(self, stream_url):
        super().__init__()
        self.connectionStatus = None
        self.factories = {}
        self._connected_event = threading.Event()
        self.stream_url = stream_url
        self._conns = {}
        self._user_callback = None
        self._logger = logging.getLogger(__name__)

    def _start_socket(
        self, stream_name, payload, callback, is_combined=False, is_live=True
    ):
        if stream_name in self._conns:
            return False

        if is_combined:
            factory_url = self.stream_url + "/stream"
        else:
            factory_url = self.stream_url + "/ws"

        if not is_live:
            payload_obj = json.loads(payload.decode("utf8"))

            if is_combined:
                factory_url = factory_url + "?streams=" + payload_obj["params"]
            else:
                factory_url = factory_url + "/" + payload_obj["params"]
            payload = None

        self._logger.info("Connection with URL: {}".format(factory_url))
        self.factory = BinanceClientFactory(factory_url, payload=payload)
        self.factory.base_client = self
        self.factory.protocol = BinanceClientProtocol

        self.factory.setProtocolOptions(
            openHandshakeTimeout=5, autoPingInterval=300, autoPingTimeout=5
        )
        self.factory.callback = callback
        self.factories[stream_name] = self.factory
        reactor.callFromThread(self.add_connection, stream_name, self.stream_url)


    def add_connection(self, stream_name, url):
        if not url.startswith("wss://"):
            raise ValueError("expected wss:// URL prefix")

        factory = self.factories[stream_name]
        options = ssl.optionsForClientTLS(hostname=urlparse(url).hostname)
        self._conns[stream_name] = connectWS(factory, options)
        self.connectionStatus = self.factory.connectionStatus

    def stop_socket(self, conn_key):
        if conn_key not in self._conns:
            return

        # disable reconnecting if we are closing
        self._conns[conn_key].factory = WebSocketClientFactory(self.stream_url)
        self._conns[conn_key].disconnect()
        del self._conns[conn_key]
        self.connectionStatus = False


    def run(self):
        try:
            reactor.run(installSignalHandlers=False)
        except ReactorAlreadyRunning:
            # Ignore error about reactor already running
            pass

    def close(self):
        keys = set(self._conns.keys())
        for key in keys:
            self.stop_socket(key)
        self._conns = {}
        self.connectionStatus = False





