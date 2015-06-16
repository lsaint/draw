//! 网络画板draw服务器对外监听模块，实现和客户端通讯
/*! 
 * \file draw_service.h
 * \author xuzhijian
  *
 * 广州华多网络科技有限公司 版权所有 (c) 2005-2011 DuoWan.com [多玩游戏]
 */

#ifndef _DRAW_SERVICE_H
#define _DRAW_SERVICE_H

#include "dsf-module-tcp-server-channel-env.h"
#include "dsf-module-tcp-client-channel-env.h"
#include "dsf-module-channel-factory.h"
#include "dsf-module-channel.h"
#include "dsf-module-mgr.h"
#include "dsf.h"
#include "dsf-pack.h"
#include "dsf-unpack.h"
#include "dsf-module-svc-channel.h"

#include "dsfp.h"

class DrawServiceChannel
    :   public DSFModuleSvcChannel
{
public: 
    //!
    DrawServiceChannel();

	//!
    virtual bool OnTimeout(DSFUInt64_t tick);

	//!
    virtual void OnClose(void);

	//!
	virtual void OnError(const DSFError_t &error);

	//!
    virtual void Destroy(void);

	//!
	virtual bool OnOriginalDataDispatch(const DSFByte_t *data, DSFInt32_t size);
	
    virtual bool OnOpen(void);
private:
    //!
    virtual ~DrawServiceChannel();
};


#define _THIRD_PARTY_APP_SRV_CHANNEL_TYPE_NAME     _DSF_TEXT("third_party_app_channel")

class DrawServiceChannelFactory
    :   public  DSFModuleChannelFactory
{
public:
    //!
    virtual DSFModuleChannel* CreateChannel(const DSFString &channel_name);
};

//_DSF_SINGLETON_INSTANTIATE(DrawServiceChannelFactory);

class DrawServiceModule
    :   public  DSFModule
{
public:
    //!
    DrawServiceModule();

	//!
    virtual bool OnLoad(void);
    
	//!
    virtual void OnUnload(void);

	//!
    virtual void Destroy(void);

	//!
	virtual bool OnOriginalDataDispatch(DSFUInt64_t channel_id, const DSFByte_t *data, DSFInt32_t size);
    
    //!
    void DrawPyInit();
    
    //!
    void OnClientDisconnect(DSFUInt64_t channel_id);
    
    //!
	void SendEntityToAllSVC( const DSFByte_t *data, DSFInt32_t size, DSFUInt64_t except_channel = 0);
    
    //!
    void PySendOriginalDataToChannel(DSFUInt64_t channel_id, std::string data);
    
	std::set<DSFUInt64_t> _all_svc_channel_ids;
	
    //!
    virtual ~DrawServiceModule();
    
private:
    object py_service_module;
};

#endif //_DRAW_SERVICE_H
