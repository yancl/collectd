import time
import socket
from collections import defaultdict
from threading import Thread
from client import Stats
from protocol.genpy.collectd.ttypes import Point, Event, TimeSlice, ETimeSlicePointType
from utils import now
from collections import namedtuple
from Queue import Queue

ConsumeItem = namedtuple('ConsumeItem', 'content, ctype')

class Aggregator(object):
    __slots__ = ['_aggregator_time', '_event', '_timeline', '_rotate_thread', '_report_thread', \
                '_reporter', '_hostname', '_event_category', '_timeline_category', '_q']
    def __init__(self, event_category='frequency', timeline_category='latency',
                server='127.0.0.1', port=1464, aggregator_time=30):
        self._event_category = event_category
        self._timeline_category = timeline_category
        self._reporter = Stats(server=server, port=port)
        self._aggregator_time = aggregator_time
        self._event = defaultdict(int)
        self._timeline = defaultdict(list)
        self._rotate_thread = Thread(target=self._rotate_worker)
        self._report_thread = Thread(target=self._report_worker)
        self._hostname = self._get_host_name()
        self._q = Queue(maxsize=100000)

    def incr_event_counter(self, key, val=1):
        self._event[key] += 1

    def append_timeline(self, key, val):
        self._timeline[key].append(val)

    def _rotate_worker(self):
        while True:
            try:
                time.sleep(self._aggregator_time)
                event = self._event
                timeline = self._timeline
                self._event = {}
                self._timeline = {}
                self._q.put_nowait(ConsumeItem(content=event, ctype=0))
                self._q.put_nowait(ConsumeItem(content=timeline, ctype=1))
            except Exception,e:
                print 'rotate ex:',e

    def _report_worker(self):
        while True:
            try:
                item = self._q.get(block=True)
                if item.ctype == 0:
                    self._report_event(item.content)
                elif item.ctype == 1:
                    self._report_timeline(item.content)
            except Exception, e:
                print 'report ex:',e

    def _report_event(self, event_m):
        events = []
        current = now()
        for (k, v) in event_m.iteritems():
            events.append(Event(timestamp=current, category=self._event_category, key=[k, self._hostname], value=v))
        if events:
            self._reporter.add_events(events)

    def _report_timeline(self, timeline_m):
        current = now()
        time_slices = []
        for (k, v) in timeline_m.iteritems():
            points = self._compute_timeline_sample_point(v)
            time_slices.append(TimeSlice(timestamp=current, category=self._timeline_category, key=k, points=points))
        if time_slices:
            self._reporter.add_time_slices(time_slices)

    def _get_host_name(self):
        return socket.gethostname()

    def _compute_timeline_sample_point(self, vs):
        if not vs:
            return []
        points = []
        vs0 = sorted(vs)
        avg = sum(vs0) / len(vs0)
        q0 = vs0[((len(vs0) * 1) /4)]
        q1 = vs0[((len(vs0) * 2) /4)]
        q2 = vs0[((len(vs0) * 3) /4)]
        p9 = vs0[((len(vs0) * 9) /10)]
        points = [Point(k=ETimeSlicePointType.PT_MIN, v='%.4f' % vs0[0]),
                  Point(k=ETimeSlicePointType.PT_MAX, v='%.4f' % vs0[-1]),
                  Point(k=ETimeSlicePointType.PT_MAX, v='%.4f' % avg),
                  Point(k=ETimeSlicePointType.PT_Q0, v='%.4f' % q0),
                  Point(k=ETimeSlicePointType.PT_Q1, v='%.4f' % q1),
                  Point(k=ETimeSlicePointType.PT_Q2, v='%.4f' % q2),
                  Point(k=ETimeSlicePointType.PT_P9, v='%.4f' % p9)]
        return points

    def run(self):
        self._rotate_thread.setDaemon(True)
        self._rotate_thread.start()
        self._report_thread.setDaemon(True)
        self._report_thread.start()
