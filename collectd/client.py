from thrift_client import thrift_client
from protocol.genpy.collectd import Collector

#caller ensure thread-safety
class Stats(object):
    __slots__ = '_client'
    def __init__(self, server, port):
        self._client = thrift_client.ThriftClient(client_class=Collector.Client, servers=[server+':'+str(port)])

    def add_event(self, event):
        self._client.add_event([event])

    def add_events(self, events):
        self._client.add_event(events)

    def add_time_slice(self, slice):
        self._client.add_time_slice([slice])

    def add_time_slices(self, slices):
        self._client.add_time_slice(slices)

    def add_alarm(self, alarm):
        self._client.add_alarm([alarm])

    def add_alarms(self, alarms):
        self._client.add_alarm(alarms)

    def add_trace(self, span):
        self._client.add_trace([span])

    def add_traces(self, spans):
        self._client.add_trace(spans)
