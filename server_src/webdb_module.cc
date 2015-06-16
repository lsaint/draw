#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <limits.h>
#include <fcntl.h>
#include <signal.h>
#include <sys/resource.h>
#include <sstream>
#include "dsf-logger.h"
#include "webdb_module.h"

WebDbChannel::WebDbChannel()
{
}

bool WebDbChannel::OnTimeout(DSFUInt64_t tick)
{
    return true;
}

void WebDbChannel::OnClose(void)
{
    printf("Channel has closed\n");
}

void WebDbChannel::OnError(const DSFError_t &error)
{
    DSFString errmsg;
    DSFGetErrorMsg(error, &errmsg);
    printf("Channel error=\"%s\"\n", _DSF_GET_MBS_STR(errmsg));
}

void WebDbChannel::Destroy(void)
{
    delete this;
}

WebDbChannel::~WebDbChannel()
{
}

bool WebDbChannel::OnEntityDataDispatch(const DSFByte_t *data, DSFInt32_t size, bool bigendian)
{
    return dynamic_cast<WebDbModule*>(GetModule())->OnEntityDataDispatch(data, size, bigendian);
}

DSFModuleChannel* WebDbChannelFactory::CreateChannel(const DSFString &channel_name)
{
    if(_WEBDB_CHANNEL_TYPE_NAME == channel_name)
    {
        return new WebDbChannel;
    }
    else
    {
        return NULL;
    }
}

WebDbModule::WebDbModule():_webdb_channel_id(0)
{
	 entity_map_.AddEntityMap(this, &WebDbModule::OnPGetUidByAccount);
     entity_map_.AddEntityMap(this, &WebDbModule::OnPGetUidByAccountRes);
     entity_map_.AddEntityMap(this, &WebDbModule::OnPGetNick);
     entity_map_.AddEntityMap(this, &WebDbModule::OnPGetNickRes);
	 entity_map_.AddEntityMap(this, &WebDbModule::OnPGetSessionLogoUrl);
     entity_map_.AddEntityMap(this, &WebDbModule::OnPGetSessionLogoUrlRes);
     entity_map_.AddEntityMap(this, &WebDbModule::OnPGetSidByAsid);
     entity_map_.AddEntityMap(this, &WebDbModule::OnPGetSidByAsidRes);
	 entity_map_.AddEntityMap(this, &WebDbModule::OnPGetImidByUid);
     entity_map_.AddEntityMap(this, &WebDbModule::OnPGetImidByUidRes);
     entity_map_.AddEntityMap(this, &WebDbModule::OnPGetAsidBySid);
     entity_map_.AddEntityMap(this, &WebDbModule::OnPGetAsidBySidRes);
	 entity_map_.AddEntityMap(this, &WebDbModule::OnPGetSessionList);
     entity_map_.AddEntityMap(this, &WebDbModule::OnPGetSessionListRes);
     entity_map_.AddEntityMap(this, &WebDbModule::OnPGetSessionNameBySid);
     entity_map_.AddEntityMap(this, &WebDbModule::OnPGetSessionNameBySidRes);
	 entity_map_.AddEntityMap(this, &WebDbModule::OnPGetSubChannelList);
     entity_map_.AddEntityMap(this, &WebDbModule::OnPGetSubChannelListRes);
     entity_map_.AddEntityMap(this, &WebDbModule::OnPBatchGetSessionLogoUrl);
     entity_map_.AddEntityMap(this, &WebDbModule::OnPBatchGetSessionLogoUrlRes);
	 entity_map_.AddEntityMap(this, &WebDbModule::OnPBatchGetAsids);
     entity_map_.AddEntityMap(this, &WebDbModule::OnPBatchGetAsidsRes);
     entity_map_.AddEntityMap(this, &WebDbModule::OnPBatchGetSessionName);
     entity_map_.AddEntityMap(this, &WebDbModule::OnPBatchGetSessionNameRes);
	 entity_map_.AddEntityMap(this, &WebDbModule::OnPValidateSessionOwner);
     entity_map_.AddEntityMap(this, &WebDbModule::OnPValidateSessionOwnerRes);
     entity_map_.AddEntityMap(this, &WebDbModule::OnPGetUserInfo);
     entity_map_.AddEntityMap(this, &WebDbModule::OnPGetUserInfoRes);
	 entity_map_.AddEntityMap(this, &WebDbModule::OnPGetSessionMemberInfo);
     entity_map_.AddEntityMap(this, &WebDbModule::OnPGetSessionMemberInfoRes);
     entity_map_.AddEntityMap(this, &WebDbModule::OnPSendSystemMessage);
     entity_map_.AddEntityMap(this, &WebDbModule::OnPSendSystemMessageRes);
}

bool WebDbModule::OnLoad(void)
{	
    DSFModuleTcpClientChannelEnv *tcp_clt_env = new DSFModuleTcpClientChannelEnv();
    tcp_clt_env->SetChannelFactory(DSFSingleton<WebDbChannelFactory>::Instance());
    tcp_clt_env->SetRemoteHost(_DSF_TEXT("webdb.yy.com"));
    tcp_clt_env->SetRemotePort(_DSF_TEXT("9011"));
    tcp_clt_env->SetReconnectTimeout(300);
    tcp_clt_env->SetReconnectMaxCount(1000);
    
    _webdb_channel_id = CreateTcpClientChannel(tcp_clt_env, _WEBDB_CHANNEL_TYPE_NAME, DSFModuleChannel::ENTITY_DATA_DISP);
    if( _webdb_channel_id == (DSFUInt64_t)-1 )
    {
        tcp_clt_env->Destroy();
        printf("webdb_channel error !\n");
        return false;
    }

    printf("webdb_channel ok !!\n");
    return true;
}

void WebDbModule::OnUnload(void)
{
    // 模块卸载时回调
}

void WebDbModule::Destroy(void)
{
    delete this;
}

WebDbModule::~WebDbModule()
{
}

bool WebDbModule::OnEntityDataDispatch(const DSFByte_t *data, DSFInt32_t size, bool bigendian)
{
    bool res = true;
    return (entity_map_.DispatchEntity(data, size, bigendian, &res) && res);
}

//! 根据uid获得通行证
bool WebDbModule::OnPGetUidByAccount( PGetUidByAccount *entity, void *data)
{
    return true;
}

bool WebDbModule::OnPGetUidByAccountRes( PGetUidByAccountRes *entity, void *data)
{
    return true;
}

//! 根据uid获得用户昵称
bool WebDbModule::OnPGetNick( PGetNick *entity, void *data)
{
    return true;
}

bool WebDbModule::OnPGetNickRes( PGetNickRes *entity, void *data)
{
    return true;
}

//! 根据长频道号获得频道图标url
bool WebDbModule::OnPGetSessionLogoUrl( PGetSessionLogoUrl *entity, void *data)
{
    return true;
}

bool WebDbModule::OnPGetSessionLogoUrlRes( PGetSessionLogoUrlRes *entity, void *data)
{
    return true;
}

//! 根据长频道号获得短频道号
bool WebDbModule::OnPGetSidByAsid( PGetSidByAsid *entity, void *data)
{
    return true;
}

bool WebDbModule::OnPGetSidByAsidRes( PGetSidByAsidRes *entity, void *data)
{
    return true;
}

//! 根据uid获得imid
bool WebDbModule::OnPGetImidByUid( PGetImidByUid *entity, void *data)
{
    return true;
}

bool WebDbModule::OnPGetImidByUidRes( PGetImidByUidRes *entity, void *data)
{
    return true;
}

//! 根据长频道号获取短频道号
bool WebDbModule::OnPGetAsidBySid( PGetAsidBySid *entity, void *data)
{
    if ( _webdb_channel_id && _webdb_channel_id != (DSFUInt64_t)-1 )
    {
        printf("WebDbModule::OnPGetAsidBySid send entity sid=[%s]\n",entity->sid.c_str());
        SendEntityToChannel(_webdb_channel_id, entity->uri, *entity);
    }
    return true;
}

bool WebDbModule::OnPGetAsidBySidRes( PGetAsidBySidRes *entity, void *data)
{
	if( DSFSingleton<DSFModuleMgr>::Instance()->SendEntityToModule(_APPSRV_MODULE_NAME, entity->uri, *entity) != _DSF_NO_ERROR )
	{
		_DSF_ERROR_LOG("send a OnPGetAsidBySidRes to appsrv_module failed!\n");
	}
    return true;
}

//! 根据uid获得该uid担当ow的频道列表
bool WebDbModule::OnPGetSessionList( PGetSessionList *entity, void *data)
{
    return true;
}

bool WebDbModule::OnPGetSessionListRes( PGetSessionListRes *entity, void *data)
{
    return true;
}


//! 根据长频道号获得频道名
bool WebDbModule::OnPGetSessionNameBySid( PGetSessionNameBySid *entity, void *data)
{
    return true;
}

bool WebDbModule::OnPGetSessionNameBySidRes( PGetSessionNameBySidRes *entity, void *data)
{
    return true;
}

//! 根据长频道号获得子频道列表
bool WebDbModule::OnPGetSubChannelList( PGetSubChannelList *entity, void *data)
{
    return true;
}

bool WebDbModule::OnPGetSubChannelListRes( PGetSubChannelListRes *entity, void *data)
{
    return true;
}

//! 批量获取频道图标url
bool WebDbModule::OnPBatchGetSessionLogoUrl( PBatchGetSessionLogoUrl *entity, void *data)
{
    return true;
}

bool WebDbModule::OnPBatchGetSessionLogoUrlRes( PBatchGetSessionLogoUrlRes *entity, void *data)
{
    return true;
}

//! 批量根据长频道号获取短频道号
bool WebDbModule::OnPBatchGetAsids( PBatchGetAsids *entity, void *data)
{
    return true;
}

bool WebDbModule::OnPBatchGetAsidsRes( PBatchGetAsidsRes *entity, void *data)
{
    return true;
}

//! 批量根据长频道号获取频道名
bool WebDbModule::OnPBatchGetSessionName( PBatchGetSessionName *entity, void *data)
{
    return true;
}

bool WebDbModule::OnPBatchGetSessionNameRes( PBatchGetSessionNameRes *entity, void *data)
{
    return true;
}

//! 判断uid是否指定长频道号的ow
bool WebDbModule::OnPValidateSessionOwner( PValidateSessionOwner *entity, void *data)
{
    return true;
}

bool WebDbModule::OnPValidateSessionOwnerRes( PValidateSessionOwnerRes *entity, void *data)
{
    return true;
}

//! 根据uid获取用户信息
bool WebDbModule::OnPGetUserInfo( PGetUserInfo *entity, void *data)
{
    return true;
}

bool WebDbModule::OnPGetUserInfoRes( PGetUserInfoRes *entity, void *data)
{
    return true;
}

//! 根据长频道号和uid，查处该uid在该频道的信息
bool WebDbModule::OnPGetSessionMemberInfo( PGetSessionMemberInfo *entity, void *data)
{
    return true;
}

bool WebDbModule::OnPGetSessionMemberInfoRes( PGetSessionMemberInfoRes *entity, void *data)
{
    return true;
}

//! 向im用户发送系统信息
bool WebDbModule::OnPSendSystemMessage( PSendSystemMessage *entity, void *data)
{
    return true;
}

bool WebDbModule::OnPSendSystemMessageRes( PSendSystemMessageRes *entity, void *data)  
{
    return true;
}
