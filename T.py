# -*- coding:utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')

import time
from flask import Flask,render_template, session, redirect, url_for,flash
from flask import make_response
from flask import request
from flask.ext.script import Manager
from flask.ext.bootstrap import Bootstrap
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required

from Crypto.Random import random
from Crypto.PublicKey import DSA
from inverse import modinv

from suds.client import Client

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
manager = Manager(app)
bootstrap = Bootstrap(app)
class NameForm(Form):
	submit = SubmitField('提交')
	v = StringField('v的值')
	u1 = StringField('μ的值')  #miu
	p =  StringField('素数p')	
	q = StringField('素数q的值')
	a = StringField('a的值')
	u = StringField('u的值')
	g = StringField('g的值')
	b = StringField('β的值')#beita
	r = StringField('γ的值')
	w = StringField('w的值')
	k = StringField('k的值')
	l = StringField('l的值')
	t1 = StringField('t1的值')
	g_t1 = StringField('g^t1的值')
	t2 = StringField('t2的值')
	g_t2 = StringField('g^t2的值')
	t3 = StringField('t3的值')
	g_t3 = StringField('g^t3的值')

	
	
class settingForm(Form):
	p_len = StringField('请输入p的位数(512 - 1024 bits,间隔64bits)', validators=[Required()])
	time = StringField('请输入测试的次数', validators=[Required()])
	submit = SubmitField('初始化')


class testForm(Form):
	p_len = StringField('请输入p的位数(512 - 1024 bits,间隔64bits)', validators=[Required()])
	a_len = StringField('请输入a的位数(1 - 160 bits)', validators=[Required()])
	submit = SubmitField('初始化')

class resultForm(Form):
	result = StringField('u^a=μ*g^γ*w^k*w^l')
	g_t1 = StringField('U1(t2/t1,g^t1)')
	g_t2 = StringField('U2(t2/t1,g^t1)')
	g_y1 = StringField('U1(γ/t3,g^t3)')
	g_y2 = StringField('U2(γ/t3,g^t3)')
	time_set = StringField('参数设置的时间/ms')
	time_u1send = StringField('U1计算的时间/ms')
	time_u2send = StringField('U2计算的时间/ms')
	time_result = StringField('计算结果的时间/ms')


class u1Form(Form):
	number11 = StringField('发送给U1的g^t1')
	index11 = StringField('发送给U1的t2/t1')
	answer11 = StringField('U1回应的g^t2')
	number21 = StringField('发送给U2的g^t1')
	index21 = StringField('发送给U2的t2/t1')
	answer21 = StringField('U2回应的g^t2')
	number12 = StringField('发送给U1的g^t3')
	index12 = StringField('发送给U1的γ/t3')
	answer12 = StringField('U1回应的g^γ')
	number22 = StringField('发送给U2的g^t3')
	index22 = StringField('发送给U2的γ/t3')
	answer22 = StringField('U2回应的g^γ')
	number13 = StringField('发送给U1的w')
	index13 = StringField('发送给U1的l')
	answer13 = StringField('U1回应的w^l')

	number23 = StringField('发送给U2的w')
	index23 = StringField('发送给U2的k')
	answer23 = StringField('U2回应的w^k')



class testresultForm(Form):
	T_set = StringField('参数设置的时间/ms')
	T_u1 = StringField('U1计算的时间/ms')
	T_u2 = StringField('U2计算的时间/ms')
	T_result = StringField('计算结果的时间/ms')
	
@app.route('/test', methods=['GET', 'POST'])
def testsetting():
	form = settingForm()
	if form.validate_on_submit():
		session['p_len'] = form.p_len.data
		session['time'] = form.time.data
		return redirect(url_for('computing'))

	if 'p_len' in session and 'time' in session:
		form.p_len.data = session['p_len']
		form.time.data = session['time']

	return render_template('test.html',form = form)


@app.route('/computing', methods=['GET', 'POST'])
def computing():
	T_set = T_u1 = T_u2 = T_result = i = 0    #最后T_set/session.get('time')
 	for i in range(0,int(session.get('time'))) :
		session['start_setting'] = time.time()

		p_len = session.get('p_len')
		param = DSA.generate(int(p_len)) 
		p = param.p 
		q = param.q
		#u's order is q
		g = random.randint(2**120,p)     # a base g   
		u = param.g                      #输入u
		a1 = random.randint(2**100,q)    #输入a

		#choose two bind pairs  
		a = random.randint(2**100,q)  # aerfa
		b = random.randint(2**100,q)   #beita
		v = pow(g,a,p)
		u1 = pow(g,b,p)
		session['u1'] = u1


		v1 = modinv(v,p)
		w = u1*v1%p  		    #send U1,U2
		r = (a1*a-b)%q
		k = random.randint(2**50,a) #send U2
		l = (a - k)%q 		    #send U1

		#choose three bind pairs
		t1 = random.randint(2**100,q)
		g_t1 = pow(g,t1,p)
		t2 = random.randint(2**100,q)
		g_t2 = pow(g,t2,p)
		t3 = random.randint(2**100,q)
		g_t3 = pow(g,t3,p)

		t_1 = modinv(t1,q)
		t_3 = modinv(t3,q)

		#send U1 U2
		k1 = g_t1
		k2 = (t2*t_1)%q  
		k3 = g_t3
		k4 = (r*t_3)%q 
		k5 = w
		k6 = l
		k7 = k
		k8 = p
		session['setting_finished'] = time.time()
		session['p'] = p
		session['k1'] = k1
		session['k2'] = k2
		session['k3'] = k3
		session['k4'] = k4
		session['k5'] = k5
		session['k6'] = k6
		session['k7'] = k7
		session['sendu1'] = time.time()
		#send U1 randomly
		U1=Client('http://127.0.0.1:6001/SOAP/?wsdl')
		flag1 = random.randint(1,6)
		if flag1 == 1:
			r1 = U1.service.compute(k1,k2,p)
			k = r1.split(",")
			r11 = long(k[0])
			t11 = float(k[1])
			r2 = U1.service.compute(k3,k4,p)
			k = r2.split(",")
			r12 = long(k[0])
			t12 = float(k[1])
			r3 = U1.service.compute(k5,k6,p)
			k = r3.split(",")
			r13 = long(k[0])
			t13 = float(k[1])
			t_u1 = t11+t12+t13
			session['u1responsed'] = t_u1
		elif flag1 == 2:
			r1 = U1.service.compute(k1,k2,p)
			k = r1.split(",")
			r11 = long(k[0])
			t11 = float(k[1])
			r3 = U1.service.compute(k5,k6,p)
			k = r3.split(",")
			r13 = long(k[0])
			t13 = float(k[1])
			r2 = U1.service.compute(k3,k4,p)
			k = r2.split(",")
			r12 = long(k[0])
			t12 = float(k[1])
			t_u1 = t11+t12+t13
			session['u1responsed'] = t_u1
		elif flag1 == 3:
			r2 = U1.service.compute(k3,k4,p)
			k = r2.split(",")
			r12 = long(k[0])
			t12 = float(k[1])
			r1 = U1.service.compute(k1,k2,p)
			k = r1.split(",")
			r11 = long(k[0])
			t11 = float(k[1])
			r3 = U1.service.compute(k5,k6,p)
			k = r3.split(",")
			r13 = long(k[0])
			t13 = float(k[1])
			t_u1 = t11+t12+t13
			session['u1responsed'] = t_u1
		elif flag1 == 4:
			r2 = U1.service.compute(k3,k4,p)
			k = r2.split(",")
			r12 = long(k[0])
			t12 = float(k[1])
			r3 = U1.service.compute(k5,k6,p)
			k = r3.split(",")
			r13 = long(k[0])
			t13 = float(k[1])
			r1 = U1.service.compute(k1,k2,p)
			k = r1.split(",")
			r11 = long(k[0])
			t11 = float(k[1])
			t_u1 = t11+t12+t13
			session['u1responsed'] = t_u1
		elif flag1 == 5:
			r3 = U1.service.compute(k5,k6,p)
			k = r3.split(",")
			r13 = long(k[0])
			t13 = float(k[1])
			r1 = U1.service.compute(k1,k2,p)
			k = r1.split(",")
			r11 = long(k[0])
			t11 = float(k[1])
			r2 = U1.service.compute(k3,k4,p)
			k = r2.split(",")
			r12 = long(k[0])
			t12 = float(k[1])
			t_u1 = t11+t12+t13
			session['u1responsed'] = t_u1
		else:
			r3 = U1.service.compute(k5,k6,p)
			k = r3.split(",")
			r13 = long(k[0])
			t13 = float(k[1])
			r2 = U1.service.compute(k3,k4,p)
			k = r2.split(",")
			r12 = long(k[0])
			t12 = float(k[1])
			r1 = U1.service.compute(k1,k2,p)
			k = r1.split(",")
			r11 = long(k[0])
			t11 = float(k[1])
			t_u1 = t11+t12+t13
			session['u1responsed'] = t_u1

		#send U2 randomly
		session['sendu2'] = time.time()
		U2=Client('http://127.0.0.1:6002/SOAP/?wsdl')
		flag2 = random.randint(1,6)
		if flag2 == 1:
			r1 = U2.service.compute(k1,k2,p)
			k = r1.split(",")
			r21 = long(k[0])
			t21 = float(k[1])
			r2 = U2.service.compute(k3,k4,p)
			k = r2.split(",")
			r22 = long(k[0])
			t22 = float(k[1])
			r3 = U2.service.compute(k5,k7,p)
			k = r3.split(",")
			r23 = long(k[0])
			t23 = float(k[1])
			t_u2 = t21+t22+t23
			session['u2responsed'] = t_u2
		elif flag2 == 2:
			r1 = U2.service.compute(k1,k2,p)
			k = r1.split(",")
			r21 = long(k[0])
			t21 = float(k[1])
			r3 = U2.service.compute(k5,k7,p)
			k = r3.split(",")
			r23 = long(k[0])
			t23 = float(k[1])
			r2 = U2.service.compute(k3,k4,p)
			k = r2.split(",")
			r22 = long(k[0])
			t22 = float(k[1])
			t_u2 = t21+t22+t23
			session['u2responsed'] = t_u2
		elif flag2 == 3:
			r2 = U2.service.compute(k3,k4,p)
			k = r2.split(",")
			r22 = long(k[0])
			t22 = float(k[1])
			r1 = U2.service.compute(k1,k2,p)
			k = r1.split(",")
			r21 = long(k[0])
			t21 = float(k[1])
			r3 = U2.service.compute(k5,k7,p)
			k = r3.split(",")
			r23 = long(k[0])
			t23 = float(k[1])
			t_u2 = t21+t22+t23
			session['u2responsed'] = t_u2
		elif flag2 == 4:
			r2 = U2.service.compute(k3,k4,p)
			k = r2.split(",")
			r22 = long(k[0])
			t22 = float(k[1])
			r3 = U2.service.compute(k5,k7,p)
			k = r3.split(",")
			r23 = long(k[0])
			t23 = float(k[1])
			r1 = U2.service.compute(k1,k2,p)
			k = r1.split(",")
			r21 = long(k[0])
			t21 = float(k[1])
			t_u2 = t21+t22+t23
			session['u2responsed'] = t_u2
		elif flag2 == 5:
			r3 = U2.service.compute(k5,k7,p)
			k = r3.split(",")
			r23 = long(k[0])
			t23 = float(k[1])
			r1 = U2.service.compute(k1,k2,p)
			k = r1.split(",")
			r21 = long(k[0])
			t21 = float(k[1])
			r2 = U2.service.compute(k3,k4,p)
			k = r2.split(",")
			r22 = long(k[0])
			t22 = float(k[1])
			t_u2 = t21+t22+t23
			session['u2responsed'] = t_u2
		else:
			r3 = U2.service.compute(k5,k7,p)
			k = r3.split(",")
			r23 = long(k[0])
			t23 = float(k[1])
			r2 = U2.service.compute(k3,k4,p)
			k = r2.split(",")
			r22 = long(k[0])
			t22 = float(k[1])
			r1 = U2.service.compute(k1,k2,p)
			k = r1.split(",")
			r21 = long(k[0])
			t21 = float(k[1])
			t_u2 = t21+t22+t23
			session['u2responsed'] = t_u2	

			session['r11'] = r11
			session['r12'] = r12
			session['r13'] = r13
			session['r21'] = r21
			session['r22'] = r22
			session['r23'] = r23

		session['resultstart'] = time.time()
		if (r11 == r21) and (r12 == r22):
			(u1*r12*r13*r23)%p

		session['resultend'] = time.time()
		time_set = (session.get('setting_finished') - session.get('start_setting'))*10**3
		T_set = T_set + time_set
		time_u1send = session.get('u1responsed')
		T_u1 = T_u1 + time_u1send
		time_u2send= session.get('u2responsed')
		T_u2 = T_u2 + time_u2send
		time_result = (session.get('resultend') - session.get('resultstart'))*10**3
		T_result = T_result + time_result
		
	T_set = T_set/float(session.get('time'))
	T_u1 = T_u1/float(session.get('time'))
	T_u2 = T_u2/float(session.get('time') )
	T_result = T_result/float(session.get('time') )
	session['T_set'] = T_set
	session['T_u1'] = T_u1
	session['T_u2'] = T_u2
	session['T_result'] = T_result
	return redirect(url_for('testresult'))

@app.route('/testresult', methods=['GET','POST'])
def testresult():	
 	form = testresultForm()
	
	form.T_set.data = session.get('T_set')
	form.T_u1.data = session.get('T_u1')
	form.T_u2.data = session.get('T_u2')
	form.T_result.data = session.get('T_result')
	return render_template('testresult.html', form=form)

@app.route('/u1', methods=['GET','POST'])
def u1():
	form = u1Form()
	if 'flag1' in session and 'flag2' in session:
		flag1 = session['flag1']
		flag2 = session['flag2']
		if flag1 == 1:
			flash('U1随机调用顺序：U1(t2/t1,g^t1),U1(γ/t3,g^t3),U1(l,w)')
		if flag1 == 2:
			flash('U1随机调用顺序：U1(t2/t1,g^t1),U1(l,w),U1(γ/t3,g^t3)')
		if flag1 == 3:
			flash('U1随机调用顺序：U1(γ/t3,g^t3),U1(t2/t1,g^t1),U1(l,w)')
		if flag1 == 4:
			flash('U1随机调用顺序：U1(γ/t3,g^t3),U1(l,w),U1(t2/t1,g^t1)')
		if flag1 == 5:
			flash('U1随机调用顺序：U1(l,w),U1(t2/t1,g^t1),U1(γ/t3,g^t3)')
		if flag1 == 6:
			flash('U2随机调用顺序：U1(l,w),U1(γ/t3,g^t3),U1(t2/t1,g^t1)')
		if flag2 == 1:
			flash('U2随机调用顺序：U2(t2/t1,g^t1),U2(γ/t3,g^t3),U2(k,w)')
		if flag2 == 2:
			flash('U2随机调用顺序：U2(t2/t1,g^t1),U2(k,w),U2(γ/t3,g^t3)')
		if flag2 == 3:
			flash('U2随机调用顺序：U2(γ/t3,g^t3),U2(t2/t1,g^t1),U2(k,w)')
		if flag2 == 4:
			flash('U2随机调用顺序：U2(γ/t3,g^t3),U2(k,w),U2(t2/t1,g^t1)')
		if flag2 == 5:
			flash('U2随机调用顺序：U2(k,w),U2(t2/t1,g^t1),U2(γ/t3,g^t3)')
		if flag2 == 6:
			flash('U2随机调用顺序：U2(k,w),U2(γ/t3,g^t3),U2(t2/t1,g^t1)')
		form.number11.data = session.get('k1')
		form.index11.data = session.get('k2')
		form.answer11.data = session.get('r11')
		form.number12.data = session.get('k3')
		form.index12.data = session.get('k4')
		form.answer12.data = session.get('r12')	
		form.number13.data = session.get('k5')
		form.index13.data = session.get('k6')
		form.answer13.data = session.get('r13')
		form.number21.data = session.get('k1')
		form.index21.data = session.get('k2')
		form.answer21.data = session.get('r21')
		form.number22.data = session.get('k3')
		form.index22.data = session.get('k4')
		form.answer22.data = session.get('r22')	
		form.number23.data = session.get('k5')
		form.index23.data = session.get('k7')
		form.answer23.data = session.get('r23')
		return render_template('u1.html', form=form)

	return render_template('u1.html',form=form)
	


@app.route('/result', methods=['GET','POST'])
def result():
 	
	form = resultForm()
	r11 = session.get('r11')
	r12 = session.get('r12')
	r13 = session.get('r13')
	r21 = session.get('r21')
	r22 = session.get('r22')
	r23 = session.get('r23')
	u1 = session.get('u1')
	p = session.get('p')
	session['resultstart'] = time.time()
	form.g_t1.data = session.get('r11')
	form.g_t2.data = session.get('r21')
	form.g_y1.data = session.get('r12')
	form.g_y2.data = session.get('r22')
	if (r11 == r21) and (r12 == r22):
		if type(u1) == long :
			form.result.data = (u1*r12*r13*r23)%p
			form.time_set.data = (session.get('setting_finished') - session.get('start_setting'))*10**3
			form.time_u1send.data = session.get('u1responsed')
			form.time_u2send.data = session.get('u2responsed')
			session['resultend'] = time.time()
			form.time_result.data = (session.get('resultend') - session.get('resultstart'))*10**3
			flash('验证正确: g^t2=U1(t2/t1,g^t1)=U2(t2/t1,g^t1) 且 g^γ=U1(γ/t3,g^t3)=U2(γ/t1,g^t3)')
	else:
		flash('验证失败!')
		
	return render_template('result.html', form=form)


@app.route('/param', methods=['GET', 'POST'])
def index():
	
	sp_len = session.get('sp_len')
	a_len = int(session.get('a_len'))
	session['start_setting'] = time.time()
	param = DSA.generate(int(sp_len)) 
	p = param.p 
	q = param.q
	#u's order is q
	g = random.randint(2**120,p)     # a base g   
	u = param.g                      #输入u
	a1 = random.randint(2**a_len,2**(a_len+1))#输入a
	#choose two bind pairs  
	a = random.randint(2**100,q)  # aerfa
	b = random.randint(2**100,q)   #beita
	v = pow(g,a,p)
	u1 = pow(g,b,p)
	session['u1'] = u1


	v1 = modinv(v,p)
	w = u1*v1%p  		    #send U1,U2
	r = (a1*a-b)%q
	k = random.randint(2**50,a) #send U2
	l = (a - k)%q 		    #send U1

	#choose three bind pairs
	t1 = random.randint(2**100,q)
	g_t1 = pow(g,t1,p)
	t2 = random.randint(2**100,q)
	g_t2 = pow(g,t2,p)
	t3 = random.randint(2**100,q)
	g_t3 = pow(g,t3,p)

	t_1 = modinv(t1,q)
	t_3 = modinv(t3,q)

	#send U1 U2
	k1 = g_t1
	k2 = (t2*t_1)%q  
	k3 = g_t3
	k4 = (r*t_3)%q 
	k5 = w
	k6 = l
	k7 = k
	k8 = p
	formdata = NameForm()
	formdata.p.data = p
	formdata.q.data = q
	formdata.w.data = w
	formdata.l.data = l
	formdata.t1.data = t1
	formdata.g_t1.data = g_t1
	formdata.t2.data = t1
	formdata.g_t2.data = g_t1
	formdata.t3.data = t1
	formdata.g_t3.data = g_t1
	formdata.u.data = u
	formdata.u1.data = u1
	formdata.g.data = g
	formdata.a.data = a1
	formdata.v.data = v
	formdata.b.data = b
	formdata.r.data = r
	formdata.k.data = k
	session['setting_finished'] = time.time()
	session['p'] = p
	session['k1'] = k1
	session['k2'] = k2
	session['k3'] = k3
	session['k4'] = k4
	session['k5'] = k5
	session['k6'] = k6
	session['k7'] = k7
	
	if formdata.validate_on_submit():
		session['sendu1'] = time.time()
		#send U1 randomly
		U1=Client('http://127.0.0.1:6001/SOAP/?wsdl')
		flag1 = random.randint(1,6)
		session['flag1'] = flag1
		if flag1 == 1:
			r1 = U1.service.compute(k1,k2,p)
			k = r1.split(",")
			r11 = long(k[0])
			t11 = float(k[1])
			r2 = U1.service.compute(k3,k4,p)
			k = r2.split(",")
			r12 = long(k[0])
			t12 = float(k[1])
			r3 = U1.service.compute(k5,k6,p)
			k = r3.split(",")
			r13 = long(k[0])
			t13 = float(k[1])
			t_u1 = t11+t12+t13
			session['u1responsed'] = t_u1
		elif flag1 == 2:
			r1 = U1.service.compute(k1,k2,p)
			k = r1.split(",")
			r11 = long(k[0])
			t11 = float(k[1])
			r3 = U1.service.compute(k5,k6,p)
			k = r3.split(",")
			r13 = long(k[0])
			t13 = float(k[1])
			r2 = U1.service.compute(k3,k4,p)
			k = r2.split(",")
			r12 = long(k[0])
			t12 = float(k[1])
			t_u1 = t11+t12+t13
			session['u1responsed'] = t_u1
		elif flag1 == 3:
			r2 = U1.service.compute(k3,k4,p)
			k = r2.split(",")
			r12 = long(k[0])
			t12 = float(k[1])
			r1 = U1.service.compute(k1,k2,p)
			k = r1.split(",")
			r11 = long(k[0])
			t11 = float(k[1])
			r3 = U1.service.compute(k5,k6,p)
			k = r3.split(",")
			r13 = long(k[0])
			t13 = float(k[1])
			t_u1 = t11+t12+t13
			session['u1responsed'] = t_u1
		elif flag1 == 4:
			r2 = U1.service.compute(k3,k4,p)
			k = r2.split(",")
			r12 = long(k[0])
			t12 = float(k[1])
			r3 = U1.service.compute(k5,k6,p)
			k = r3.split(",")
			r13 = long(k[0])
			t13 = float(k[1])
			r1 = U1.service.compute(k1,k2,p)
			k = r1.split(",")
			r11 = long(k[0])
			t11 = float(k[1])
			t_u1 = t11+t12+t13
			session['u1responsed'] = t_u1
		elif flag1 == 5:
			r3 = U1.service.compute(k5,k6,p)
			k = r3.split(",")
			r13 = long(k[0])
			t13 = float(k[1])
			r1 = U1.service.compute(k1,k2,p)
			k = r1.split(",")
			r11 = long(k[0])
			t11 = float(k[1])
			r2 = U1.service.compute(k3,k4,p)
			k = r2.split(",")
			r12 = long(k[0])
			t12 = float(k[1])
			t_u1 = t11+t12+t13
			session['u1responsed'] = t_u1
		else:
			r3 = U1.service.compute(k5,k6,p)
			k = r3.split(",")
			r13 = long(k[0])
			t13 = float(k[1])
			r2 = U1.service.compute(k3,k4,p)
			k = r2.split(",")
			r12 = long(k[0])
			t12 = float(k[1])
			r1 = U1.service.compute(k1,k2,p)
			k = r1.split(",")
			r11 = long(k[0])
			t11 = float(k[1])
			t_u1 = t11+t12+t13
			session['u1responsed'] = t_u1
		
		#send U2 randomly
		session['sendu2'] = time.time()
		U2=Client('http://127.0.0.1:6002/SOAP/?wsdl')
		flag2 = random.randint(1,6)
		session['flag2'] = flag2
		if flag2 == 1:
			r1 = U2.service.compute(k1,k2,p)
			k = r1.split(",")
			r21 = long(k[0])
			t11 = float(k[1])
			r2 = U2.service.compute(k3,k4,p)
			k = r2.split(",")
			r22 = long(k[0])
			t12 = float(k[1])
			r3 = U2.service.compute(k5,k7,p)
			k = r3.split(",")
			r23 = long(k[0])
			t13 = float(k[1])
			t_u2 = t11+t12+t13
			session['u2responsed'] = t_u2
		elif flag2 == 2:
			r1 = U2.service.compute(k1,k2,p)
			k = r1.split(",")
			r21 = long(k[0])
			t11 = float(k[1])
			r3 = U2.service.compute(k5,k7,p)
			k = r3.split(",")
			r23 = long(k[0])
			t13 = float(k[1])
			r2 = U2.service.compute(k3,k4,p)
			k = r2.split(",")
			r22 = long(k[0])
			t12 = float(k[1])
			t_u2 = t11+t12+t13
			session['u2responsed'] = t_u2
		elif flag2 == 3:
			r2 = U2.service.compute(k3,k4,p)
			k = r2.split(",")
			r22 = long(k[0])
			t12 = float(k[1])
			r1 = U2.service.compute(k1,k2,p)
			k = r1.split(",")
			r21 = long(k[0])
			t11 = float(k[1])
			r3 = U2.service.compute(k5,k7,p)
			k = r3.split(",")
			r23 = long(k[0])
			t13 = float(k[1])
			t_u2 = t11+t12+t13
			session['u2responsed'] = t_u2
		elif flag2 == 4:
			r2 = U2.service.compute(k3,k4,p)
			k = r2.split(",")
			r22 = long(k[0])
			t12 = float(k[1])
			r3 = U2.service.compute(k5,k7,p)
			k = r3.split(",")
			r23 = long(k[0])
			t13 = float(k[1])
			r1 = U2.service.compute(k1,k2,p)
			k = r1.split(",")
			r21 = long(k[0])
			t11 = float(k[1])
			t_u2 = t11+t12+t13
			session['u2responsed'] = t_u2
		elif flag2 == 5:
			r3 = U2.service.compute(k5,k7,p)
			k = r3.split(",")
			r23 = long(k[0])
			t13 = float(k[1])
			r1 = U2.service.compute(k1,k2,p)
			k = r1.split(",")
			r21 = long(k[0])
			t11 = float(k[1])
			r2 = U2.service.compute(k3,k4,p)
			k = r2.split(",")
			r22 = long(k[0])
			t12 = float(k[1])
			t_u2 = t11+t12+t13
			session['u2responsed'] = t_u2
		else:
			r3 = U2.service.compute(k5,k7,p)
			k = r3.split(",")
			r23 = long(k[0])
			t13 = float(k[1])
			r2 = U2.service.compute(k3,k4,p)
			k = r2.split(",")
			r22 = long(k[0])
			t12 = float(k[1])
			r1 = U2.service.compute(k1,k2,p)
			k = r1.split(",")
			r21 = long(k[0])
			t11 = float(k[1])
			t_u2 = t11+t12+t13
			session['u2responsed'] = t_u2

		session['r11'] = r11
		session['r12'] = r12
		session['r13'] = r13
		session['r21'] = r21
		session['r22'] = r22
		session['r23'] = r23

		return redirect(url_for('result'))


	return render_template('index.html',form=formdata)

	
@app.route('/', methods=['GET', 'POST'])
def setting():
	form = testForm()
	if form.validate_on_submit():
		session['sp_len'] = form.p_len.data
		session['a_len'] = form.a_len.data
		return redirect(url_for('index'))
	if 'sp_len' in session and 'a_len' in session:
		form.p_len.data = session['sp_len']
		form.a_len.data = session['a_len']

	return render_template('setting.html',form = form)

@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
	return render_template('500.html'), 500

if __name__ == '__main__':
	manager.run()

