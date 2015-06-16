# -*- coding:utf-8 -*-
import struct

from draw_pb2 import *


LEN_BUF = 4
LEN_URI = 4

LEN_HEADER = LEN_BUF + LEN_URI 



_PROTOCOL_SERVICE_ID = 101


_name2uri_dict = {
        "dc2ds_login_request"                  :   1,
        "ds2dc_login_response"                 :   2,
        "ds2dc_change_subchannel"              :   3,
        "ds2dc_add_drawer_list"                :   4,
        "ds2dc_remove_drawer_list"             :   5,
        "ds2dc_set_master_drawer"              :   6,
        "dc2ds_master_draw_action"             :   7,
        "ds2dc_draw_action"                    :   8,
        "dc2ds_logout_request"                 :   9,
        "dc2ds_set_master_type_request"        :   10,
        "ds2dc_set_master_type_response"       :   11,
        "ds2dc_set_master_type_notification"   :   12,
        "dc2ds_change_role_request"            :   13,
        "ds2dc_change_role_response"           :   14,
        "ds2dc_change_role_notification"       :   15,
        "ds2dc_change_yyrole_notification"     :   16,
        "dc2ds_chat_request"                   :   17,
        "ds2dc_chat_response"                  :   18,
        "ds2dc_chat_notification"              :   19,
        "dc2ds_config_request"                 :   20,
        "ds2dc_config_response"                :   21,
        "ds2dc_config_notification"            :   22,
        "dc2ds_chat_config_request"            :   23,
        "ds2dc_chat_config_response"           :   24,
        "ds2dc_chat_config_notification"       :   25,
        "dc2ds_ping"                           :   26,
        "ds2dc_quit_notification"              :   27,
        "ds2dc_estimate_state"                 :   28,
        "ds2dc_apply_state"                    :   29,
        "dc2ds_apply_drawer_request"           :   30,
        "ds2dc_apply_drawer_response"          :   31,
        "ds2dc_apply_drawer_notification"      :   32,
        "ds2dc_game_state"                     :   33,
        "ds2dc_first_hit_keyword_notification" :   34,
        "dc2ds_manage_channel_words_request"   :   35,
        "ds2dc_manage_channel_words_response"  :   36,
        "dc2ds_update_channel_words_request"   :   37,
        "ds2dc_update_channel_words_response"  :   38,
        "dc2ds_submit_words_request"           :   39,
        "dc2ds_make_suggestions"               :   40,
        "dc2ds_login_launcher_request"         :   41,
        "dc2ds_login_launcher_response"        :   42,
        "ds2dc_gain_item_notification"         :   43,
        "dc2ds_use_item_request"               :   44,
        "ds2dc_use_item_response"              :   45,
        "ds2dc_use_item_notification"          :   46,
        "dc2ds_get_score_request"              :   47,
        "ds2dc_get_score_response"             :   48,
        "dc2ds_start_action_request"           :   49,
        "ds2dc_start_action_response"          :   50,
        "ds2dc_start_action_notification"      :   51,
        "dc2ds_stop_action_request"            :   52,
        "ds2dc_stop_action_response"           :   53,
        "ds2dc_stop_action_notification"       :   54,
        "ds2dc_chn_action_score_notification"  :   55,
}


def CombineUri(uri, service_id):
    return service_id * 65536 + uri


def GetPbUri(pb):
    uri = _name2uri_dict.get(pb.DESCRIPTOR.name)
    if not uri:
        return 0
    return CombineUri(uri, _PROTOCOL_SERVICE_ID)
 


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

    def ParseMessage(self, data):
        if len(data) < LEN_URI:
            return None, data
        (length,) = struct.unpack('I', data[:LEN_URI])
        body = data[LEN_URI:length]

        print "ParseMessage length = %d, body_len = %d" % (length, len(body) )
        if len(body) == length - LEN_URI:
            data = data[length:]
            msg = ProtobufMessage(body)
            return msg, data
        elif len(body) > length:
            print 'Error ! buff data overflow'
            assert False
        return None, data
        

    def PackMessage(self, pb_ins):
        uri = GetPbUri(pb_ins)
        if uri == 0:
            print pb_ins
            print "Get Uri Error"
            return
        return "%s%s" % (struct.pack("II", pb_ins.ByteSize() + LEN_HEADER, uri),  pb_ins.SerializeToString())
        



class ConnectionHandle():    
    def __init__(self):
        self._msgFactory = ProtobufMessageFactory()
        self._recvBuf = ''
        self._handlers = {}
        self.RegisterMessage()
    
    def RegisterMessage(self):
        pass
        
    def AddHandler(self, pb_class, handler):
        self._handlers[GetPbUri(pb_class)] = (handler, pb_class)
        
    def SendMessage(self, pb_ins):
        self.transport.write(self._msgFactory.PackMessage(pb_ins))
        
    
    def dataReceived(self, uid, yychannel_id, yysubchannel_id, data):
        self._recvBuf += data
        print "dataReceived _recvBuf = %d, data = %d" % (len(self._recvBuf), len(data))
        while True:
            msg, self._recvBuf = self._msgFactory.ParseMessage(self._recvBuf)
            if msg is None:
                break
            self.Dispatch(uid, yychannel_id, yysubchannel_id, msg)
            
    def Dispatch(self, uid, yychannel_id, yysubchannel_id, msg):
        uri = msg.GetUri()
        print "Dispatch uid = %d, yychannel_id = %d, uri = %d" % (uid, yychannel_id, uri)
        if uri <= 0:
            print "dispatch invalid uri"
            return 
        if uri in self._handlers.keys():
            handler, pb_class = self._handlers[uri]
            #self._handlers[uri](msg.GetBody())
            ins = pb_class()
            ins.ParseFromString(msg.GetBody())
            handler(uid, yychannel_id, yysubchannel_id, ins)
        else:
            self.OnUnknownMessage(uid, yychannel_id, yysubchannel_id, msg)
            
    def OnUnknownMessage(self, uid, yychannel_id, yysubchannel_id, msg):
        print "uid = %d, yychannel_id = %d, yysubchannel_id = %d, UnknownMessage message" % (uid, yychannel_id, yysubchannel_id)
        
    def connectionMade(self):
        print "connect succ"



''' 客户端调用本模块的例子
from twisted.internet.protocol import Protocol, ClientFactory
from twisted.internet import protocol
from twisted.internet import reactor

from dsf_protobuf_handle import *   
from user_pb2 import *    #具体protobuf生成的协议
from py_net_board_protocol import *

#////////////////////////////////////////////////////////////////////////////////////////////////////////////////
class TestApplication(ConnectionHandle):
    
    def RegisterMessage(self):
        self.AddHandler(user, self.OnUser)

    def OnUser(self, a_user):
        #a_user = user()
        #a_user.ParseFromString(msg)
        print ("username = %s, password = %s, age = %d\n") % (a_user.username, a_user.password, a_user.age )
        
    def connectionMade(self):
        print "connect succ"

        a_user = user()
        a_user.username = 'pyuser'
        a_user.password = 'pypw'
        a_user.age = 20
        
        self.SendMessage(a_user)
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////
class TestFactory(ClientFactory):
    protocol = TestApplication

#////////////////////////////////////////////////////////////////////////////////////////////////////////////////
        
if __name__ == '__main__':  
    reactor.connectTCP("127.0.0.1", 5100, TestFactory())
    reactor.run()

#######################################################每个进程定义这样一个协议名字和uri对应表文件################

#////////////////////////////////各进程自定义通讯协议

_PROTOCOL_SERVICE_ID = 101

_name2uri_dict = {
    user : 1
}
#/////////////////////////////通用函数

def CombineUri(uri, service_id):
    return service_id * 65536 + uri


def GetPbUri(pb):
    if type(pb) != type(type):
        pb = type(pb)
    uri = _name2uri_dict.get(type(pb))
    if not uri:
        return 0
    return CombineUri(uri, _PROTOCOL_SERVICE_ID)
    
'''

