from soaplib.wsgi_soap import SimpleWSGISoapApp
from soaplib.service import soapmethod
from soaplib.serializers.clazz import ClassSerializer
from soaplib.serializers.primitive import String, Integer, Array, DateTime
from wsgiref.simple_server import make_server
from robot.api import logger
from suds.client import Client
import threading

class MockedObject(SimpleWSGISoapApp):
    
    @soapmethod(_returns=String,_outVariableName = 'return',_outMessage="invokeMessageResponse")
    def invokeMessageResponse(self):
		return self._text
    
    def _change_response_body(self, text):
        self._text = text

    def _wrap_response_in_soap_body(self, text):
        soap = """\
        <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
           <soap:Body>
              %s
           </soap:Body>
        </soap:Envelope>""" % text       
        self._text = soap

class MockedWebserviceServer(object):
    
    mocked_object = MockedObject()
    
    def __init__(self):
        self.host, self.port, self.server = 'localhost', 7789, None
        
    def _set_host_and_port(self, host, port):
        self.host, self.port = host, port
        
    def _start_server(self):
    	try:
    		self.server = make_server(self.host, int(self.port), self.mocked_object)
    		self.server.serve_forever(poll_interval=0.5) #0.5 need for _stop_server
    	except ImportError:
    		raise Exeption("Error: example server code requires Python >= 2.5")
 
    def _stop_server(self):
		#shutdown server should be in separate thread
		#http://www.gossamer-threads.com/lists/python/python/886482
		threading.Thread(target=self.server.shutdown).start()	

    def _change_response(self,text):
        self.mocked_object._change_response_body(text) 
		
class MockedWebserviceKeywords(object):
    mocked_webservice = MockedWebserviceServer()
    
    def start_server(self, host='localhost', port=7788):
        '''
        Start server with defined `host` and `port`. Server will start in background.
        So once you started server you can do request to webservice.
        
        `start_server` can take two optional parameters
        it sets to host='localhost', port=7788 by default
        
        *Note:* you can easy change response body without server restart by calling keyword `changed_message_body`
        
        _Example:_
        | changed message body |    123 |     | 
        | Start Server  |   localhost |    8890 | 
        | Sleep |    1 seconds    | | 
        | test webservice by call |   |      
        | Sleep |    1 seconds    | | 
        | changed message body |    321 | |      
        | Sleep |     2 seconds    | | 
        | test webservice by call |    |     
        | Stop Server | |        |
        '''
        self._host, self._port = host, port
        self.mocked_webservice._set_host_and_port(host, port)
        thread = threading.Thread(target=self.mocked_webservice._start_server)
        thread.daemon = True
        thread.start()

    def stop_server(self):
        '''
        Stop server started by keyword `start_server`
        '''
        self.mocked_webservice._stop_server()
    
    def changed_message_body(self,text):
        '''
        Change text of response of mocked webservice. It will be plain text. 
        *Note*: If you need soap request please wrap it accordingly
        '''
        self.mocked_webservice._change_response(text)
        
    def test_webservice_by_call(self):
        '''
        Simple method to check that mocked webservice is up and running 
        so you don't need to debug it. Messages are stored as INFO in logs.
        '''
        logger.info(Client("http://%s:%s/?wsdl" % (self._host, self._port)).service.invokeMessageResponse())