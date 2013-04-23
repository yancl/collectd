import time

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

from collections import namedtuple

StoreColumn = namedtuple('StoreColumn', 'cf name value timestamp')

def init_keyspace_and_columns(keyspace, cfs):
    client = thrift_client.ThriftClient(client_class=Cassandra.Client, servers=servers)
    _cassandra_meta_api = cassandra_meta_api.CassandraMetaAPI(handle=client)
    _cassandra_meta_api.add_keyspace(name=keyspace, cf_names=cfs)

class CassandraWrapper(object):
    def __init__(self, keyspace, servers=['127.0.0.1:9160']):
        client = thrift_client.ThriftClient(client_class=Cassandra.Client,
                        servers=servers)
        self._cassandra_api = cassandra_api.CassandraAPI(handle=client, keyspace=keyspace)

    def _batch_update(self, pk, columns):
        cbf = cassandra_api.CassandraAPI.CassandraBatchCF()
        mutations = []
        for column in columns:
            mutations.append(Mutation(column_or_supercolumn=
                ColumnOrSuperColumn(
                    column=Column(
                            name=column.name,
                            value=column.value,
                            timestamp=column.timestamp))))
            cbf.add(cf=column.cf, mutations=mutations)

        #cassandra batch
        cb = cassandra_api.CassandraAPI.CassandraBatch()
        cb.add(pk=pk, cassandra_batch_cf=cbf)
        self._cassandra_api.batch_update(cassandra_batch=cb)

    def add_event(self, events):
        pass

    def _get_time_slice_pk(self, time_slice):
        return time_slice.category + ':' + time_slice.key

    def add_time_slice(self, slices):
        for time_slice in slices:
            columns = [StoreColumn(cf=str(point.k), name=str(time_slice.timestamp),
                                    value=str(point.v), timestamp=time_slice.timestamp) for point in time_slice.points]
            print 'update slice:',time_slice
            pk = self._get_time_slice_pk(time_slice)
            self._batch_update(pk=pk, columns=columns)

class CollectorConsumer(object):
    def __init__(self, q_max_size, store):
        self._store = store 
        self._eq = Queue(maxsize=q_max_size)
        self._tq = Queue(maxsize=q_max_size)
        self._event_worker = self._create_worker(self._event_consumer)
        self._time_worker = self._create_worker(self._time_slice_consumer)

    def add_event(self, events):
        self._eq.put_nowait(events)

    def add_time_slice(self, slices):
        self._tq.put_nowait(slices)

    def _create_worker(self, runner):
        return Thread(target=runner)

    def _event_consumer(self):
        while True:
            events = self._eq.get(block=True)
            #self._cassandra.
            self._store.add_event(events)
            print 'e:',events

    def _time_slice_consumer(self):
        while True:
            slice = self._tq.get(block=True)
            self._store.add_time_slice(slice)
            print 's:',slice

    def run(self):
        self._event_worker.setDaemon(True)
        self._time_worker.setDaemon(True)
        self._event_worker.start()
        self._time_worker.start()

class CollectorHandler(object):
    def __init__(self, collector):
        self._collector = collector

    def add_event(self, events):
        self._collector.add_event(events)

    def add_time_slice(self, slices):
        self._collector.add_time_slice(slices)

collector_consumer = CollectorConsumer(q_max_size=100000, store=CassandraWrapper(keyspace='stats'))

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
