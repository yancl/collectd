from datetime import datetime
import time
from cPickle import dumps
from utils import now_microseconds

from collections import namedtuple, defaultdict
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

EventCF = ('Y', 'M', 'D', 'H', 'm')

class EventDateWrapper(object):
    def __init__(self, t):
        ts = time.localtime(t)
        self.m = {}
        self.m['Y'] = int(time.mktime((ts.tm_year,1,1,0,0,0,0,0,0)))
        self.m['M'] = int(time.mktime((ts.tm_year,ts.tm_mon,1,0,0,0,0,0,0)))
        self.m['D'] = int(time.mktime((ts.tm_year,ts.tm_mon,ts.tm_mday,0,0,0,0,0,0)))
        self.m['H'] = int(time.mktime((ts.tm_year,ts.tm_mon,ts.tm_mday,ts.tm_hour,0,0,0,0,0)))
        self.m['m'] = int(time.mktime((ts.tm_year,ts.tm_mon,ts.tm_mday,ts.tm_hour,ts.tm_min,0,0,0,0)))
        self.daystr= '%d-%d-%d' % (ts.tm_year, ts.tm_mon, ts.tm_mday)

class TimeLineDateWrapper(object):
    def __init__(self, t):
        ts = time.localtime(t)
        if ts.tm_sec < 30:
            self.s = int(time.mktime((ts.tm_year,ts.tm_mon,ts.tm_mday,ts.tm_hour,ts.tm_min,0,0,0,0)))
        else:
            self.s = int(time.mktime((ts.tm_year,ts.tm_mon,ts.tm_mday,ts.tm_hour,ts.tm_min,30,0,0,0)))
        self.daystr = '%d-%d-%d' % (ts.tm_year, ts.tm_mon, ts.tm_mday)

class CassandraWrapper(object):
    def __init__(self, timeline_keyspace, event_keyspace, servers, options):
        timeline_client = thrift_client.ThriftClient(client_class=Cassandra.Client,
                        servers=servers, options=options)
        event_client = thrift_client.ThriftClient(client_class=Cassandra.Client,
                        servers=servers, options=options)
        alarm_client = thrift_client.ThriftClient(client_class=Cassandra.Client,
                        servers=servers, options=options)
        trace_client = thrift_client.ThriftClient(client_class=Cassandra.Client,
                        servers=servers, options=options)
        self._timeline_cassandra_api = cassandra_api.CassandraAPI(handle=timeline_client, keyspace=timeline_keyspace)
        self._trace_cassandra_api = cassandra_api.CassandraAPI(handle=trace_client, keyspace=timeline_keyspace)
        self._event_cassandra_api = cassandra_api.CassandraAPI(handle=event_client, keyspace=event_keyspace)
        self._alarm_cassandra_api = cassandra_api.CassandraAPI(handle=alarm_client, keyspace=event_keyspace)

    def _batch_update_timeline(self, handle, update_pairs):
        update_pairs = self._merge_update_pairs(update_pairs)
        cb = cassandra_api.CassandraAPI.CassandraBatch()
        for (pk, columns) in update_pairs:
            cbf = cassandra_api.CassandraAPI.CassandraBatchCF()
            m = self._merge_update_cf(columns)
            for (cf, mutations) in m.iteritems():
                cbf.add(cf=cf, mutations=mutations)
            cb.add(pk=pk, cassandra_batch_cf=cbf)
        handle.batch_update(cassandra_batch=cb)

    def _batch_update_event(self, handle, update_pairs):
        update_pairs = self._merge_update_pairs(update_pairs)
        cb = cassandra_api.CassandraAPI.CassandraBatch()
        for (pk, columns) in update_pairs:
            cbf = cassandra_api.CassandraAPI.CassandraBatchCF()
            m = self._merge_update_counter_cf(columns)
            for (cf, mutations) in m.iteritems():
                cbf.add(cf=cf, mutations=mutations)
            cb.add(pk=pk, cassandra_batch_cf=cbf)
        handle.batch_update(cassandra_batch=cb)

    def _batch_update_event_properties(self, handle, update_pairs):
        update_pairs = self._merge_update_pairs(update_pairs)
        cb = cassandra_api.CassandraAPI.CassandraBatch()
        for (pk, columns) in update_pairs:
            cbf = cassandra_api.CassandraAPI.CassandraBatchCF()
            m = self._merge_update_cf(columns)
            for (cf, mutations) in m.iteritems():
                cbf.add(cf=cf, mutations=mutations)
            cb.add(pk=pk, cassandra_batch_cf=cbf)
        handle.batch_update(cassandra_batch=cb)

    def _merge_update_pairs(self, pairs):
        m = defaultdict(list)
        for (k, v) in pairs:
            m[k].extend(v)
        r = []
        for (k, v) in m.iteritems():
            r.append((k, v))
        return r

    def _merge_update_cf(self, columns):
        m = defaultdict(list)
        for column in columns:
            m[column.cf].append(
                Mutation(column_or_supercolumn=
                    ColumnOrSuperColumn(
                        column=Column(
                                name=column.name,
                                value=column.value,
                                timestamp=column.timestamp))))
        return m

    def _merge_update_counter_cf(self, columns):
        m = defaultdict(list)
        for column in columns:
            m[column.cf].append(
                Mutation(column_or_supercolumn=
                    ColumnOrSuperColumn(
                        counter_column=CounterColumn(
                                name=column.name,
                                value=column.value))))
        return m

    def _denormalize_keys(self, key_list):
        r = []
        num = len(key_list)

        for i in xrange(num):
            r.append(':'.join(key_list[0:i+1]))
        return r

    def _compose_longest_key(self, key_list):
        return ':'.join(key_list)

    def add_event(self, events):
        update_pairs = []
        properties_pairs = []
        for event in events:
            t = EventDateWrapper(event.timestamp)
            keys = self._denormalize_keys(event.key)
            for cf in EventCF:
                if cf == 'm':
                    continue
                for key in keys:
                    columns = [StoreColumn(cf=cf, name=str(t.m[cf]), value=event.value, timestamp=0)]  #counter do not need timestamp
                    update_pairs.append((self._get_store_pk(event.category, key), columns))

            #process column family 'm',it is special 
            #because of huge amount if we do not store it according to DAY.
            for key in keys:
                columns = [StoreColumn(cf='m', name=str(t.m['m']), value=event.value, timestamp=0)]
                update_pairs.append((t.daystr+':'+self._get_store_pk(event.category, key), columns))
        self._batch_update_event(self._event_cassandra_api, update_pairs)

    def _get_store_pk(self, category, key):
        return category + ':' + key

    def add_time_slice(self, slices):
        timestamp = now_microseconds()
        update_pairs = []
        for time_slice in slices:
            t = TimeLineDateWrapper(time_slice.timestamp)
            columns = [StoreColumn(cf=str(point.k), name=str(t.s),
                                    value=str(point.v), timestamp=timestamp) for point in time_slice.points]
            pk = t.daystr + ':' + self._get_store_pk(time_slice.category, time_slice.key)
            update_pairs.append((pk, columns))
        self._batch_update_timeline(self._timeline_cassandra_api, update_pairs)

    def add_alarm(self, alarms):
        timestamp = now_microseconds()
        update_pairs = []
        reason_pairs = []
        for alarm in alarms:
            alarm_key = (str(alarm.level), alarm.category, alarm.key, alarm.host)
            t = EventDateWrapper(alarm.timestamp)
            keys = self._denormalize_keys(alarm_key)
            for cf in EventCF:
                if cf == 'm':
                    continue
                for key in keys:
                    columns = [StoreColumn(cf=cf, name=str(t.m[cf]), value=1, timestamp=0)]  #counter do not need timestamp
                    update_pairs.append((self._get_store_pk('alarm', key), columns))

            #process column family 'm',it is special 
            #because of huge amount if we do not store it according to DAY.
            for key in keys:
                columns = [StoreColumn(cf='m', name=str(t.m['m']), value=1, timestamp=0)]
                update_pairs.append((t.daystr+':'+self._get_store_pk('alarm', key), columns))

            columns = [StoreColumn(cf='properties', name=str(alarm.timestamp)+':'+ 
                                    self._compose_longest_key(alarm_key),
                                    value=alarm.reason,
                                    timestamp=timestamp)]
            reason_pairs.append((t.daystr+':alarm', columns))
        self._batch_update_event(self._alarm_cassandra_api, update_pairs)
        self._batch_update_event_properties(self._alarm_cassandra_api, reason_pairs)

    def add_trace(self, spans):
        timestamp = now_microseconds()
        update_pairs = []
        for span in spans:
            columns = [StoreColumn(cf='trace', name=str(span.id),
                            value=dumps(self._trans_span_to_dict(span)), timestamp=timestamp)]
            update_pairs.append((str(span.trace_id), columns))
        self._batch_update_timeline(self._trace_cassandra_api, update_pairs)

    def _trans_span_to_dict(self, span):
        return dict(timestamp=span.timestamp, trace_id=span.trace_id, name=span.name, id=span.id,
                    parent_id=span.parent_id, duration=span.duration, host=span.host)


class CollectorConsumer(object):
    def __init__(self, q_max_size, store):
        self._store = store 
        self._eq = Queue(maxsize=q_max_size)
        self._tq = Queue(maxsize=q_max_size)
        self._aq = Queue(maxsize=q_max_size)
        self._sq = Queue(maxsize=q_max_size)
        self._event_thread = self._create_worker(self._event_worker)
        self._time_thread = self._create_worker(self._time_slice_worker)
        self._alarm_thread = self._create_worker(self._alarm_worker)
        self._trace_thread = self._create_worker(self._trace_worker)

    def add_event(self, events):
        self._eq.put_nowait(events)

    def add_time_slice(self, slices):
        self._tq.put_nowait(slices)

    def add_alarm(self, alarms):
        self._aq.put_nowait(alarms)

    def add_trace(self, spans):
        self._sq.put_nowait(spans)

    def _create_worker(self, runner):
        return Thread(target=runner)

    def _event_worker(self):
        while True:
            try:
                events = self._eq.get(block=True)
                self._store.add_event(events)
            except Exception,e:
                print e

    def _time_slice_worker(self):
        while True:
            try:
                slice = self._tq.get(block=True)
                self._store.add_time_slice(slice)
            except Exception,e:
                print e

    def _alarm_worker(self):
        while True:
            try:
                alarms = self._aq.get(block=True)
                self._store.add_alarm(alarms)
            except Exception,e:
                print e

    def _trace_worker(self):
        while True:
            try:
                spans = self._sq.get(block=True)
                self._store.add_trace(spans)
            except Exception,e:
                print e


    def run(self):
        self._event_thread.setDaemon(True)
        self._time_thread.setDaemon(True)
        self._alarm_thread.setDaemon(True)
        self._trace_thread.setDaemon(True)
        self._event_thread.start()
        self._time_thread.start()
        self._alarm_thread.start()
        self._trace_thread.start()

class CollectorHandler(object):
    def __init__(self, collector):
        self._collector = collector

    def add_event(self, events):
        self._collector.add_event(events)

    def add_time_slice(self, slices):
        self._collector.add_time_slice(slices)

    def add_alarm(self, alarms):
        self._collector.add_alarm(alarms)

    def add_trace(self, spans):
        self._collector.add_trace(spans)



class Server(object):
    def __init__(self, host, port, collector_consumer):
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
    import os
    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option("-f", "--file", action="store", type="string", dest="filename",
                        help="read conf for cassandra servers [must]")
    parser.add_option("-t", "--timeout", action="store", type="int", dest="timeout",
                        help="the timeout of operations to cassandra servers", default=10)
    parser.add_option("-q", "--quiet",
                        action="store_false", dest="verbose", default=True,
                        help="don't print status messages to stdout")

    (options, args) = parser.parse_args()
    print options
    if not options.filename:
        parser.error("-f is a must args")
        os.exit(1)

    servers = []
    with open(options.filename, 'r') as f:
        for line in f:
            (name, hosts) = line.strip().split('=')
            if name == 'SERVERS':
                servers = hosts.split(',')

    if not servers:
        parser.error("conf file is not valide, see servers.conf for example")
        os.exit(1)

    server_options={'timeout':options.timeout}

    collector_consumer = CollectorConsumer(q_max_size=100000,
                                           store=CassandraWrapper( timeline_keyspace='timeline_stats',
                                                    event_keyspace='event_stats', servers=servers,
                                                    options=server_options))
    collector_consumer.run()
    Server(host='127.0.0.1', port=1464, collector_consumer=collector_consumer).serve()
