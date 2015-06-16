#ifndef _C_PYTHON_INTERFACE_H_
#define _C_PYTHON_INTERFACE_H_

BOOST_PYTHON_MODULE(c_python_interface)
{
    //class_< DrawServiceModule, boost::noncopyable >("DrawServiceModule", no_init)
    //    .def("PySendOriginalDataToChannel", &DrawServiceModule::PySendOriginalDataToChannel)
    //;

    class_< AppSrvModule, boost::noncopyable >("AppSrvModule", no_init)
        .def("PySendOriginalDataToUser", &AppSrvModule::PySendOriginalDataToUser)
        .def("PySendOriginalDataToUsers", &AppSrvModule::PySendOriginalDataToUsers)
        .def("PySendPYYSessionGetYYChannelInfoRequest", &AppSrvModule::PySendPYYSessionGetYYChannelInfoRequest)
        .def("PyGetAsidBySid", &AppSrvModule::PyGetAsidBySid)
    ;

    //register_ptr_to_python<PTR_SERVICE_MODULE>();
    register_ptr_to_python<PTR_APP_SRV_MODULE>();
    
    DEF_DSF_STL_ADAPTER(Uint32Vector);
    DEF_PYTHON_VECTOR_CLASS(Uint32Vector);
}

#endif