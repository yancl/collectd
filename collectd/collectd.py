from datetime import datetime
import time

from collections import namedtuple
from Queue import Queue
from threading import Thread

#cassandra
from cassandra_client.protocol.genpy.cassandra import Cassandra
from cassandra_client.protocol.genpy.cassandra.ttypes import *
from cassandra_client import cassandra_api
from thrift_client import thrift_client

#thrift server
from protocol.genpy.collectd.Collector import Processor
from thrift.transport import TSocket
from thrift.protocol import TBinaryProtocol
from thrift.server.TNonblockingServer import TNonblockingServer


StoreColumn = namedtuple('StoreColumn', 'cf name value timestamp')

def get_daystr():
    current = datetime.now()
    return '%d-%d-%d' % (current.year, current.month, current.day)

class CassandraWrapper(object):
    def __init__(self, timeline_keyspace, event_keyspace, servers=['127.0.0.1:9160']):
        options = {'timeout':10}
        timeline_client = thrift_client.ThriftClient(client_class=Cassandra.Client,
                        servers=servers, options=options)
        event_client = thrift_client.ThriftClient(client_class=Cassandra.Client,
                        servers=servers, options=options)
        self._timeline_cassandra_api = cassandra_api.CassandraAPI(handle=timeline_client, keyspace=timeline_keyspace)
        self._event_cassandra_api = cassandra_api.CassandraAPI(handle=event_client, keyspace=event_keyspace)
        self._daystr = get_daystr()

    def _batch_update_timeline(self, update_pairs):
        cb = cassandra_api.CassandraAPI.CassandraBatch()
        for (pk, columns) in update_pairs:
            cbf = cassandra_api.CassandraAPI.CassandraBatchCF()
            for column in columns:
                mutations = []
                mutations.append(Mutation(column_or_supercolumn=
                    ColumnOrSuperColumn(
                        column=Column(
                                name=column.name,
                                value=column.value,
                                timestamp=column.timestamp))))
                cbf.add(cf=column.cf, mutations=mutations)

            cb.add(pk=pk, cassandra_batch_cf=cbf)
        self._timeline_cassandra_api.batch_update(cassandra_batch=cb)

    def _batch_update_event(self, pks, columns):
        cb = cassandra_api.CassandraAPI.CassandraBatch()
        cbf = cassandra_api.CassandraAPI.CassandraBatchCF()
        for column in columns:
            mutations = []
            mutations.append(Mutation(column_or_supercolumn=
                ColumnOrSuperColumn(
                    counter_column=CounterColumn(
                            name=column.name,
                            value=column.value))))
            cbf.add(cf=column.cf, mutations=mutations)

        for pk in pks:
            cb.add(pk=pk, cassandra_batch_cf=cbf)
        self._event_cassandra_api.batch_update(cassandra_batch=cb)

    def _denormalize_keys(self, key_list):
        r = []
        num = len(key_list)

        for i in xrange(num):
            r.append(':'.join(key_list[0:i+1]))
        return r

    def add_event(self, events):
        for event in events:
            keys = self._denormalize_keys(event.key)
            pks = [self._get_store_pk(event.category, key) for key in keys]
            self._batch_update_event(pks=pks,
                    columns=[StoreColumn(cf='counters', name=str(event.timestamp), value=event.value, timestamp=event.timestamp)])

    def _get_store_pk(self, category, key):
        return self._daystr + ':' + category + ':' + key

    def add_time_slice(self, slices):
        update_pairs = []
        for time_slice in slices:
            columns = [StoreColumn(cf=str(point.k), name=str(time_slice.timestamp),
                                    value=str(point.v), timestamp=time_slice.timestamp) for point in time_slice.points]
            pk = self._get_store_pk(time_slice.category, time_slice.key)
            update_pairs.append((pk, columns))
        self._batch_update_timeline(update_pairs)

    def update_daystr(self, daystr):
        self._daystr = daystr

class CollectorConsumer(object):
    def __init__(self, q_max_size, store):
        self._store = store 
        self._eq = Queue(maxsize=q_max_size)
        self._tq = Queue(maxsize=q_max_size)
        self._event_worker = self._create_worker(self._event_worker)
        self._time_worker = self._create_worker(self._time_slice_worker)
        self._daystr_worker = self._create_worker(self._daystr_worker)

    def add_event(self, events):
        self._eq.put_nowait(events)

    def add_time_slice(self, slices):
        self._tq.put_nowait(slices)

    def _create_worker(self, runner):
        return Thread(target=runner)

    def _event_worker(self):
        while True:
            events = self._eq.get(block=True)
            self._store.add_event(events)

    def _daystr_worker(self):
        while True:
            time.sleep(30)
            self._store.update_daystr(get_daystr())
            

    def _time_slice_worker(self):
        while True:
            slice = self._tq.get(block=True)
            self._store.add_time_slice(slice)

    def run(self):
        self._event_worker.setDaemon(True)
        self._time_worker.setDaemon(True)
        self._daystr_worker.setDaemon(True)
        self._event_worker.start()
        self._time_worker.start()
        self._daystr_worker.start()

class CollectorHandler(object):
    def __init__(self, collector):
        self._collector = collector

    def add_event(self, events):
        self._collector.add_event(events)

    def add_time_slice(self, slices):
        self._collector.add_time_slice(slices)

collector_consumer = CollectorConsumer(q_max_size=100000,
                                    store=CassandraWrapper(timeline_keyspace='timeline_stats',
                                                            event_keyspace='event_stats'))

class Server(object):
    def __init__(self, host, port):
        handler = CollectorHandler(collector_consumer)
        processor = Processor(handler)
        transport = TSocket.TServerSocket(host, port)
        pfactory = TBinaryProtocol.TBinaryProtocolFactory()
        self._server = TNonblockingServer(processor,
                                    transport,
                                    pfactory,
                                    pfactory)

    def serve(self):
        self._server.serve()


if __name__ == '__main__':
    collector_consumer.run()
    Server(host='127.0.0.1', port=1464).serve()
