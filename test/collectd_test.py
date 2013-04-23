import sys
sys.path.insert(0, '../')

from collectd import Event,Stats,TimeSlice,Point,ETimeSlicePointType,now

class TestXBird(object):
    def setUp(self):
        self._stats = Stats(server='127.0.0.1', port=1464)

    def tearDown(self):
        self._stats = None

    def test_add_event(self):
        self._stats.add_event(Event(timestamp=now(),
                        category='call_counter',
                        key=['stats', 'add_user', 'host0'],
                        value=11))

    def test_add_slice(self):
        self._stats.add_time_slice(TimeSlice(timestamp=now(),
                        category='call_latency',
                        key='add_user',
                        points=[Point(ETimeSlicePointType.PT_MIN,'1.1'),
                                Point(ETimeSlicePointType.PT_MAX,'92.9'),
                                Point(ETimeSlicePointType.PT_AVG,'53.3'),
                                Point(ETimeSlicePointType.PT_Q0,'23.3'),
                                Point(ETimeSlicePointType.PT_Q1,'55.3'),
                                Point(ETimeSlicePointType.PT_Q2,'73.4')]))
