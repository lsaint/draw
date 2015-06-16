//! 网络画板应用服务器透传通讯模块
/*! 
 * \file app_srv_module.h
 * \author xuzhijian
  *
 * 广州华多网络科技有限公司 版权所有 (c) 2005-2011 DuoWan.com [多玩游戏]
 */
 
#pragma once
#ifndef _APP_SRV_MODULE_H
#define _APP_SRV_MODULE_H

#include "dsf-logger.h"
#include "dsf-byte-buffer.h"
#include "dsf-string.h"
#include "dsfp.h"
#include "dsf-module-mgr.h"
#include "draw.h"
#include "dsf/appmgr-clt-module-protocol.h"
#include "dsf/yysession-module-protocol.h"
#include "dsf-module.h"
#include "proto/draw.pb.h"
#include "web/yyuserdata-protocol.h"

#include <boost/python/suite/indexing/map_indexing_suite.hpp>
#include <boost/python/suite/indexing/vector_indexing_suite.hpp>

namespace 
{
    const DSFUInt8_t MAX_COMBINED_KEY_LENGTH = 64;

    const DSFString  YYSESSION_MODULE_NAME = _DSF_TEXT("yysession");
    const DSFUInt64_t PY_INTERVAL = 500;

    #define _GET_COMBINE_CHL_ID(arg) *((DSFUInt64_t*)arg) & (((DSFUInt64_t)1 << 32) - 1)
    #define _GET_COMBINE_USR_ID(arg) *((DSFUInt64_t*)arg) >> 32

	#define _REPLY(entity, arg)\
              TransparentSendEntityToUser(\
                *((DSFUInt64_t*)arg) >> 32,\
                *((DSFUInt64_t*)arg) & (((DSFUInt64_t)1 << 32) - 1),\
                entity.uri,\
                entity);

    #define _SEND_PY_TIMMING_ENTITY(lt, entity_type)\
        for (int i=0; i<boost::python::len(lt); i++) \
        {\
            boost::python::tuple tp = extract<boost::python::tuple>(lt[i]);\
            entity_type entity = extract<entity_type>(tp[2]);\
            TransparentSendEntityToUser(extract<DSFUInt32_t>(tp[0]), \
                    extract<DSFUInt32_t>(tp[1]), entity.uri, entity); \
        }

}

typedef std::vector<DSFUInt32_t> Uint32Vector;
typedef std::map<DSFUInt32_t,DSFUInt32_t> UInt32_UInt32_Map;

class AppSrvModule
    :   public  DSFModule
{
public:
	AppSrvModule();

	virtual bool OnLoad();

	virtual void OnUnload()
    {
        ;
    }

	virtual void Destroy()
	{
		delete this;
	}

	virtual ~AppSrvModule()
    {
    }
    
	void TransparentSendEntityToUser(DSFUInt32_t uid, DSFUInt32_t yychannel_id, DSFUInt32_t uri, DSFMarshallable &entity);
    
    void PySendOriginalDataToUser(DSFUInt32_t uid, DSFUInt32_t yychannel_id, std::string original_data);
    
    void PySendOriginalDataToUsers(const Uint32Vector &uid_vec, DSFUInt32_t yychannel_id, std::string original_data);
    
    void PySendPYYSessionGetYYChannelInfoRequest(DSFUInt32_t yychannel_id); //发出频道查询请求
    
    void PyGetAsidBySid( std::string channel_id );
	
	void DrawPyInitRun();
    
    void reg_py_interface(AppSrvModule* _pure_module);
    
private:

    ////////////////////////////////////////////////////////////////////////////////////////////////
    // appmgr client protocols
    ////////////////////////////////////////////////////////////////////////////////////////////////
    bool OnPAppMgrCltLoginResponse(PAppMgrCltLoginResponse *entity, void *arg);  // 登录appmgr回应

    bool OnPAppMgrCltYYChannelCreatedNotify(PAppMgrCltYYChannelCreatedNotify *entity, void *arg); // 一个频道上线并加载应用通知

    bool OnPAppMgrCltSubscriptionNotify(PAppMgrCltSubscriptionNotify *entity, void *arg); // 由前端递送的频道订阅应用的通知(加载应用的通知不应该通过此协议，应该通过上面的协议，因为订阅不代表该频道在线)
    
    bool OnPAppMgrCltUnsubscriptionNotify(PAppMgrCltUnsubscriptionNotify *entity, void *arg);

    
    ///////////////////////////////////////////////////////////////////////////////////////////////
    // yysession protocols
    ///////////////////////////////////////////////////////////////////////////////////////////////
    bool OnPYYSessionAppRegisterResponse(PYYSessionAppRegisterResponse *entity, void *arg);  // 向yysession注册app回应

    //bool OnPYYSessionAddAppToYYChannelResponse(PYYSessionAddAppToYYChannelResponse *entity, void *arg); // 向yysession添加一个应用到指定频道的回应

    bool OnPYYSessionDelAppFromYYChannelResponse(PYYSessionDelAppFromYYChannelResponse *entity, void *arg); // 向yysession从一个指定频道删除应用的回应

    bool OnPYYSessionSendDataToUsersResponse(PYYSessionSendDataToUsersResponse *entity, void *arg); // 向yy频道指定用户发送数据的回应

    bool OnPYYSessionSendDataToAllUsersResponse(PYYSessionSendDataToAllUsersResponse *entity, void *arg); // 向yy频道所有用户发送数据的回应

    bool OnPYYSessionOnYYChannelReset(PYYSessionOnYYChannelReset *entity, void *arg); // yy频道被重置

    bool OnPYYSessionOnNewUsers(PYYSessionOnNewUsers *entity, void *arg); // 有新用户加入频道
    
    bool OnPYYSessionOnRemoveUsers(PYYSessionOnRemoveUsers *entity, void *arg); // 用户退出频道

    bool OnPYYSessionOnUserInfoUpdate(PYYSessionOnUserInfoUpdate *entity, void *arg); // 用户信息更新

    bool OnPYYSessionOnUserSubChannelChange(PYYSessionOnUserSubChannelChange *entity, void *arg); // 用户子频道切换

    bool OnPYYSessionOnSubChannelDelete(PYYSessionOnSubChannelDelete *entity, void *arg); // 子频道被删除

    bool OnPYYSessionOnSubChannelInfoUpdate(PYYSessionOnSubChannelInfoUpdate *entity, void *arg);  // 子频道信息更新

    bool OnPYYSessionOnNewSubChannel(PYYSessionOnNewSubChannel *entity, void *arg); // 新的子频道被创建

    bool OnPYYSessionOnUserRoleUpdate(PYYSessionOnUserRoleUpdate *entity, void *arg); // 用户角色变更

    bool OnPYYSessionOnUserMsg(PYYSessionOnUserMsg *entity, void *arg); // 接收到用户消息

    bool OnPYYSessionOnYYChannelDestroy(PYYSessionOnYYChannelDestroy *entity, void *arg); // 频道被销毁
    
    bool OnPYYSessionGetYYChannelInfoResponse(PYYSessionGetYYChannelInfoResponse *entity, void*arg); //频道查询回应
    
    bool OnPGetAsidBySidRes( PGetAsidBySidRes *entity, void *data);
       
	void DrawPyInitConfig();
	
    virtual bool OnTimeout(DSFUInt64_t tick);
    
    DSFUInt64_t py_timer;
    
    object py_yysession_module;
};
    
typedef boost::shared_ptr<AppSrvModule> PTR_APP_SRV_MODULE;
    
#endif // _APP_SRV_MODULE_H

