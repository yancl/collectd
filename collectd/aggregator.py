import time
import socket
from collections import defaultdict
from threading import Thread
from client import Stats
from protocol.genpy.collectd.ttypes import Point, Event, Alarm, TimeSlice, ETimeSlicePointType, Span
from utils import now
from collections import namedtuple
from Queue import Queue
import cPickle

ConsumeItem = namedtuple('ConsumeItem', 'content, ctype')

class Aggregator(object):
    ALARM_LEVEL_FATAL = 0
    ALARM_LEVEL_ERROR = 1
    ALARM_LEVEL_WARNING = 2
    ALARM_LEVEL_INFO = 3

    __slots__ = ['_aggregator_time', '_event', '_timeline', '_trace', '_commit_trace',\
                '_alarm', '_rotate_thread', '_report_thread', \
                '_reporter', '_hostname', '_event_category', '_timeline_category', '_q']
    def __init__(self, event_category='frequency', timeline_category='latency', alarm_category='alarm',
                server='127.0.0.1', port=1464, aggregator_time=30):
        self._event_category = event_category
        self._timeline_category = timeline_category
        self._reporter = Stats(server=server, port=port)
        self._aggregator_time = aggregator_time
        self._event = defaultdict(int)
        self._timeline = defaultdict(list)
        self._trace = defaultdict(list)
        self._commit_trace = defaultdict(list)
        self._alarm = []
        self._rotate_thread = Thread(target=self._rotate_worker)
        self._report_thread = Thread(target=self._report_worker)
        self._hostname = self._get_host_name()
        self._q = Queue(maxsize=100000)

    def add_trace(self, trace_id, span_id, span_name, timestamp, duration):
        span = Span(timestamp=timestamp, trace_id=trace_id,
                    name=span_name, id=span_id, parent_id=0,
                    duration=duration, host=self._hostname)
        self._trace[trace_id].append(span)

    def commit_trace(self, trace_id):
        trace = self._trace.pop(trace_id, None)
        if trace:
            self._commit_trace[trace_id] = trace

    def abort_trace(self, trace_id):
        self._trace.pop(trace_id, None)

    def add_alarm(self, level, category, key, reason, trace_id=0):
        reason = cPickle.dumps(dict(reason=reason, trace_id=trace_id))
        self._alarm.append((level, category, key, reason))

    def incr_event_counter(self, key, val=1):
        self._event[key] += 1

    def append_timeline(self, key, val):
        self._timeline[key].append(val)

    def _rotate_worker(self):
        while True:
            try:
                time.sleep(self._aggregator_time)
                #sweep data
                event = self._event
                timeline = self._timeline
                commit_trace = self._commit_trace
                alarm = self._alarm

                self._event = defaultdict(int)
                self._timeline = defaultdict(list)
                self._commit_trace = defaultdict(list)
                self._alarm = [] 

                #async consumer
                self._q.put_nowait(ConsumeItem(content=event, ctype=0))
                self._q.put_nowait(ConsumeItem(content=timeline, ctype=1))
                self._q.put_nowait(ConsumeItem(content=alarm, ctype=2))
                self._q.put_nowait(ConsumeItem(content=commit_trace, ctype=3))
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
                elif item.ctype == 2:
                    self._report_alarm(item.content)
                elif item.ctype == 3:
                    self._report_trace(item.content)
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

    def _report_alarm(self, alarm_l):
        alarms = []
        current = now()
        for (level, category, key, reason) in alarm_l:
            alarms.append(Alarm(timestamp=current, category=category, key=key,
                    reason=reason, level=level, host=self._hostname))
        if alarms:
            self._reporter.add_alarms(alarms)

    def _report_trace(self, traces):
        spans = []
        for (k, v) in traces.iteritems():
            spans.extend(v)

        if spans:
            self._reporter.add_traces(spans)

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
                  Point(k=ETimeSlicePointType.PT_AVG, v='%.4f' % avg),
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
