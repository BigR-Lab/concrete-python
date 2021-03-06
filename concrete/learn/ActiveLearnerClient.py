# -*- coding: utf-8 -*-
#
# Autogenerated by Thrift Compiler (0.9.3)
#
# DO NOT EDIT UNLESS YOU ARE SURE THAT YOU KNOW WHAT YOU ARE DOING
#
#  options string: py:new_style,utf8strings,coding=utf-8
#

from thrift.Thrift import TType, TMessageType, TException, TApplicationException
import concrete.services.Service
import logging
from ttypes import *
from thrift.Thrift import TProcessor
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol, TProtocol
try:
  from thrift.protocol import fastbinary
except:
  fastbinary = None


class Iface(concrete.services.Service.Iface):
  """
  The active learner client implements a method to accept new sorts of the annotation units
  """
  def submitSort(self, sessionId, unitIds):
    """
    Submit a new sort of communications to the broker

    Parameters:
     - sessionId
     - unitIds
    """
    pass


class Client(concrete.services.Service.Client, Iface):
  """
  The active learner client implements a method to accept new sorts of the annotation units
  """
  def __init__(self, iprot, oprot=None):
    concrete.services.Service.Client.__init__(self, iprot, oprot)

  def submitSort(self, sessionId, unitIds):
    """
    Submit a new sort of communications to the broker

    Parameters:
     - sessionId
     - unitIds
    """
    self.send_submitSort(sessionId, unitIds)
    self.recv_submitSort()

  def send_submitSort(self, sessionId, unitIds):
    self._oprot.writeMessageBegin('submitSort', TMessageType.CALL, self._seqid)
    args = submitSort_args()
    args.sessionId = sessionId
    args.unitIds = unitIds
    args.write(self._oprot)
    self._oprot.writeMessageEnd()
    self._oprot.trans.flush()

  def recv_submitSort(self):
    iprot = self._iprot
    (fname, mtype, rseqid) = iprot.readMessageBegin()
    if mtype == TMessageType.EXCEPTION:
      x = TApplicationException()
      x.read(iprot)
      iprot.readMessageEnd()
      raise x
    result = submitSort_result()
    result.read(iprot)
    iprot.readMessageEnd()
    return


class Processor(concrete.services.Service.Processor, Iface, TProcessor):
  def __init__(self, handler):
    concrete.services.Service.Processor.__init__(self, handler)
    self._processMap["submitSort"] = Processor.process_submitSort

  def process(self, iprot, oprot):
    (name, type, seqid) = iprot.readMessageBegin()
    if name not in self._processMap:
      iprot.skip(TType.STRUCT)
      iprot.readMessageEnd()
      x = TApplicationException(TApplicationException.UNKNOWN_METHOD, 'Unknown function %s' % (name))
      oprot.writeMessageBegin(name, TMessageType.EXCEPTION, seqid)
      x.write(oprot)
      oprot.writeMessageEnd()
      oprot.trans.flush()
      return
    else:
      self._processMap[name](self, seqid, iprot, oprot)
    return True

  def process_submitSort(self, seqid, iprot, oprot):
    args = submitSort_args()
    args.read(iprot)
    iprot.readMessageEnd()
    result = submitSort_result()
    try:
      self._handler.submitSort(args.sessionId, args.unitIds)
      msg_type = TMessageType.REPLY
    except (TTransport.TTransportException, KeyboardInterrupt, SystemExit):
      raise
    except Exception as ex:
      msg_type = TMessageType.EXCEPTION
      logging.exception(ex)
      result = TApplicationException(TApplicationException.INTERNAL_ERROR, 'Internal error')
    oprot.writeMessageBegin("submitSort", msg_type, seqid)
    result.write(oprot)
    oprot.writeMessageEnd()
    oprot.trans.flush()


# HELPER FUNCTIONS AND STRUCTURES

class submitSort_args(object):
  """
  Attributes:
   - sessionId
   - unitIds
  """

  thrift_spec = (
    None, # 0
    (1, TType.STRUCT, 'sessionId', (concrete.uuid.ttypes.UUID, concrete.uuid.ttypes.UUID.thrift_spec), None, ), # 1
    (2, TType.LIST, 'unitIds', (TType.STRUCT,(concrete.services.ttypes.AnnotationUnitIdentifier, concrete.services.ttypes.AnnotationUnitIdentifier.thrift_spec)), None, ), # 2
  )

  def __init__(self, sessionId=None, unitIds=None,):
    self.sessionId = sessionId
    self.unitIds = unitIds

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
        if ftype == TType.STRUCT:
          self.sessionId = concrete.uuid.ttypes.UUID()
          self.sessionId.read(iprot)
        else:
          iprot.skip(ftype)
      elif fid == 2:
        if ftype == TType.LIST:
          self.unitIds = []
          (_etype17, _size14) = iprot.readListBegin()
          for _i18 in xrange(_size14):
            _elem19 = concrete.services.ttypes.AnnotationUnitIdentifier()
            _elem19.read(iprot)
            self.unitIds.append(_elem19)
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
    oprot.writeStructBegin('submitSort_args')
    if self.sessionId is not None:
      oprot.writeFieldBegin('sessionId', TType.STRUCT, 1)
      self.sessionId.write(oprot)
      oprot.writeFieldEnd()
    if self.unitIds is not None:
      oprot.writeFieldBegin('unitIds', TType.LIST, 2)
      oprot.writeListBegin(TType.STRUCT, len(self.unitIds))
      for iter20 in self.unitIds:
        iter20.write(oprot)
      oprot.writeListEnd()
      oprot.writeFieldEnd()
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    return


  def __hash__(self):
    value = 17
    value = (value * 31) ^ hash(self.sessionId)
    value = (value * 31) ^ hash(self.unitIds)
    return value

  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)

class submitSort_result(object):

  thrift_spec = (
  )

  def read(self, iprot):
    if iprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None and fastbinary is not None:
      fastbinary.decode_binary(self, iprot.trans, (self.__class__, self.thrift_spec))
      return
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      else:
        iprot.skip(ftype)
      iprot.readFieldEnd()
    iprot.readStructEnd()

  def write(self, oprot):
    if oprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and self.thrift_spec is not None and fastbinary is not None:
      oprot.trans.write(fastbinary.encode_binary(self, (self.__class__, self.thrift_spec)))
      return
    oprot.writeStructBegin('submitSort_result')
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    return


  def __hash__(self):
    value = 17
    return value

  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)
