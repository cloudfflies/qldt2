#!/usr/bin/env python
# -*- coding: utf8 -*-


import mechanize
import cookielib
from pprint import pprint
import sys
from bs4 import BeautifulSoup


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
	br.open(qldt+'cmcsoft.iu.web.info/Login.aspx')
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

	
#load trang thư mục điểm	
def tree_group():
	global br
	#load Thu muc diem
	br.open(qldt+'CMCSoft.IU.Web.Info/CourseByFieldTree.aspx') 
	br.select_form(nr = 0)
	#Chọn Kiểm tra tình trạng hoàn thành chương trình học
	br['CTDT'] = ['rdoCheckPassedStageBystu']
	resp = br.submit()
	#
	resp = resp.read()
	group_sub(resp)
	
#xửa lý trang thư mục điểm 
def group_sub(resp):
	global data
	global br
	resp = BeautifulSoup(resp)
	#tên sinh viên
	UserFullName = resp.find(id ='PageHeader1_lblUserFullName') 
	UserFullName = unicode(UserFullName.string)

	#StageID
	StageId = resp.find(id ='hidStageId')
	StageId = unicode(StageId['value'])

	#StudentID
	StudentId = resp.find(id ='hidStudentId')
	StudentId = unicode(StudentId['value'])

	#tên nghành 
	lblTitle = resp.find(id ='lblTitle')
	lblTitle = unicode(lblTitle.contents[2].string)

	#tên group
	k = resp.find_all(attrs={"onclick":"return OpenPopupList(this);"})

	GroupSubjectName = []
	for line in k:
		GroupSubjectName.append(unicode(line.string))
	
	#group id
	GroupSubjectId = []
	for i in range(2,30):
		k = 'grdField__ctl'+str(i)+'_hidCreditGroupSubjectId'
		try:
			k = str(resp.find_all(id = k)[0]['value'])
			GroupSubjectId.append(k)
		except:
			break

	for GSI in GroupSubjectId:
		address = qldt+'CMCSoft.IU.Web.Info/PopupList/GroupCourseMarkDetail.aspx?CreditGroupId='+GSI+'&StudentId='+StudentId+'&StageId='+StageId
		resp = br.open(address).read()
		sub(resp)
		
def sub(resp):
	resp = BeautifulSoup(resp)
	for i in range(2,30):
		k = 'grdField__ctl'+str(i)+'_'
		try:
			CourseCode = str(resp.find(id = k+'lblCourseCode').string)
			CourseName = unicode(resp.find(id = k+'lblCourseName').string)
			CourseCredit = str(resp.find(id = k+'lblCourseCredit').string)
			Theory = str(resp.find(id = k+'txtTheory').string)
			print CourseCode,CourseName,CourseCredit,Theory
		except:
			break
	
#lấy username và pass	
usname = ""
uspass = ""
qldt = "https://"+"qldt2"+".neu.edu.vn/"
user_pass()
#mở file data 
data = open("data.txt","w")
#browser	
br = mechanize.Browser()		

dang_nhap(usname,uspass)
tree_group()

data.close()
