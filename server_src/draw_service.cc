//! 网络画板draw服务器对外监听模块，实现和客户端通讯
/*! 
 * \file draw_service.cc
 * \author xuzhijian
  *
 * 广州华多网络科技有限公司 版权所有 (c) 2005-2011 DuoWan.com [多玩游戏]
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <signal.h>
#include <sys/resource.h>
#include "draw.h"
#include "draw_service.h"
#include "tinyxml.h"


DrawServiceChannel::DrawServiceChannel()
{	
}

bool DrawServiceChannel::OnTimeout(DSFUInt64_t tick)
{
    return true;
}

void DrawServiceChannel::OnClose(void)
{
    DrawServiceModule* draw_service_module = dynamic_cast<DrawServiceModule*>(GetModule());
	draw_service_module->_all_svc_channel_ids.erase( GetId() );
    draw_service_module->OnClientDisconnect( GetId() );
    printf("Channel has closed\n");
}

void DrawServiceChannel::OnError(const DSFError_t &error)
{
    DSFString errmsg;
    DSFGetErrorMsg(error, &errmsg);
    printf("Channel error=\"%s\"", _DSF_GET_MBS_STR(errmsg));
}

void DrawServiceChannel::Destroy(void)
{
    delete this;
}

DrawServiceChannel::~DrawServiceChannel()
{
}

bool DrawServiceChannel::OnOriginalDataDispatch(const DSFByte_t *data, DSFInt32_t size)
{
    DrawServiceModule* module = dynamic_cast<DrawServiceModule*>(GetModule());
    module->OnOriginalDataDispatch(GetId(), data, size );
	
    return true;
}

bool DrawServiceChannel::OnOpen(void)
{
	dynamic_cast<DrawServiceModule*>(GetModule())->_all_svc_channel_ids.insert( GetId() );
    return true;
}

DSFModuleChannel* DrawServiceChannelFactory::CreateChannel(const DSFString &channel_name)
{
    if(_THIRD_PARTY_APP_SRV_CHANNEL_TYPE_NAME == channel_name)
    {
        return new DrawServiceChannel;
    }
    else
    {
        return NULL;
    }
}

DrawServiceModule::DrawServiceModule()
{
    DrawPyInit();
}

void DrawServiceModule::SendEntityToAllSVC( const DSFByte_t *data, DSFInt32_t size, DSFUInt64_t except_channel)
{
	_DSF_INFO_LOG("DrawServiceModule receive size=%d svc_size=%d\n", size, _all_svc_channel_ids.size());
	for( std::set<DSFUInt64_t>::const_iterator iter = _all_svc_channel_ids.begin(); iter != _all_svc_channel_ids.end(); ++iter)
	{
        if ( except_channel == *iter )
            continue;
		if( SendOriginalDataToChannel(*iter, data, size) != _DSF_NO_ERROR )
			_DSF_INFO_LOG("SendEntityToSVC error size=%d channelid=%llu\n", size, *iter);
		else
			_DSF_INFO_LOG("SendEntityToSVC ok size=%d channelid=%llu\n", size, *iter);
	}
}

bool DrawServiceModule::OnLoad(void)
{
    DSFModuleTcpServerChannelEnv *tcp_svc_env = new DSFModuleTcpServerChannelEnv();
    tcp_svc_env->SetChannelFactory(DSFSingleton<DrawServiceChannelFactory>::Instance());
    tcp_svc_env->SetBindPort(_DSF_TEXT("5100"));
    tcp_svc_env->SetTimeout(45);
	if(CreateTcpServerChannel(tcp_svc_env, _THIRD_PARTY_APP_SRV_CHANNEL_TYPE_NAME,DSFModuleChannel::ORIGINAL_DATA_DISP ) != _DSF_NO_ERROR)
    {
        tcp_svc_env->Destroy();
        return false;
    }
    return true;
}

void DrawServiceModule::OnClientDisconnect(DSFUInt64_t channel_id)
{
    BPL_BEGIN 
        call_method<bool>(py_service_module.ptr(), "OnClientDisconnect", 
            channel_id);
    BPL_END
}

void DrawServiceModule::PySendOriginalDataToChannel(DSFUInt64_t channel_id, std::string data)
{
    SendOriginalDataToChannel( channel_id, (const DSFByte_t *)data.c_str() , data.size() );
    
    //for debug
    //SendEntityToAllSVC( (const DSFByte_t *)data.c_str() , data.size(), channel_id);
}

bool DrawServiceModule::OnOriginalDataDispatch(DSFUInt64_t channel_id, const DSFByte_t *data, DSFInt32_t size)
{
    //for debug
    //for( int i = 0; i<size; ++i)
    //{
    //    printf("OnOriginalDataDispatch i=%d, data[%d]=%d\n" , i, i, *(data+i) );
    //}
    
    std::string *s_data = new std::string((const char *)data, size);
    
    BPL_BEGIN 
        call_method<bool>(py_service_module.ptr(), "OnDrawClientMsg", 
            channel_id, *s_data, size);
    BPL_END
      
    delete s_data;
      
    return true;
}

void DrawServiceModule::OnUnload(void)
{
    // 模块卸载时回调
}

void DrawServiceModule::Destroy(void)
{
    delete this;
}

DrawServiceModule::~DrawServiceModule()
{
}

void DrawServiceModule::DrawPyInit()
{
    BPL_BEGIN
        py_service_module = import("draw.server_src.api_service");
    BPL_END_ERR_EXIT
}