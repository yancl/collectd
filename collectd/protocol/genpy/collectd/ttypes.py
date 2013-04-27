#
# Autogenerated by Thrift Compiler (0.9.0)
#
# DO NOT EDIT UNLESS YOU ARE SURE THAT YOU KNOW WHAT YOU ARE DOING
#
#  options string: py
#

from thrift.Thrift import TType, TMessageType, TException, TApplicationException

from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol, TProtocol
try:
  from thrift.protocol import fastbinary
except:
  fastbinary = None


class ETimeSlicePointType:
  PT_MIN = 0
  PT_MAX = 1
  PT_AVG = 2
  PT_Q0 = 3
  PT_Q1 = 4
  PT_Q2 = 5
  PT_P9 = 6

  _VALUES_TO_NAMES = {
    0: "PT_MIN",
    1: "PT_MAX",
    2: "PT_AVG",
    3: "PT_Q0",
    4: "PT_Q1",
    5: "PT_Q2",
    6: "PT_P9",
  }

  _NAMES_TO_VALUES = {
    "PT_MIN": 0,
    "PT_MAX": 1,
    "PT_AVG": 2,
    "PT_Q0": 3,
    "PT_Q1": 4,
    "PT_Q2": 5,
    "PT_P9": 6,
  }


class Event:
  """
  Attributes:
   - timestamp
   - category
   - key
   - value
  """

  thrift_spec = (
    None, # 0
    (1, TType.I32, 'timestamp', None, None, ), # 1
    (2, TType.STRING, 'category', None, None, ), # 2
    (3, TType.LIST, 'key', (TType.STRING,None), None, ), # 3
    (4, TType.I64, 'value', None, None, ), # 4
  )

  def __init__(self, timestamp=None, category=None, key=None, value=None,):
    self.timestamp = timestamp
    self.category = category
    self.key = key
    self.value = value

  def read(self, iprot):
    if iprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None and fastbinary is not None:
      fastbinary.decode_binary(self, iprot.trans, (self.__class__, self.thrift_spec))
      return
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      if fid == 1:
        if ftype == TType.I32:
          self.timestamp = iprot.readI32();
        else:
          iprot.skip(ftype)
      elif fid == 2:
        if ftype == TType.STRING:
          self.category = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 3:
        if ftype == TType.LIST:
          self.key = []
          (_etype3, _size0) = iprot.readListBegin()
          for _i4 in xrange(_size0):
            _elem5 = iprot.readString();
            self.key.append(_elem5)
          iprot.readListEnd()
        else:
          iprot.skip(ftype)
      elif fid == 4:
        if ftype == TType.I64:
          self.value = iprot.readI64();
        else:
          iprot.skip(ftype)
      else:
        iprot.skip(ftype)
      iprot.readFieldEnd()
    iprot.readStructEnd()

  def write(self, oprot):
    if oprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and self.thrift_spec is not None and fastbinary is not None:
      oprot.trans.write(fastbinary.encode_binary(self, (self.__class__, self.thrift_spec)))
      return
    oprot.writeStructBegin('Event')
    if self.timestamp is not None:
      oprot.writeFieldBegin('timestamp', TType.I32, 1)
      oprot.writeI32(self.timestamp)
      oprot.writeFieldEnd()
    if self.category is not None:
      oprot.writeFieldBegin('category', TType.STRING, 2)
      oprot.writeString(self.category)
      oprot.writeFieldEnd()
    if self.key is not None:
      oprot.writeFieldBegin('key', TType.LIST, 3)
      oprot.writeListBegin(TType.STRING, len(self.key))
      for iter6 in self.key:
        oprot.writeString(iter6)
      oprot.writeListEnd()
      oprot.writeFieldEnd()
    if self.value is not None:
      oprot.writeFieldBegin('value', TType.I64, 4)
      oprot.writeI64(self.value)
      oprot.writeFieldEnd()
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    return


  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)

class Point:
  """
  Attributes:
   - k
   - v
  """

  thrift_spec = (
    None, # 0
    (1, TType.I32, 'k', None, None, ), # 1
    (2, TType.STRING, 'v', None, None, ), # 2
  )

  def __init__(self, k=None, v=None,):
    self.k = k
    self.v = v

  def read(self, iprot):
    if iprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None and fastbinary is not None:
      fastbinary.decode_binary(self, iprot.trans, (self.__class__, self.thrift_spec))
      return
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      if fid == 1:
        if ftype == TType.I32:
          self.k = iprot.readI32();
        else:
          iprot.skip(ftype)
      elif fid == 2:
        if ftype == TType.STRING:
          self.v = iprot.readString();
        else:
          iprot.skip(ftype)
      else:
        iprot.skip(ftype)
      iprot.readFieldEnd()
    iprot.readStructEnd()

  def write(self, oprot):
    if oprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and self.thrift_spec is not None and fastbinary is not None:
      oprot.trans.write(fastbinary.encode_binary(self, (self.__class__, self.thrift_spec)))
      return
    oprot.writeStructBegin('Point')
    if self.k is not None:
      oprot.writeFieldBegin('k', TType.I32, 1)
      oprot.writeI32(self.k)
      oprot.writeFieldEnd()
    if self.v is not None:
      oprot.writeFieldBegin('v', TType.STRING, 2)
      oprot.writeString(self.v)
      oprot.writeFieldEnd()
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    return


  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)

class TimeSlice:
  """
  Attributes:
   - timestamp
   - category
   - key
   - points
  """

  thrift_spec = (
    None, # 0
    (1, TType.I32, 'timestamp', None, None, ), # 1
    (2, TType.STRING, 'category', None, None, ), # 2
    (3, TType.STRING, 'key', None, None, ), # 3
    (4, TType.LIST, 'points', (TType.STRUCT,(Point, Point.thrift_spec)), None, ), # 4
  )

  def __init__(self, timestamp=None, category=None, key=None, points=None,):
    self.timestamp = timestamp
    self.category = category
    self.key = key
    self.points = points

  def read(self, iprot):
    if iprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None and fastbinary is not None:
      fastbinary.decode_binary(self, iprot.trans, (self.__class__, self.thrift_spec))
      return
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      if fid == 1:
        if ftype == TType.I32:
          self.timestamp = iprot.readI32();
        else:
          iprot.skip(ftype)
      elif fid == 2:
        if ftype == TType.STRING:
          self.category = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 3:
        if ftype == TType.STRING:
          self.key = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 4:
        if ftype == TType.LIST:
          self.points = []
          (_etype10, _size7) = iprot.readListBegin()
          for _i11 in xrange(_size7):
            _elem12 = Point()
            _elem12.read(iprot)
            self.points.append(_elem12)
          iprot.readListEnd()
        else:
          iprot.skip(ftype)
      else:
        iprot.skip(ftype)
      iprot.readFieldEnd()
    iprot.readStructEnd()

  def write(self, oprot):
    if oprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and self.thrift_spec is not None and fastbinary is not None:
      oprot.trans.write(fastbinary.encode_binary(self, (self.__class__, self.thrift_spec)))
      return
    oprot.writeStructBegin('TimeSlice')
    if self.timestamp is not None:
      oprot.writeFieldBegin('timestamp', TType.I32, 1)
      oprot.writeI32(self.timestamp)
      oprot.writeFieldEnd()
    if self.category is not None:
      oprot.writeFieldBegin('category', TType.STRING, 2)
      oprot.writeString(self.category)
      oprot.writeFieldEnd()
    if self.key is not None:
      oprot.writeFieldBegin('key', TType.STRING, 3)
      oprot.writeString(self.key)
      oprot.writeFieldEnd()
    if self.points is not None:
      oprot.writeFieldBegin('points', TType.LIST, 4)
      oprot.writeListBegin(TType.STRUCT, len(self.points))
      for iter13 in self.points:
        iter13.write(oprot)
      oprot.writeListEnd()
      oprot.writeFieldEnd()
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    return


  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)

class Alarm:
  """
  Attributes:
   - timestamp
   - category
   - key
   - reason
   - level
   - host
  """

  thrift_spec = (
    None, # 0
    (1, TType.I32, 'timestamp', None, None, ), # 1
    (2, TType.STRING, 'category', None, None, ), # 2
    (3, TType.STRING, 'key', None, None, ), # 3
    (4, TType.STRING, 'reason', None, None, ), # 4
    (5, TType.I32, 'level', None, None, ), # 5
    (6, TType.STRING, 'host', None, None, ), # 6
  )

  def __init__(self, timestamp=None, category=None, key=None, reason=None, level=None, host=None,):
    self.timestamp = timestamp
    self.category = category
    self.key = key
    self.reason = reason
    self.level = level
    self.host = host

  def read(self, iprot):
    if iprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None and fastbinary is not None:
      fastbinary.decode_binary(self, iprot.trans, (self.__class__, self.thrift_spec))
      return
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      if fid == 1:
        if ftype == TType.I32:
          self.timestamp = iprot.readI32();
        else:
          iprot.skip(ftype)
      elif fid == 2:
        if ftype == TType.STRING:
          self.category = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 3:
        if ftype == TType.STRING:
          self.key = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 4:
        if ftype == TType.STRING:
          self.reason = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 5:
        if ftype == TType.I32:
          self.level = iprot.readI32();
        else:
          iprot.skip(ftype)
      elif fid == 6:
        if ftype == TType.STRING:
          self.host = iprot.readString();
        else:
          iprot.skip(ftype)
      else:
        iprot.skip(ftype)
      iprot.readFieldEnd()
    iprot.readStructEnd()

  def write(self, oprot):
    if oprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and self.thrift_spec is not None and fastbinary is not None:
      oprot.trans.write(fastbinary.encode_binary(self, (self.__class__, self.thrift_spec)))
      return
    oprot.writeStructBegin('Alarm')
    if self.timestamp is not None:
      oprot.writeFieldBegin('timestamp', TType.I32, 1)
      oprot.writeI32(self.timestamp)
      oprot.writeFieldEnd()
    if self.category is not None:
      oprot.writeFieldBegin('category', TType.STRING, 2)
      oprot.writeString(self.category)
      oprot.writeFieldEnd()
    if self.key is not None:
      oprot.writeFieldBegin('key', TType.STRING, 3)
      oprot.writeString(self.key)
      oprot.writeFieldEnd()
    if self.reason is not None:
      oprot.writeFieldBegin('reason', TType.STRING, 4)
      oprot.writeString(self.reason)
      oprot.writeFieldEnd()
    if self.level is not None:
      oprot.writeFieldBegin('level', TType.I32, 5)
      oprot.writeI32(self.level)
      oprot.writeFieldEnd()
    if self.host is not None:
      oprot.writeFieldBegin('host', TType.STRING, 6)
      oprot.writeString(self.host)
      oprot.writeFieldEnd()
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    return


  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)
