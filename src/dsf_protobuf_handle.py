# -*- coding:utf-8 -*-
import struct

#from twisted.internet.protocol import Protocol
#from twisted.internet import protocol



LEN_BUF = 4
LEN_URI = 4

LEN_HEADER = LEN_BUF + LEN_URI 



class ProtobufMessage(object):

    def __init__(self, body=''):
        self.body = body


    def GetUri(self):
        if len(self.body) < LEN_URI:
            return 0
        (uri,) = struct.unpack('I', self.body[:LEN_URI])
        return uri


    def GetBody(self):
        if len(self.body) < LEN_URI:
            return ''
        return self.body[LEN_URI:]
        


class ProtobufMessageFactory(object):

    type2idx = {}     
    service_id = 0

    def __init__(self, dt, idx):
        self.type2idx = dt
        self.service_id = idx
    
 
    def CombineUri(self, uri):
        return self.service_id * 65536 + uri


    def GetPbUri(self, pb):
        #uri = self.type2idx.get(pb)
        #if not uri:
        uri = self.type2idx.get(pb.DESCRIPTOR.name)
        if not uri:
            return 0
        return self.CombineUri(uri)
     


    def ParseMessage(self, data):
        if len(data) < LEN_URI:
            return None, data
        (length,) = struct.unpack('I', data[:LEN_URI])
        body = data[LEN_URI:length]

        if len(body) == length - LEN_URI:
            data = data[length:]
            msg = ProtobufMessage(body)
            return msg, data
        elif len(body) > length:
            print 'Error ! buff data overflow'
            assert False
        return None, data
        

    def PackMessage(self, pb_ins):
        uri = self.GetPbUri(pb_ins)
        if uri == 0:
            print self.type2idx
            print pb_ins.DESCRIPTOR.name
            #print type(pb_ins) in self.type2idx.keys()
            print "Get Uri Error"
            return
        return "%s%s" % (struct.pack("II", pb_ins.ByteSize() + LEN_HEADER, uri),  pb_ins.SerializeToString())
        

