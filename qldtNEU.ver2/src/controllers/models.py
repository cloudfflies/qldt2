#!/usr/bin/env python
# -*- coding: utf8 -*-
import logging

from google.appengine.ext import ndb
from xlrd import open_workbook
from datetime import datetime
import csv
import webapp2
class TimeInfo(ndb.Model):
    startdate = ndb.DateProperty()
    expireddate = ndb.DateProperty()
def PutTimeInfo(name,startdate,expireddate):
    newFile = TimeInfo(id = name,
                        startdate = startdate,
                        expireddate = expireddate,
                             )
    newFile.put()
def QryTimeInfo(key):
    Time_key = ndb.Key('TimeInfo',key)
    GetTimeInfo = TimeInfo.query(ancestor=Time_key)
    GetTimeInfo = GetTimeInfo.get()
    return GetTimeInfo
    
class ExamSchedule(ndb.Model):
    Date = ndb.DateProperty()
    Content = ndb.StringProperty()
def QryExamSchedule(key):
    ExamSchedule_key = ndb.Key('ExamSchedule',key)
    GetExamSchedule = ExamSchedule.query(ancestor=ExamSchedule_key)
    GetExamSchedule = GetExamSchedule.get()
    return GetExamSchedule
def PutExamSchedule(file):
    logging.info("update exam schedule")
    file = file.split('\n')
    for x, line in enumerate(file):
        file[x] = line.split(';')

    for row in file:
        if row[0] <> '':
            date = row[1]
            date = datetime.strptime(date,'%d/%m/%Y')
            #Môn trắc nghiệm
            if row[5] <> '0':
                #Class name
                shift = row[0]
                #shift
                if row[2] == '1':
                    shift = shift + "\nCa 1 trắc nghiệm: 7h-8h\n"
                elif row[2] == '2':
                    shift = shift + "\nCa 2 trắc nghiệm: 8h30-9h30\n"
                elif row[2] == '3':
                    shift = shift + "\nCa 3 trắc nghiệm: 10h-11h\n"
                elif row[2] == '4':
                    shift = shift + "\nCa 4 trắc nghiệm: 13h-14h\n"
                elif row[2] == '5':
                    shift = shift + "\nCa 5 trắc nghiệm: 14h30-15h30\n"
                elif row[2] == '6':
                    shift = shift + "\nCa 6 trắc nghiệm: 16h-17h \n"
                else:
                    shift = shift + "\nVui lòng kiểm tra lại trên qldt\n"
                    
                #Location 
                shift = shift + row[3]
                if row[4] == 'x':
                    shift = shift+"\nLàm bài trên máy tính"
            else:
                #môn tự luận
                shift = row[0]
                if row[2] == '1':
                    shift = shift + "\nCa 1 tự luận: 7h-830h\n"
                elif row[2] == '2':
                    shift = shift + "\nCa 2 tự luận: 9h-10h30\n"
                elif row[2] == '3':
                    shift = shift + "\nCa 3 tự luận: 13h-14h30\n"
                elif row[2] == '4':
                    shift = shift + "\nCa 4 tự luận: 15h-16h30\n"
                else:
                    shift = shift + "\nVui lòng kiểm tra lại trên qldt\n"
                #Location 
                shift = shift + row[3]
                if row[4] == 'x':
                    shift = shift+"\nLàm bài trên máy tính"
            newExam = ExamSchedule(id = row[0], #class
                                   Date = date,
                                   Content = shift
                                   );             
            newExam.put();
            
    logging.info("update course success")
class CourseInfo(ndb.Model):
    CourseName = ndb.StringProperty()
    #CourseId = ndb.StringProperty()
    CourseCredit = ndb.IntegerProperty()
    GocHocTap = ndb.StringProperty()
    
class FieldInfo(ndb.Model):
    GroupName = ndb.StringProperty(repeated=True)      
    ListCourseId =  ndb.StringProperty(repeated=True)            
    GroupProperty = ndb.IntegerProperty(repeated=True)          
    NumOfCredits = ndb.IntegerProperty()    
class StuInfo(ndb.Model):
    StuName = ndb.StringProperty()      
    StuField =  ndb.StringProperty() 
    
    StuCourse = ndb.StringProperty(repeated=True)    
    StuAttendance = ndb.FloatProperty(repeated=True)
    StuMidTerm = ndb.FloatProperty(repeated=True)
    StuFinal = ndb.FloatProperty(repeated=True)
    StuCourseMark = ndb.FloatProperty(repeated=True)
    
    BackUpStuCourse = ndb.StringProperty(repeated=True)    
    BackUpStuAttendance = ndb.FloatProperty(repeated=True)
    BackUpStuMidTerm = ndb.FloatProperty(repeated=True)
    BackUpStuFinal = ndb.FloatProperty(repeated=True)
    BackUpStuCourseMark = ndb.FloatProperty(repeated=True)
    
    StuGPA = ndb.FloatProperty()
    StuOveral = ndb.FloatProperty()
    StuCreditCount = ndb.IntegerProperty()
    
    StuLearingCourse = ndb.StringProperty(repeated=True)
    StuLearingCourseId = ndb.StringProperty(repeated=True)
    StuLearingSchedule = ndb.StringProperty(repeated=True)
    StuLearingLocation = ndb.StringProperty(repeated=True)
           
    Feedback = ndb.StringProperty()
#Update date
def UpdateData():
    logging.info("update course")
    wb = open_workbook('course.xls')
    for s in wb.sheets():
        #print 'Sheet:',s.name
        for row in range(s.nrows):
            GocHocTap = s.cell(row,3).value
            if GocHocTap == '':
                GocHocTap = "http://www.dethineu.com/"
            newCourse = CourseInfo(CourseName = s.cell(row,1).value, 
                                   id = s.cell(row,0).value, #courseid
                                   CourseCredit = int(s.cell(row,2).value or 0),
                                   GocHocTap = GocHocTap,
                                   );                     
            newCourse.put();
    logging.info("update course success")
def UpdateField():
    logging.info("update Field")
    wb = open_workbook('majorResult.xls')
    for s in wb.sheets():
        #print 'Sheet:',s.name
        ListCourseId = []
        GroupName = []
        GroupProperty =[]
        majorName = s.cell(0,0).value
        NumOfCredits = int(s.cell(0,1).value)
        for row in range(1,s.nrows):
            GroupName.append(s.cell(row,0).value)
            ListCourseId.append(s.cell(row,1).value)
            GroupProperty.append(int(s.cell(row,2).value or 0))
                
        newField = FieldInfo(id = majorName,
                             GroupName = GroupName,
                             NumOfCredits = NumOfCredits,
                             ListCourseId = ListCourseId,
                             GroupProperty = GroupProperty,
                             )
        newField.put()
    logging.info("update Field success")
        
def PutNewStu(id_key,StuName,StuField,StuCourse,StuAttendance,StuMidTerm,StuFinal,StuCourseMark,BackUpStuCourse,BackUpStuAttendance,BackUpStuMidTerm,BackUpStuFinal,BackUpStuCourseMark,StuLearingCourse,StuLearingCourseId,StuLearingSchedule,StuLearingLocation,Feedback):
    newStu = StuInfo(id = id_key,
                     StuName = StuName,
                     StuField = StuField,  

                     StuCourse = StuCourse,
                     StuAttendance = StuAttendance,
                     StuMidTerm = StuMidTerm,
                     StuFinal = StuFinal,
                     StuCourseMark = StuCourseMark,
                     
                     BackUpStuCourse = BackUpStuCourse,
                     BackUpStuAttendance = BackUpStuAttendance,
                     BackUpStuMidTerm = BackUpStuMidTerm,
                     BackUpStuFinal = BackUpStuFinal,
                     BackUpStuCourseMark = BackUpStuCourseMark,
                     
                     StuLearingCourse = StuLearingCourse,
                     StuLearingCourseId = StuLearingCourseId,
                     StuLearingSchedule = StuLearingSchedule,
                     StuLearingLocation = StuLearingLocation,
                     Feedback = Feedback)

    newStu.put()  
    
def QryStu(key):

    Stu_key = ndb.Key('StuInfo', key)
    GetStuInfo = StuInfo.query(ancestor=Stu_key)
    GetStuInfo = GetStuInfo.get()
    return GetStuInfo

def QryField(key):    
    try:
        Field_key = ndb.Key('FieldInfo', key)
        GetCourseTree = FieldInfo.query(ancestor=Field_key)
        GetCourseTree = GetCourseTree.get()
        return GetCourseTree
    except:
        return "ImpossibleToFind"
def QryCourse(key):
    Course_key = ndb.Key('CourseInfo',key)
    GetCourse = CourseInfo.query(ancestor=Course_key)
    GetCourse = GetCourse.get()
    return GetCourse