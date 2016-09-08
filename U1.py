# -*- coding:utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')

import time
import soaplib
from soaplib.core.util.wsgi_wrapper import run_twisted #发布服务
from soaplib.core.server import wsgi
from soaplib.core.service import DefinitionBase  #所有服务类必须继承该类
from soaplib.core.service import soap  #声明注解
from soaplib.core.model.clazz import Array #声明要使用的类型
from soaplib.core.model.clazz import ClassModel  #若服务返回类，该返回类必须是该类的子类
from soaplib.core.model.primitive import Integer,String
class C_ProbeCdrModel(ClassModel):
	__namespace__ = "C_ProbeCdrModel"
	Name=String
	Id=Integer
class U1Service(DefinitionBase):  #this is a web service
 	#声明一个服务，标识方法的参数以及返回值
	@soap(Integer,Integer,Integer,_returns=String)
	def compute(self,k1,k2,k3):
		startTime = time.time()
		r = pow(k1,k2,k3)
		endTime = time.time()
		t = (endTime - startTime)*10**3
		k = str(r)+","+str(t)
		return k

if __name__=='_main__':
	soap_app=soaplib.core.Application([U1Service], 'tns')
	wsgi_app=wsgi.Application(soap_app)
	print 'listening on 127.0.0.1:6001'
	print 'wsdl is at: http://127.0.0.1:6001/SOAP/?wsdl'
	run_twisted( ( (wsgi_app, "SOAP"),), 6001)
if __name__=='__main__':  #发布服务
	try:
		print 'U1服务器已经开启!'
		from wsgiref.simple_server import make_server
		soap_application = soaplib.core.Application([U1Service],'tns')
		wsgi_application = wsgi.Application(soap_application)
		server = make_server('localhost', 6001, wsgi_application)
		server.serve_forever()
	except ImportError:
		print 'error'
