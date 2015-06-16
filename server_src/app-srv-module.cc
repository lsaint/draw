//! 网络画板应用服务器透传通讯模块
/*! 
 * \file app_srv_module.cc
 * \author xuzhijian
  *
 * 广州华多网络科技有限公司 版权所有 (c) 2005-2011 DuoWan.com [多玩游戏]
 */

#include <time.h>
#include "app-srv-module.h"
#include "tinyxml.h"
#include <iostream>
#include "c_python_interface.h"

using namespace std;

static void __SendEntityToModule(const DSFString &module_name, DSFUInt32_t uri, DSFMarshallable &entity)
{
    DSFError_t err = DSFSingleton<DSFModuleMgr>::Instance()->SendEntityToModule(module_name, uri, entity);
    if(err != _DSF_NO_ERROR)
    {
        DSFString errmsg;
        DSFGetErrorMsg(err, &errmsg);
        _DSF_WARNING_LOG("appmgr client module can not send entity to module \"%s\", entity service id=%u entity command id=%u"
                         " error=\"%s\"", _DSF_GET_MBS_STR(module_name), _DSF_ENTITY_SERVICE_ID(uri), 
                         _DSF_ENTITY_COMMAND_ID(uri), _DSF_GET_MBS_STR(errmsg));
    }/*
    else
    {
        _DSF_DEBUG_LOG("appmgr client module send entity to module \"%s\" success, entity service id=%u entity command id=%u",
                       _DSF_GET_MBS_STR(module_name), _DSF_ENTITY_SERVICE_ID(uri), _DSF_ENTITY_COMMAND_ID(uri));
    }*/
}

AppSrvModule::AppSrvModule()
{
	//DSFPyInit();
    initc_python_interface();
	DrawPyInitConfig();

    py_timer = 0;
    
    entity_map_.AddEntityMap(this, &AppSrvModule::OnPAppMgrCltLoginResponse);
    entity_map_.AddEntityMap(this, &AppSrvModule::OnPAppMgrCltYYChannelCreatedNotify);
    entity_map_.AddEntityMap(this, &AppSrvModule::OnPAppMgrCltSubscriptionNotify);
    entity_map_.AddEntityMap(this, &AppSrvModule::OnPAppMgrCltUnsubscriptionNotify);

    entity_map_.AddEntityMap(this, &AppSrvModule::OnPYYSessionAppRegisterResponse);
    entity_map_.AddEntityMap(this, &AppSrvModule::OnPYYSessionDelAppFromYYChannelResponse);
    entity_map_.AddEntityMap(this, &AppSrvModule::OnPYYSessionSendDataToUsersResponse);
    entity_map_.AddEntityMap(this, &AppSrvModule::OnPYYSessionSendDataToAllUsersResponse);
    entity_map_.AddEntityMap(this, &AppSrvModule::OnPYYSessionOnYYChannelReset);
    entity_map_.AddEntityMap(this, &AppSrvModule::OnPYYSessionOnNewUsers);
    entity_map_.AddEntityMap(this, &AppSrvModule::OnPYYSessionOnRemoveUsers);
    entity_map_.AddEntityMap(this, &AppSrvModule::OnPYYSessionOnUserInfoUpdate);
    entity_map_.AddEntityMap(this, &AppSrvModule::OnPYYSessionOnUserSubChannelChange);
    entity_map_.AddEntityMap(this, &AppSrvModule::OnPYYSessionOnSubChannelDelete);
    entity_map_.AddEntityMap(this, &AppSrvModule::OnPYYSessionOnSubChannelInfoUpdate);
    entity_map_.AddEntityMap(this, &AppSrvModule::OnPYYSessionOnNewSubChannel);
    entity_map_.AddEntityMap(this, &AppSrvModule::OnPYYSessionOnUserRoleUpdate);
    entity_map_.AddEntityMap(this, &AppSrvModule::OnPYYSessionOnUserMsg);
    entity_map_.AddEntityMap(this, &AppSrvModule::OnPYYSessionOnYYChannelDestroy);
    entity_map_.AddEntityMap(this, &AppSrvModule::OnPYYSessionGetYYChannelInfoResponse);
    
    entity_map_.AddEntityMap(this, &AppSrvModule::OnPGetAsidBySidRes);
}

void AppSrvModule::DrawPyInitRun()
{
    BPL_BEGIN
        py_yysession_module = import("draw.server_src.api_yysession");
        call_method<bool>(py_yysession_module.ptr(), "OnInitSrv");
    BPL_END_ERR_EXIT
}

void AppSrvModule::DrawPyInitConfig()
{
    DEF_PYTHON_MAP_CLASS(UInt32_UInt32_Map);
}

bool AppSrvModule::OnLoad(void)
{
	std::string strAppMgrAppVersion, strAppMgrPassword;
	std::string strPluginVersion, strPluginMinVersion, strPluginMaxVersion, strPluginMd5, strPluginUrl;
    std::string strPluginVersion2, strPluginMinVersion2, strPluginMaxVersion2, strPluginMd52, strPluginUrl2;
	std::string strAppInfoVersion, strAppInfoDesc, strAppInfoFileName, strAppInfoRecommandVersion;
	
	TiXmlDocument ticonfig("draw-srv.xml");
	if( !ticonfig.LoadFile() )
	{
		_DSF_ERROR_LOG("AppSrvModule::OnLoad ticonfig.LoadFile error !");
		return false;
	}
	TiXmlElement* appmgr_object = ticonfig.FirstChildElement("draw-srv")->FirstChildElement("APPMGRINFO");
	strAppMgrAppVersion = appmgr_object->FirstChildElement("APPSRV_VERSION")->GetText();
	strAppMgrPassword = appmgr_object->FirstChildElement("PASSWORD")->GetText();	

	TiXmlElement* plugin_object = ticonfig.FirstChildElement("draw-srv")->FirstChildElement("PLUGIN0");
	strPluginVersion = plugin_object->FirstChildElement("VERSION")->GetText();
	strPluginMinVersion = plugin_object->FirstChildElement("MIN_VERSION")->GetText();
	strPluginMaxVersion = plugin_object->FirstChildElement("MAX_VERSION")->GetText();
	strPluginMd5 = plugin_object->FirstChildElement("MD5")->GetText();
	strPluginUrl = plugin_object->FirstChildElement("URL")->GetText();

	TiXmlElement* plugin_object2 = ticonfig.FirstChildElement("draw-srv")->FirstChildElement("PLUGIN1");
	strPluginVersion2 = plugin_object2->FirstChildElement("VERSION")->GetText();
	strPluginMinVersion2 = plugin_object2->FirstChildElement("MIN_VERSION")->GetText();
	strPluginMaxVersion2 = plugin_object2->FirstChildElement("MAX_VERSION")->GetText();
	strPluginMd52 = plugin_object2->FirstChildElement("MD5")->GetText();
	strPluginUrl2 = plugin_object2->FirstChildElement("URL")->GetText();
    
	TiXmlElement* app_reg_info_object = ticonfig.FirstChildElement("draw-srv")->FirstChildElement("APPREGINFO");
	strAppInfoVersion = app_reg_info_object->FirstChildElement("VERSION")->GetText();
	strAppInfoDesc = app_reg_info_object->FirstChildElement("DESCRIPTION")->GetText();
	strAppInfoFileName = app_reg_info_object->FirstChildElement("APP_FILE_NAME")->GetText();
	strAppInfoRecommandVersion = app_reg_info_object->FirstChildElement("RECOMMAND_VERSION")->GetText();
    
    /*
    //for debug
	strAppMgrAppVersion = "1";
	strAppMgrPassword = "f9xM4Hk";	

	strPluginVersion = "6";
	strPluginMinVersion = "10001";
	strPluginMaxVersion = "10005";
	strPluginMd5 = "a22670c8c749811a628888ba9debc0a6";
	strPluginUrl = "http://222.186.49.42/static/draw/20101_6.7z";

	strAppInfoVersion = "0";
	strAppInfoDesc = "网络画板";
	strAppInfoFileName = "none.dll";
	strAppInfoRecommandVersion = "-2";*/

    

	// 登陆到appmgr
    PAppMgrCltLoginRequest login_req;
    login_req.from_module = GetName();
    login_req.app_id = DRAW_APPID;
    login_req.appsrv_version = atoi(strAppMgrAppVersion.c_str());
    login_req.password = strAppMgrPassword;
    __SendEntityToModule(_APPMGR_CLT_MODULE_NAME, login_req.uri, login_req);

    // 注册到yysession  老架构
    AppYYVersionInfo  yyver;
    yyver.version = atoi(strPluginVersion.c_str());  //plugin.dll
    yyver.min_version = atoi(strPluginMinVersion.c_str());//plugin sdk min
    yyver.max_version = atoi(strPluginMaxVersion.c_str());//plugin sdk max
    yyver.md5 = strPluginMd5;
    yyver.url = strPluginUrl;

    AppYYVersionInfo  yyver2;
    yyver2.version = atoi(strPluginVersion2.c_str());  //plugin.dll
    yyver2.min_version = atoi(strPluginMinVersion2.c_str());//plugin sdk min
    yyver2.max_version = atoi(strPluginMaxVersion2.c_str());//plugin sdk max
    yyver2.md5 = strPluginMd52;
    yyver2.url = strPluginUrl2; 
    
    PYYSessionAppRegisterRequest  reg_req;
    reg_req.from_module = GetName();
    reg_req.app_id = DRAW_APPID;
    reg_req.version = atoi(strAppInfoVersion.c_str());
    reg_req.description = strAppInfoDesc;
    
	reg_req.app_file_name = strAppInfoFileName;
    reg_req.recommand_version = atoi(strAppInfoRecommandVersion.c_str());
    reg_req.yyversions->push_back(yyver);
    reg_req.yyversions->push_back(yyver2);
    
    //reg_req.enable_app_load_mgr = 0;

    __SendEntityToModule(_YYSESSION_MODULE_NAME, reg_req.uri, reg_req);
	
    // =========================================appmgr一期重构，yysession新架构
    PYYSessionAppRegisterRequest2 new_yysession;
    new_yysession.from_module = GetName();
    new_yysession.app_id = DRAW_APPID;
	new_yysession.isp_type = 2;
	new_yysession.disp_flag = 0;
	new_yysession.key = strAppMgrPassword;
	new_yysession.group = 1;
	new_yysession.max_yychannel_count = 15000;
	__SendEntityToModule(_YYSESSION_MODULE_NAME, new_yysession.uri, new_yysession);
    // ================
	
    return true;
}

//! 根据短频道号获取长频道号
void AppSrvModule::PyGetAsidBySid( std::string channel_id )
{
    PGetAsidBySid entity;
    entity.sid = channel_id;
	if( DSFSingleton<DSFModuleMgr>::Instance()->SendEntityToModule(_WEBDB_MODULE_NAME, entity.uri, entity) != _DSF_NO_ERROR )
	{
		_DSF_ERROR_LOG("send a OnPGetAsidBySid to c_python_interface failed!\n");
	}
}

bool AppSrvModule::OnPGetAsidBySidRes( PGetAsidBySidRes *entity, void *data)
{
    BPL_BEGIN 
        call_method<bool>(py_yysession_module.ptr(), "OnPGetAsidBySidRes", 
                entity->sid, entity->asid, entity->status );
    BPL_END
    return true;
}

bool AppSrvModule::OnPAppMgrCltLoginResponse(PAppMgrCltLoginResponse *entity, void *arg)
{
    if(entity->status == _APPMGR_CLT_STATUS_SUCCESS)
    {
        _DSF_INFO_LOG("login to appmgr successed, appid=%u", entity->app_id);
    }
    else if(entity->status == _APPMGR_CLT_STATUS_FAILED)
    {
        _DSF_ERROR_LOG("login to appmgr failed, appid=%u", entity->app_id);
    }

    return true;
}

bool AppSrvModule::OnPAppMgrCltYYChannelCreatedNotify(PAppMgrCltYYChannelCreatedNotify *entity, void *arg)
{
    _DSF_INFO_LOG("Receive a yychannel created notify, appid=%u yychannelid=%u", entity->app_id, entity->yychannel_id);    

    // 添加一个应用到yy频道
    PYYSessionAddAppToYYChannelRequest add_req;
    add_req.from_module = GetName();
    add_req.app_id = DRAW_APPID;
    add_req.yychannel_id = entity->yychannel_id;

    __SendEntityToModule(_YYSESSION_MODULE_NAME, add_req.uri, add_req);

    return true;
}

bool AppSrvModule::OnPAppMgrCltSubscriptionNotify(PAppMgrCltSubscriptionNotify *entity, void *arg)
{
	_DSF_INFO_LOG("Receive a yychannel Subscription notify, appid=%u yychannelid=%u", entity->app_id, entity->yychannel_id);    

    PYYSessionAddAppToYYChannelRequest add_req;
    add_req.from_module = GetName();
    add_req.app_id = DRAW_APPID;
    add_req.yychannel_id = entity->yychannel_id;

    __SendEntityToModule(_YYSESSION_MODULE_NAME, add_req.uri, add_req);

    return true;
}
    
bool AppSrvModule::OnPAppMgrCltUnsubscriptionNotify(PAppMgrCltUnsubscriptionNotify *entity, void *arg)
{
	_DSF_INFO_LOG("Receive a yychannel Unsubscription notify, appid=%u yychannelid=%u", entity->app_id, entity->yychannel_id);    

	PYYSessionDelAppFromYYChannelRequest req;
	req.from_module = GetName();
	req.app_id = entity->app_id;
	req.yychannel_id = entity->yychannel_id;
	__SendEntityToModule(_YYSESSION_MODULE_NAME, req.uri, req);
    return true;
}

bool AppSrvModule::OnPYYSessionAppRegisterResponse(PYYSessionAppRegisterResponse *entity, void *arg)
{
    if(entity->status == _YYSESSION_STATUS_FAILED)
    {
        _DSF_WARNING_LOG("Register app %u failed!", entity->app_id);
    }
    else if(entity->status == _YYSESSION_STATUS_SUCCESS)
    {
        _DSF_INFO_LOG("Register app %u successed!", entity->app_id);
    }
    return true;
}

bool AppSrvModule::OnPYYSessionDelAppFromYYChannelResponse( PYYSessionDelAppFromYYChannelResponse *entity, void *arg)
{
    if ( 1 == entity->status )
    {
        _DSF_WARNING_LOG("OnPYYSessionDelAppFromYYChannelResponse yychn_id=%u DelApp appid=%u failed!", entity->yychannel_id, entity->app_id);
    }
    else if ( 0 == entity->status )
    {
        _DSF_INFO_LOG("OnPYYSessionDelAppFromYYChannelResponse yychn_id=%u DelApp appid=%u ok!", entity->yychannel_id, entity->app_id);
    }
    return true;
}

bool AppSrvModule::OnPYYSessionSendDataToUsersResponse(PYYSessionSendDataToUsersResponse *entity, void *arg)
{
    return true;
}

bool AppSrvModule::OnPYYSessionSendDataToAllUsersResponse(PYYSessionSendDataToAllUsersResponse *entity, void *arg)
{
    return true;
}

bool AppSrvModule::OnPYYSessionOnYYChannelReset(PYYSessionOnYYChannelReset *entity, void *arg)
{
    _DSF_INFO_LOG("yychannel %u Reset", entity->yychannel_id);
    return true;
}


bool AppSrvModule::OnPYYSessionOnNewUsers(PYYSessionOnNewUsers *entity, void *arg)
{
    //_DSF_INFO_LOG("On new users, user count="_DSF_SIZE_T_PRIS" yychannel_id=%u", entity->users->size(), entity->yychannel_id);
    cout<<"C++ OnPYYSessionOnNewUsers"<<endl;
    
    for(std::map<DSFUInt32_t, YYChannelUserInfo>::iterator iter = entity->users->begin(); iter != entity->users->end(); ++iter) {
        //_DSF_INFO_LOG("User:id=%u nick=%s sign=%s sex=%u pid=%u user_jifen=%u member_jifen=%u",
        //              iter->second.uid, _DSF_GET_MBS_STR(iter->second.nick), _DSF_GET_MBS_STR(iter->second.sign),
        //              iter->second.sex, iter->second.pid, iter->second.user_jifen, iter->second.member_jifen);
        //cout<<"*uid "<<iter->second.uid<<" *name "<<_DSF_GET_MBS_STR(iter->second.nick)<<" enter *channel "<<entity->yychannel_id<<endl;
        
        UInt32_UInt32_Map _rolers;
        for( DSFUInt32_t i = 0; i < iter->second.rolers->size(); ++i)
            _rolers[ iter->second.rolers->at(i).yychannel_id ] = iter->second.rolers->at(i).role;
            
        BPL_BEGIN 
            call_method<bool>(py_yysession_module.ptr(), "OnPYYSessionOnNewUsers", 
                    iter->second.uid, entity->yychannel_id, _DSF_GET_MBS_STR(iter->second.nick), _rolers );
        BPL_END
    }

    return true;
}


bool AppSrvModule::OnPYYSessionOnUserInfoUpdate(PYYSessionOnUserInfoUpdate *entity, void *arg)
{
    //_DSF_INFO_LOG("On users info updated, user count="_DSF_SIZE_T_PRIS" yychannel_id=%u", entity->users->size(), entity->yychannel_id);
    //cout<<"C++ OnPYYSessionOnUserInfoUpdate"<<endl;
    
    for(std::map<DSFUInt32_t, YYChannelUserInfo>::iterator iter = entity->users->begin(); iter != entity->users->end(); ++iter) {
        UInt32_UInt32_Map _rolers;
        for( DSFUInt32_t i = 0; i < iter->second.rolers->size(); ++i)
            _rolers[ iter->second.rolers->at(i).yychannel_id ] = iter->second.rolers->at(i).role;
            
        BPL_BEGIN 
            call_method<bool>(py_yysession_module.ptr(), "OnPYYSessionOnUserInfoUpdate", 
                    iter->second.uid, entity->yychannel_id, _DSF_GET_MBS_STR(iter->second.nick), _rolers );
        BPL_END
    }    
    
    return true;
}

bool AppSrvModule::OnPYYSessionOnRemoveUsers(PYYSessionOnRemoveUsers *entity, void *arg)
{
    //_DSF_INFO_LOG("On users remove, user count="_DSF_SIZE_T_PRIS" yychannel_id=%u", entity->users->size(), entity->yychannel_id);
    //cout<<"C++ OnPYYSessionOnRemoveUsers"<<endl;
    for(std::map<DSFUInt32_t, YYChannelUserInfo>::iterator iter = entity->users->begin(); iter != entity->users->end(); ++iter) {
        //cout<<"*uid "<<iter->second.uid<<" *name "<<_DSF_GET_MBS_STR(iter->second.nick)<<" leave *channel "<<entity->yychannel_id<<endl;
        BPL_BEGIN 
            call_method<bool>(py_yysession_module.ptr(), "OnPYYSessionOnRemoveUsers", 
                    iter->second.uid, entity->yychannel_id);
        BPL_END
    }
    return true;
}

bool AppSrvModule::OnTimeout(DSFUInt64_t tick)
{
    //printf("T");
    if (tick >= py_timer)
	{
        BPL_BEGIN
            call_method<bool>(py_yysession_module.ptr(), "OnTimer", py_timer);
        BPL_END
        //printf("\nC++ OnTimeout pyt_timer=%lld DSFGetSysTick=%lld tick=%lld\n", py_timer, DSFGetSysTick(), tick);
        py_timer = tick + PY_INTERVAL;
    }

    return true;
}

bool AppSrvModule::OnPYYSessionOnUserSubChannelChange(PYYSessionOnUserSubChannelChange *entity, void *arg)
{
    //_DSF_INFO_LOG("On users subchannel changned, user count="_DSF_SIZE_T_PRIS" yychannel_id=%u", entity->users->size(), entity->yychannel_id);
    //cout<<"C++ OnPYYSessionOnUserSubChannelChange"<<endl;
    for(std::map<DSFUInt32_t, YYChannelUserInfo>::iterator iter = entity->users->begin(); iter != entity->users->end(); ++iter) {
        //cout<<"*uid "<<iter->second.uid<<" *name "<<_DSF_GET_MBS_STR(iter->second.nick)<<" subchannel change *channel "<<entity->yychannel_id<<endl;
        BPL_BEGIN 
            call_method<bool>(py_yysession_module.ptr(), "OnPYYSessionOnUserSubChannelChange", 
                    iter->second.uid, entity->yychannel_id, iter->second.pid);
        BPL_END
    }
    return true;
}

bool AppSrvModule::OnPYYSessionOnSubChannelDelete(PYYSessionOnSubChannelDelete *entity, void *arg)
{
    //_DSF_INFO_LOG("On subchannel delete, count="_DSF_SIZE_T_PRIS" yychannel_id=%u", entity->sub_channels->size(), entity->yychannel_id);
    //暂时不处理删除子频道的情况，原来已经进入的用户可以继续游戏，但是新用户无法再通过 OnUserSubChannelChange 进入了
    return true;
}

bool AppSrvModule::OnPYYSessionOnSubChannelInfoUpdate(PYYSessionOnSubChannelInfoUpdate *entity, void *arg)
{
    //_DSF_INFO_LOG("On subchannel info updated, count="_DSF_SIZE_T_PRIS" yychannel_id=%u", entity->sub_channels->size(), entity->yychannel_id);
    return true;
}

bool AppSrvModule::OnPYYSessionOnNewSubChannel(PYYSessionOnNewSubChannel *entity, void *arg)
{
    //_DSF_INFO_LOG("On new subchannel added, count="_DSF_SIZE_T_PRIS" yychannel_id=%u", entity->sub_channels->size(), entity->yychannel_id);
    return true;
}

bool AppSrvModule::OnPYYSessionOnUserRoleUpdate(PYYSessionOnUserRoleUpdate *entity, void *arg)
{
    BPL_BEGIN 
        call_method<bool>(py_yysession_module.ptr(), "OnPYYSessionOnUserRoleUpdate", 
            entity->uid, entity->yychannel_id, entity->yysubchannel_id, entity->type, entity->role );
    BPL_END
    return true;
}

bool AppSrvModule::OnPYYSessionOnYYChannelDestroy(PYYSessionOnYYChannelDestroy *entity, void *arg)
{
	_DSF_INFO_LOG("OnPYYSessionOnYYChannelDestroy appid=%u yychn_id=%u", entity->app_id, entity->yychannel_id);

	//通知脚本层逻辑的处理
    BPL_BEGIN 
        call_method<bool>(py_yysession_module.ptr(), "OnPYYSessionOnYYChannelDestroy", 
            entity->yychannel_id );
    BPL_END
	
	/*//通知yysession去除该频道的关注
    PYYSessionDelAppFromYYChannelRequest remove_req;
    remove_req.from_module = GetName();
    remove_req.app_id = DRAW_APPID;
    remove_req.yychannel_id = entity->yychannel_id;
	remove_req.auto_send_notify = 1;  //是否自动发送卸载通知, 1 is true, 0 is false

    __SendEntityToModule(_YYSESSION_MODULE_NAME, remove_req.uri, remove_req);*/
	
    return true;
}

bool AppSrvModule::OnPYYSessionOnUserMsg(PYYSessionOnUserMsg *entity, void *arg)
{
	_DSF_INFO_LOG("Receive a PYYSessionOnUserMsg entity from channel, uid=%u app_id=%u channel=%u\n", entity->uid, entity->app_id, entity->yychannel_id);
	//DSFUInt64_t combine_arg = ( (DSFUInt64_t)entity->uid << 32 ) | (DSFUInt64_t)entity->yychannel_id;
    
    //for debug
    //for(int i = 0; i<entity->msg_data.GetDataCount(); ++i)
    //{
    //    printf("OnUserMsg i=%d, data[%d]=%d\n", i, i, *(entity->msg_data.GetData()+i) );
    //}
    
    std::string s_user_msg = std::string( (const char*)entity->msg_data.GetData(), entity->msg_data.GetDataCount() );
    BPL_BEGIN 
        call_method<bool>(py_yysession_module.ptr(), "OnPYYSessionOnUserMsg", 
            entity->uid, entity->yychannel_id, entity->yysubchannel_id, s_user_msg);
    BPL_END
	//entity_map_.DispatchEntity(entity->msg_data.GetData(), entity->msg_data.GetDataCount(), false, NULL, &combine_arg );
    
    return true;
}

bool AppSrvModule::OnPYYSessionGetYYChannelInfoResponse(PYYSessionGetYYChannelInfoResponse *entity, void*arg)
{
    _DSF_INFO_LOG("Receive a OnPYYSessionGetYYChannelInfoResponse, app_id=%u yychannel_id=%u\n", entity->app_id, entity->yychannel_id);
    
    for( std::map<DSFUInt32_t, YYChannelInfo>::iterator iter = entity->yychannel_info.sub_channel_infos->begin(); iter != entity->yychannel_info.sub_channel_infos->end(); ++iter )
    {
        BPL_BEGIN 
            call_method<bool>(py_yysession_module.ptr(), "OnPYYSessionGetYYChannelInfoResponse", 
                iter->first, iter->second.pid, iter->second.name );
        BPL_END
    }
    
    return true;
}

void AppSrvModule::PySendPYYSessionGetYYChannelInfoRequest(DSFUInt32_t yychannel_id)
{
	PYYSessionGetYYChannelInfoRequest send_req;
	send_req.from_module = GetName();
	send_req.app_id = DRAW_APPID;
	send_req.yychannel_id = yychannel_id;

	__SendEntityToModule(_YYSESSION_MODULE_NAME, send_req.uri, send_req);
}

void AppSrvModule::PySendOriginalDataToUser(DSFUInt32_t uid, DSFUInt32_t yychannel_id, std::string original_data)
{
	//DSFPack pack;
	//pack.Push(uri);
	//entity.Marshal(&pack);
    
    DSFByteBuffer original_data_buf = DSFByteBuffer( (const DSFByte_t *)original_data.c_str(), original_data.size() );
	
    //for debug
    //for(int i = 0; i<original_data_buf.GetDataCount(); ++i)
    //{
    //    printf("Send i=%d, data[%d]=%d\n", i, i, *(original_data_buf.GetData()+i) );
    //}
    
	PYYSessionSendDataToUsersRequest send_req;
	send_req.from_module = GetName();
	send_req.app_id = DRAW_APPID;
	send_req.users->clear();
	send_req.users->push_back(uid);
	send_req.yychannel_id = yychannel_id;
	send_req.data = original_data_buf;

	__SendEntityToModule(_YYSESSION_MODULE_NAME, send_req.uri, send_req);
}

void AppSrvModule::PySendOriginalDataToUsers(const Uint32Vector &uid_vec, DSFUInt32_t yychannel_id, std::string original_data)
{
    DSFByteBuffer original_data_buf = DSFByteBuffer( (const DSFByte_t *)original_data.c_str(), original_data.size() );
    
	PYYSessionSendDataToUsersRequest send_req;
	send_req.from_module = GetName();
	send_req.app_id = DRAW_APPID;
	send_req.users->clear();
	*send_req.users = uid_vec;
	send_req.yychannel_id = yychannel_id;
	send_req.data = original_data_buf;

	__SendEntityToModule(_YYSESSION_MODULE_NAME, send_req.uri, send_req);
}


void AppSrvModule::TransparentSendEntityToUser(DSFUInt32_t uid, DSFUInt32_t yychannel_id, DSFUInt32_t uri, DSFMarshallable &entity)
{
	DSFPack pack;
	pack.Push(uri);
	entity.Marshal(&pack);
	
	PYYSessionSendDataToUsersRequest send_req;
	send_req.from_module = GetName();
	send_req.app_id = DRAW_APPID;
	send_req.users->clear();
	send_req.users->push_back(uid);
	send_req.yychannel_id = yychannel_id;
	send_req.data = *pack.GetBuffer();

	__SendEntityToModule(_YYSESSION_MODULE_NAME, send_req.uri, send_req);
}

void AppSrvModule::reg_py_interface(AppSrvModule* _pure_module)
{
    PTR_APP_SRV_MODULE c_python_interface(_pure_module);
    
    object m = import("DSFP");
    boost::python::api::setattr(m, "c_python_interface", c_python_interface);
}