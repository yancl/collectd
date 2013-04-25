#cassandra
from cassandra_client.protocol.genpy.cassandra import Cassandra
from cassandra_client.protocol.genpy.cassandra.ttypes import *
from cassandra_client import cassandra_api
from thrift_client import thrift_client
import conf

def init_timeline_keyspace_and_column_familys(keyspace, cfs, servers):
    print 'initing timeline keyspace&column familys'
    print 'using servers:',servers
    print 'init keyspace:',keyspace
    print 'init column familys:', cfs
    client = thrift_client.ThriftClient(client_class=Cassandra.Client, servers=servers)
    _cassandra_meta_api = cassandra_api.CassandraMetaAPI(handle=client,
                            key_validation_class='org.apache.cassandra.db.marshal.UTF8Type',
                            default_validation_class='org.apache.cassandra.db.marshal.UTF8Type',
                            comparator_type='org.apache.cassandra.db.marshal.UTF8Type',
                            strategy_class='org.apache.cassandra.locator.NetworkTopologyStrategy')
    _cassandra_meta_api.add_keyspace(name=keyspace, cf_names=cfs)
    print 'done.'

def init_event_keyspace_and_column_familys(keyspace, cfs, servers):
    print 'initing event keyspace&column familys'
    print 'using servers:',servers
    print 'init keyspace:',keyspace
    print 'init column familys:', cfs
    client = thrift_client.ThriftClient(client_class=Cassandra.Client, servers=servers)
    _cassandra_meta_api = cassandra_api.CassandraMetaAPI(handle=client,
                            key_validation_class='org.apache.cassandra.db.marshal.UTF8Type',
                            default_validation_class='org.apache.cassandra.db.marshal.CounterColumnType',
                            comparator_type='org.apache.cassandra.db.marshal.UTF8Type',
                            strategy_class='org.apache.cassandra.locator.NetworkTopologyStrategy')
    _cassandra_meta_api.add_keyspace(name=keyspace, cf_names=cfs)
    print 'done.'

if __name__ == '__main__':
    init_timeline_keyspace_and_column_familys(keyspace='timeline_stats',
                            cfs=['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'],
                            servers=conf.SERVERS)

    init_event_keyspace_and_column_familys(keyspace='event_stats',
                            cfs=['Y', 'M', 'D', 'H', 'm'],
                            servers=conf.SERVERS)
