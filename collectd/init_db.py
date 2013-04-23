#cassandra
from cassandra_client.protocol.genpy.cassandra import Cassandra
from cassandra_client.protocol.genpy.cassandra.ttypes import *
from cassandra_client import cassandra_api
from thrift_client import thrift_client

def init_keyspace_and_columns(keyspace, cfs, servers):
    print 'using servers:',servers
    print 'init keyspace:',keyspace
    print 'init column familys:', cfs
    client = thrift_client.ThriftClient(client_class=Cassandra.Client, servers=servers)
    _cassandra_meta_api = cassandra_api.CassandraMetaAPI(handle=client)
    _cassandra_meta_api.add_keyspace(name=keyspace, cf_names=cfs)
    print 'done.'

if __name__ == '__main__':
    init_keyspace_and_columns(keyspace='stats',
                            cfs=['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'],
                            servers=['127.0.0.1:9160'])
