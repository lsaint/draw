//! webdbģ�飬��Ҫʵ�ֺ�webdb_daemonͨѶ�����Ĺ���
/*! 
 * \file webdb_module.h
 * \author xuzhijian
  *
 * ���ݻ�������Ƽ����޹�˾ ��Ȩ���� (c) 2005-2011 DuoWan.com [������Ϸ]
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
	
    //! ����uid���ͨ��֤
	bool OnPGetUidByAccount( PGetUidByAccount *entity, void *data);
	bool OnPGetUidByAccountRes( PGetUidByAccountRes *entity, void *data);
    
    //! ����uid����û��ǳ�
	bool OnPGetNick( PGetNick *entity, void *data);
	bool OnPGetNickRes( PGetNickRes *entity, void *data);
    
    //! ���ݳ�Ƶ���Ż��Ƶ��ͼ��url
	bool OnPGetSessionLogoUrl( PGetSessionLogoUrl *entity, void *data);
	bool OnPGetSessionLogoUrlRes( PGetSessionLogoUrlRes *entity, void *data);
    
    //! ���ݶ�Ƶ���Ż�ó�Ƶ����
	bool OnPGetSidByAsid( PGetSidByAsid *entity, void *data);
	bool OnPGetSidByAsidRes( PGetSidByAsidRes *entity, void *data);
    
    //! ����uid���imid
	bool OnPGetImidByUid( PGetImidByUid *entity, void *data);
	bool OnPGetImidByUidRes( PGetImidByUidRes *entity, void *data);
    
    //! ���ݳ�Ƶ���Ż�ȡ��Ƶ����
	bool OnPGetAsidBySid( PGetAsidBySid *entity, void *data);
	bool OnPGetAsidBySidRes( PGetAsidBySidRes *entity, void *data);
    
    //! ����uid��ø�uid����ow��Ƶ���б�
	bool OnPGetSessionList( PGetSessionList *entity, void *data);
	bool OnPGetSessionListRes( PGetSessionListRes *entity, void *data);
    
    //! ���ݳ�Ƶ���Ż��Ƶ����
	bool OnPGetSessionNameBySid( PGetSessionNameBySid *entity, void *data);
	bool OnPGetSessionNameBySidRes( PGetSessionNameBySidRes *entity, void *data);
    
    //! ���ݳ�Ƶ���Ż����Ƶ���б�
	bool OnPGetSubChannelList( PGetSubChannelList *entity, void *data);
	bool OnPGetSubChannelListRes( PGetSubChannelListRes *entity, void *data);
    
    //! ������ȡƵ��ͼ��url
	bool OnPBatchGetSessionLogoUrl( PBatchGetSessionLogoUrl *entity, void *data);
	bool OnPBatchGetSessionLogoUrlRes( PBatchGetSessionLogoUrlRes *entity, void *data);
    
    //! �������ݳ�Ƶ���Ż�ȡ��Ƶ����
	bool OnPBatchGetAsids( PBatchGetAsids *entity, void *data);
	bool OnPBatchGetAsidsRes( PBatchGetAsidsRes *entity, void *data);
    
    //! �������ݳ�Ƶ���Ż�ȡƵ����
	bool OnPBatchGetSessionName( PBatchGetSessionName *entity, void *data);
	bool OnPBatchGetSessionNameRes( PBatchGetSessionNameRes *entity, void *data);
    
    //! �ж�uid�Ƿ�ָ����Ƶ���ŵ�ow
	bool OnPValidateSessionOwner( PValidateSessionOwner *entity, void *data);
	bool OnPValidateSessionOwnerRes( PValidateSessionOwnerRes *entity, void *data);
    
    //! ����uid��ȡ�û���Ϣ
	bool OnPGetUserInfo( PGetUserInfo *entity, void *data);
	bool OnPGetUserInfoRes( PGetUserInfoRes *entity, void *data);
    
    //! ���ݳ�Ƶ���ź�uid���鴦��uid�ڸ�Ƶ������Ϣ
	bool OnPGetSessionMemberInfo( PGetSessionMemberInfo *entity, void *data);
	bool OnPGetSessionMemberInfoRes( PGetSessionMemberInfoRes *entity, void *data);
    
    //! ��im�û�����ϵͳ��Ϣ
	bool OnPSendSystemMessage( PSendSystemMessage *entity, void *data);
	bool OnPSendSystemMessageRes( PSendSystemMessageRes *entity, void *data);
    
    DSFUInt64_t _webdb_channel_id;
};

#endif //_webdb_module_H

