from mock import MockedWebserviceKeywords

__version__ = '0.1'
__author__ = 'Mykhailo Poliarush'

class WebServiceMockLibrary(MockedWebserviceKeywords):
    """
    WebServiceMockLibrary is designed to mock webservices. As for now only soap requests are supported. 
    """
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'