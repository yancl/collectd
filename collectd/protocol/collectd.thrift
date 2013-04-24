#used for counter
struct Event {
    1: i32 timestamp,
    2: string category,
    3: list<string> key,
    4: i64 value
}

enum ETimeSlicePointType
{
    PT_MIN = 0,
    PT_MAX = 1,
    PT_AVG = 2,
    PT_Q0  = 3, #First Quartile
    PT_Q1  = 4, #Second Quartile
    PT_Q2  = 5, #Third Qurartile
    PT_P9  = 6, #90 percent response time
}

struct Point
{
    1: ETimeSlicePointType k,
    2: string v
}

#used for timeline
struct TimeSlice {
    1: i32 timestamp
    2: string category,
    3: string key,
    4: list<Point> points,
}

service Collector {
    void add_event(1: list<Event> events)
    void add_time_slice(1: list<TimeSlice> slices)
}
