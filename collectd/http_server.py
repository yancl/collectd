#cassandra
from cassandra_client.protocol.genpy.cassandra import Cassandra
from cassandra_client.protocol.genpy.cassandra.ttypes import *
from cassandra_client import cassandra_api
from thrift_client import thrift_client

from datetime import datetime
import json
import web
urls = (
    #/time_line?category='call_latency'&key='add_user'&type=1&start='0'&finish=''&reversed=0&count=1000
    '/time_line', 'time_line'
)
app = web.application(urls, globals())

KEYSPACE = 'stats'
SERVERS = ['127.0.0.1:9160']

def create_cassandra_client(keyspace, servers):
    client = thrift_client.ThriftClient(client_class=Cassandra.Client,
                    servers=servers)
    return cassandra_api.CassandraAPI(handle=client, keyspace=keyspace)

def get_time_slice_pk(category, key):
    #FIXME, slow performance
    now = datetime.now()
    daystr = '%d-%d-%d' % (now.year, now.month, now.day)
    return daystr + ':' + category + ':' + key



class time_line:        
    def GET(self):
        wi = web.input()
        category = wi.category
        key = wi.key
        cf = wi.type
        start = wi.start
        finish = wi.finish
        reversed = wi.reversed
        count = int(wi.count)

        cassandra_handle = create_cassandra_client(keyspace=KEYSPACE, servers=SERVERS)
        pk = get_time_slice_pk(category, key)
        slice = cassandra_handle.select_slice(pk=pk, cf=cf, start=start, finish=finish, reversed=reversed, count=count)
        l = []
        for item in slice:
            l.append((item.column.name, item.column.value))
        j = {'slice':l}
        return json.dumps(j)


if __name__ == "__main__":
    app.run()
