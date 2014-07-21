#!/usr/bin/env python
# -*- coding: utf8 -*-


import mechanize
import cookielib
from pprint import pprint
import sys
from BeautifulSoup import BeautifulSoup



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
	print ("Dang vao qldt2")
	br.select_form(nr = 0)
	br.form['txtUserName'] = US
	br.form['txtPassword'] = PS
	resp = br.submit()
	print ("Dang dang nhap")
	#check login
	dk = '.: Ðăng ký môn học :.'
	if br.title() == dk:
		print ('Dang nhap thanh cong')
		sys.stdout.flush()
	else:
		print('Dang nhap khong thanh cong, kiem tra lại mat khau va tai khoan')

	
#load trang thư mục điểm	
def tree_group():
	global br
	#load Thu muc diem
	br.open(qldt+'CMCSoft.IU.Web.Info/CourseByFieldTree.aspx') 
	br.select_form(nr = 0)
	#Chọn Kiểm tra tình trạng hoàn thành chương trình học
	br['CTDT'] = ['rdoCheckPassedStageBystu']
	resp = br.submit()
	print "Dang vao bang diem"
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
	data.write(UserFullName.text.encode('utf8')+"\n")
	#StageID
	StageId = resp.find(id ='hidStageId')
	StageId = unicode(StageId['value'])

	#StudentID
	StudentId = resp.find(id ='hidStudentId')
	StudentId = unicode(StudentId['value'])

	#tên nghành 
	lblTitle = resp.find(id ='lblTitle')
	lblTitle = unicode(lblTitle.contents[2].string)
	data.write(lblTitle.encode('utf8')+"\n")
	#tên group
	k = resp.findAll(attrs={"onclick":"return OpenPopupList(this);"})

	GroupSubjectName = []
	for line in k:
		GroupSubjectName.append(unicode(line.string))
	
	#group id
	GroupSubjectId = []
	for i in range(2,30):
		k = 'grdField__ctl'+str(i)+'_hidCreditGroupSubjectId'
		try:
			k = str(resp.findAll(id = k)[0]['value'])
			GroupSubjectId.append(k)
		except:
			break
			
	str1 = u"    --> Kiến thức l"
	str2 = u"KIẾN THỨC GIÁO DỤC "
	str3 = u"KIẾN THỨC LỰA CHỌN "
	k = 0
	for GSI in GroupSubjectId:
		#GroupSubjectName[k] = str(GroupSubjectName[k])

		if (GroupSubjectName[k][0:19] == str1) or (GroupSubjectName[k][0:19] == str2) or (GroupSubjectName[k][0:19] == str3):
			data.write(GroupSubjectName[k].encode('utf8')+"\n")
		else:
			data.write(GroupSubjectName[k].encode('utf8'))
			address = qldt+'CMCSoft.IU.Web.Info/PopupList/GroupCourseMarkDetail.aspx?CreditGroupId='+GSI+'&StudentId='+StudentId+'&StageId='+StageId
			resp = br.open(address).read()
			sub(resp)
		k += 1
		
def sub(resp):
	resp = BeautifulSoup(resp)
	for i in range(2,30):
		k = 'grdField__ctl'+str(i)+'_'
		try:
			CourseCode = str(resp.find(id = k+'lblCourseCode').string)
			CourseName = unicode(resp.find(id = k+'lblCourseName').string)
			CourseCredit = str(resp.find(id = k+'lblCourseCredit').string)
			Theory = str(resp.find(id = k+'txtTheory').string)
			data.write(';'+CourseCode+';'+CourseName.encode('utf8')+';'+CourseCredit+';'+Theory+"\n")
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
