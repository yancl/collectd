from protocol.genpy.collectd.Collector import Processor
from thrift.transport import TSocket
from thrift.protocol import TBinaryProtocol
from thrift.server.TNonblockingServer import TNonblockingServer

class CollectorHandler(object):
    def add_event(self, events):
        print 'e:',events

    def add_time_slice(self, slices):
        print 's:',slices


class Server(object):
    def __init__(self, host, port):
        handler = CollectorHandler()
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
    Server(host='127.0.0.1', port=1464).serve()
