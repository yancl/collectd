from thrift_client import thrift_client
from protocol.genpy.collectd import Collector

#caller ensure thread-safety
class Stats(object):
    __slots__ = '_client'
    def __init__(self, server, port):
        self._client = thrift_client.ThriftClient(client_class=Collector.Client, servers=[server+':'+str(port)])

    def add_event(self, event):
        self._client.add_event([event])

    def add_time_slice(self, slice):
        self._client.add_time_slice([slice])
