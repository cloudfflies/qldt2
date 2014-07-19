#!/usr/bin/env python
# -*- coding: utf8 -*-

import mechanize
import cookielib
from pprint import pprint
import sys



#lấy username và pass
def user_pass():
	global usname 
	global uspass
	txt = open('login.txt', 'r')
	usname = txt.readline()[:-1]
	uspass = txt.readline()[:-1]
	txt.close()
# US username PS password
def dang_nhap(US,PS):
	global br
	#login
	br.open('https://qldt2.neu.edu.vn/cmcsoft.iu.web.info/Login.aspx')
	print ("Đang chạy 1/2")
	br.select_form(nr = 0)
	br.form['txtUserName'] = US
	br.form['txtPassword'] = PS
	resp = br.submit()
	print ("Đang chạy 2/2")
	#check login
	dk = '.: Ðăng ký môn học :.'
	if br.title() == dk:
		print ('Đăng nhập thành công')
		sys.stdout.flush()
	else:
		print('Đăng nhập không thành công, kiểm tra lại mật khẩu và tài khoản')

def get_value(string,location):
	string = string[location:]
	location = string.find(">") + 1
	end = string.find("<")
	return string[location:end]
	
#load trang thư mục điểm	
def tree_group():
	global br
	global data
	#load Thu muc diem
	br.open('https://qldt2.neu.edu.vn/CMCSoft.IU.Web.Info/CourseByFieldTree.aspx') 
	br.select_form(nr = 0)
	#Chọn Kiểm tra tình trạng hoàn thành chương trình học
	br['CTDT'] = ['rdoCheckPassedStageBystu']
	resp = br.submit()
	#
	CreditGroup = []
	resp = resp.read()
	data = data.write(resp)

	
#lấy username và pass	
usname = ""
uspass = ""
user_pass()
#mở file data 
data = open("data.txt","w")
#browser	
br = mechanize.Browser()		

dang_nhap(usname,uspass)
tree_group()

data.close()
