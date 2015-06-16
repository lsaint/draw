//! webdb模块，主要实现和webdb_daemon通讯交互的功能
/*! 
 * \file webdb_module.h
 * \author xuzhijian
  *
 * 广州华多网络科技有限公司 版权所有 (c) 2005-2011 DuoWan.com [多玩游戏]
 */
#ifndef _webdb_module_H
#define _webdb_module_H

#include "dsf-module-tcp-server-channel-env.h"
#include "dsf-module-tcp-client-channel-env.h"
#include "dsf-module-channel-factory.h"
#include "dsf-module-channel.h"
#include "dsf-module-mgr.h"
#include "dsf.h"
#include "dsf-pack.h"
#include "dsf-unpack.h"
#include "web/yyuserdata-protocol.h"
#include "draw.h"

class WebDbChannel
    :   public DSFModuleChannel
{
public: 
    //!
    WebDbChannel();

	//!
    virtual bool OnTimeout(DSFUInt64_t tick);

	//!
    virtual void OnClose(void);

	//!
	virtual void OnError(const DSFError_t &error);

	//!
    virtual void Destroy(void);
    
    //!
    virtual ~WebDbChannel();
    
private:
    //!
    virtual bool OnEntityDataDispatch(const DSFByte_t *data, DSFInt32_t size, bool bigendian);

private:
	DSFString buffer_;
};

#define _WEBDB_CHANNEL_TYPE_NAME     _DSF_TEXT("webdb_channel")

class WebDbChannelFactory
    :   public  DSFModuleChannelFactory
{
public:
    //!
    virtual DSFModuleChannel* CreateChannel(const DSFString &channel_name);
};

//_DSF_SINGLETON_INSTANTIATE(WebDbChannelFactory);

class WebDbModule
    :   public  DSFModule
{
public:
    //!
    WebDbModule();

	//!
    virtual bool OnLoad(void);
    
	//!
    virtual void OnUnload(void);

	//!
    virtual void Destroy(void);
	
    bool OnEntityDataDispatch(const DSFByte_t *data, DSFInt32_t size, bool bigendian);
    
    //!
    virtual ~WebDbModule();
    
private:
	
    //! 根据uid获得通行证
	bool OnPGetUidByAccount( PGetUidByAccount *entity, void *data);
	bool OnPGetUidByAccountRes( PGetUidByAccountRes *entity, void *data);
    
    //! 根据uid获得用户昵称
	bool OnPGetNick( PGetNick *entity, void *data);
	bool OnPGetNickRes( PGetNickRes *entity, void *data);
    
    //! 根据长频道号获得频道图标url
	bool OnPGetSessionLogoUrl( PGetSessionLogoUrl *entity, void *data);
	bool OnPGetSessionLogoUrlRes( PGetSessionLogoUrlRes *entity, void *data);
    
    //! 根据短频道号获得长频道号
	bool OnPGetSidByAsid( PGetSidByAsid *entity, void *data);
	bool OnPGetSidByAsidRes( PGetSidByAsidRes *entity, void *data);
    
    //! 根据uid获得imid
	bool OnPGetImidByUid( PGetImidByUid *entity, void *data);
	bool OnPGetImidByUidRes( PGetImidByUidRes *entity, void *data);
    
    //! 根据长频道号获取短频道号
	bool OnPGetAsidBySid( PGetAsidBySid *entity, void *data);
	bool OnPGetAsidBySidRes( PGetAsidBySidRes *entity, void *data);
    
    //! 根据uid获得该uid担当ow的频道列表
	bool OnPGetSessionList( PGetSessionList *entity, void *data);
	bool OnPGetSessionListRes( PGetSessionListRes *entity, void *data);
    
    //! 根据长频道号获得频道名
	bool OnPGetSessionNameBySid( PGetSessionNameBySid *entity, void *data);
	bool OnPGetSessionNameBySidRes( PGetSessionNameBySidRes *entity, void *data);
    
    //! 根据长频道号获得子频道列表
	bool OnPGetSubChannelList( PGetSubChannelList *entity, void *data);
	bool OnPGetSubChannelListRes( PGetSubChannelListRes *entity, void *data);
    
    //! 批量获取频道图标url
	bool OnPBatchGetSessionLogoUrl( PBatchGetSessionLogoUrl *entity, void *data);
	bool OnPBatchGetSessionLogoUrlRes( PBatchGetSessionLogoUrlRes *entity, void *data);
    
    //! 批量根据长频道号获取短频道号
	bool OnPBatchGetAsids( PBatchGetAsids *entity, void *data);
	bool OnPBatchGetAsidsRes( PBatchGetAsidsRes *entity, void *data);
    
    //! 批量根据长频道号获取频道名
	bool OnPBatchGetSessionName( PBatchGetSessionName *entity, void *data);
	bool OnPBatchGetSessionNameRes( PBatchGetSessionNameRes *entity, void *data);
    
    //! 判断uid是否指定长频道号的ow
	bool OnPValidateSessionOwner( PValidateSessionOwner *entity, void *data);
	bool OnPValidateSessionOwnerRes( PValidateSessionOwnerRes *entity, void *data);
    
    //! 根据uid获取用户信息
	bool OnPGetUserInfo( PGetUserInfo *entity, void *data);
	bool OnPGetUserInfoRes( PGetUserInfoRes *entity, void *data);
    
    //! 根据长频道号和uid，查处该uid在该频道的信息
	bool OnPGetSessionMemberInfo( PGetSessionMemberInfo *entity, void *data);
	bool OnPGetSessionMemberInfoRes( PGetSessionMemberInfoRes *entity, void *data);
    
    //! 向im用户发送系统信息
	bool OnPSendSystemMessage( PSendSystemMessage *entity, void *data);
	bool OnPSendSystemMessageRes( PSendSystemMessageRes *entity, void *data);
    
    DSFUInt64_t _webdb_channel_id;
};

#endif //_webdb_module_H

