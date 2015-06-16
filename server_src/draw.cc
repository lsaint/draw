#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <signal.h>
#include <sys/resource.h>
#include "draw_service.h"
#include "webdb_module.h"
#include "dsf.h"
#include "app-srv-module.h"
#include "draw.h"

#include "dsfp.h"

int daemonize()
{
	int fd;

	switch(fork())
	{
		case -1 :
			return -1;
		case 0 :
			break;
		default :
			exit(1);
	}
	
	if (setsid() == -1)
	{
		return -1;
	}

	fd = open("/dev/null", O_RDWR, 0);
	if (fd)
	{
		(void) dup2(fd, STDIN_FILENO);
		(void) dup2(fd, STDOUT_FILENO);
		(void) dup2(fd, STDERR_FILENO);
		if (fd > STDERR_FILENO)
		{
			(void) close(fd);
		}
	}
	
	return 0;
}

static void sig_handler(const int sig)
{
    object py_yysession_module;
    BPL_BEGIN
        py_yysession_module = import("draw.server_src.api_yysession");
        call_method<bool>(py_yysession_module.ptr(), "OnPYYSessionOnPreHalt" );
    BPL_END_ERR_EXIT

	return;
}
void set_sig() {
	struct sigaction *sa = (struct sigaction *) malloc(sizeof(struct sigaction));
	
	signal(SIGINT, sig_handler);
	signal(SIGTERM, sig_handler);
	signal(SIGQUIT, sig_handler);
	//signal(SIGKILL, sig_handler);

	sa->sa_handler = SIG_IGN;
	sa->sa_flags = 0;
	signal(SIGPIPE, SIG_IGN);
	if (sigemptyset(&sa->sa_mask) == -1 || sigaction(SIGPIPE, sa, 0) == -1)
	{
		fprintf(stderr, "Ignore SIGPIPE failed\n");
		exit(DSF_SYSTEM_ERROR);
	}

	return;
}

void set_rlimit()
{
	struct rlimit rlim, rlim_new;
	
	if (0 == getrlimit(RLIMIT_CORE, &rlim))
	{
		rlim_new.rlim_cur = rlim_new.rlim_max = RLIM_INFINITY;

		if (0 != setrlimit(RLIMIT_CORE, &rlim_new))
		{
			rlim_new.rlim_cur = rlim_new.rlim_max = rlim.rlim_max;
			(void) setrlimit(RLIMIT_CORE, &rlim_new);

			fprintf(stderr, "Set rlimit max error, default max value will be used\n");
		}
	}

	if (0 != getrlimit(RLIMIT_CORE, &rlim) || rlim.rlim_cur == 0)
	{
		fprintf(stderr, "Failed to ensure core file creation\n");

		exit(DSF_SYSTEM_ERROR);
	}

	if (0 != getrlimit(RLIMIT_NOFILE, &rlim))
	{
		fprintf(stderr, "Failed to getrlimit number of files\n");

		exit(DSF_SYSTEM_ERROR);
	}

	else
	{
		unsigned int maxfiles = 20000;

		if (rlim.rlim_cur < maxfiles + 3)
		{
			rlim.rlim_cur = maxfiles + 3;
		}

		if (rlim.rlim_max < rlim.rlim_cur)
		{
			if (0 == getuid() || 0 == geteuid())
			{
				fprintf(stderr, "Increase NOFILE hard_limit from %d to %d\n", (int) rlim.rlim_max, (int) rlim.rlim_cur);
				rlim.rlim_max = rlim.rlim_cur;
			}

			else
			{
				fprintf(stderr, "You cannot modify NOFILE hard_limit out of superuser privilege\n");
				rlim.rlim_cur = rlim.rlim_max;
			}
		}

		if (0 != setrlimit(RLIMIT_NOFILE, &rlim))
		{
			fprintf(stderr, "Failed to set rlimit for open files, try root privilege.\n");

			exit(DSF_SYSTEM_ERROR);
		}
	}
	
	return;
}

int main(int argc, char *argv[])
{
    if(DSFInit() != _DSF_NO_ERROR)
    {
    	printf("DSFInit error\n");
        return 1;
    }
    else
        printf("DSFInit ok\n");
        
    DSFPyInit();
    //daemonize();
	
	set_sig();
    printf("set_sig ok\n");

	set_rlimit();
    printf("st_rlimit ok\n");
	
    DSFSingleton<DSFLogger>::Instance()->RegisterWriter(new DSFNormalLoggerWriter());

    // 初始化模块管理器
    if(DSFSingleton<DSFModuleMgr>::Instance()->Init() != _DSF_NO_ERROR)
    {
        printf("Module mgr init error\n");
        return 1;
    }
    else
        printf("Module mgr init ok\n");
				
    if(DSFSingleton<DSFModuleMgr>::Instance()->Register("dsf_modules/appmgr_clt.so",_APPMGR_CLT_MODULE_NAME) != _DSF_NO_ERROR)
    {
		printf("AppMgrCltModule register error\n");
        return 1;
    }
    else
        printf("AppMgrCltModule register ok\n");

	if(DSFSingleton<DSFModuleMgr>::Instance()->Register("dsf_modules/yysession.so",_YYSESSION_MODULE_NAME) != _DSF_NO_ERROR)
    {
		printf("YYSessionModule register error\n");
        return 1;
    }
    else
        printf("YYSessionModule register ok\n");
	
       
    /*PTR_SERVICE_MODULE drawservice_module(new DrawServiceModule);
    boost::python::api::setattr(m, "drawservice_module", drawservice_module);
    drawservice_module->SetName(_DRAW_SERVICE_MODULE_NAME);
    if(DSFSingleton<DSFModuleMgr>::Instance()->Register(drawservice_module.get()) != _DSF_NO_ERROR)
    {
        drawservice_module->Destroy();
		printf("DrawServiceModule register error\n");
        return 1;
    }
    else
        printf("DrawServiceModule register ok\n");*/

    AppSrvModule* appsrv_module = new AppSrvModule();
    appsrv_module->reg_py_interface( appsrv_module );
    appsrv_module->SetName(_APPSRV_MODULE_NAME);
    if(DSFSingleton<DSFModuleMgr>::Instance()->Register(appsrv_module) != _DSF_NO_ERROR)
    {
        appsrv_module->Destroy();
		printf("AppSrvModule register error\n");
        return 1;
    }
    else
        printf("AppSrvModule register ok\n");
	
    /*WebDbModule *webdb_module = new WebDbModule;
    webdb_module->SetName(_WEBDB_MODULE_NAME);
    if(DSFSingleton<DSFModuleMgr>::Instance()->Register(webdb_module) != _DSF_NO_ERROR)
    {
        webdb_module->Destroy();
		printf("WebDbModule register error\n");
        return 1;
    }
    else
        printf("WebDbModule register ok\n");
   */ 
	//所有模块都载入后才能运行
	appsrv_module->DrawPyInitRun();
	
	printf("Draw App Server Start !\n");
    DSFSingleton<DSFModuleMgr>::Instance()->RunLoop();
}
