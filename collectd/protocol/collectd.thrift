#used for counter
struct Event {
    1: i64 timestamp,           // microseconds from epoch
    2: string category,
    3: list<string> key,
    4: i64 value,
    #5: optional map<string, string> properties
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
    1: i64 timestamp,           // microseconds from epoch
    2: string category,
    3: string key,
    4: list<Point> points,
}

struct Alarm {
    1: i64 timestamp,           // microseconds from epoch
    2: string category,
    3: string key,
    4: string reason,
    5: i32 level,
    6: string host,
}

struct Span {
    1: i64 timestamp,                 // microseconds from epoch
    2: i64 trace_id,                  // unique trace id, use for all spans in trace
    3: string name,                  // span name, rpc method for example
    4: i64 id,                       // unique span id, only used for this span
    5: optional i64 parent_id,       // parent span id
    6: optional i32 duration,        // how long did the operation take? microseconds
    7: optional string host,         // the host this span happens
}

service Collector {
    void add_event(1: list<Event> events)
    void add_time_slice(1: list<TimeSlice> slices)
    void add_alarm(1: list<Alarm> alarms)
    void add_trace(1: list<Span> spans)
}
