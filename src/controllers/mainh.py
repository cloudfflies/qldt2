#!/usr/bin/env python
# -*- coding: utf8 -*-

import os
import logging
from google.appengine.ext.webapp import template
from google.appengine.ext import ndb
import models
from datetime import datetime
import threading

import gaemechanize2
from BeautifulSoup import BeautifulSoup
from BeautifulSoup import BeautifulStoneSoup

#Return time code for schedule
def TimeCode(resp):
    string = BeautifulSoup(str(resp))
    string = unicode(string.find('b'))
    #print string
    Day =''
    for i in range(2,8):
        if u'Thứ '+str(i) in string:
            Day = str(i)
    if u'Chủ nhật' in string:
        Day = str(8)

    string = string.split(u'tiết ')[1]
    string = string.split(' (LT)')[0]
    #string = 1,2 / 1,2,3 / 3,4,5 / 4,5 ...
    NumOfPeriod = str((len(string)+1)/2)
    #NumOfPeriod = 2/3/4
    Period = str(string[0])
    #fist period of class
    return Day+Period+NumOfPeriod
    #ex: 742 Thứ 7 tiết 4,5
    
#Tinh tong tin chi hoan thanh, tong diem co he so
class ClassGPA():
    CountCredit = 0
    TotalOveral = 0
    TotalGPA = 0
    def Main(self,credit,mark10,mark4):
        self.CountCredit += credit
        self.TotalOveral += mark10*credit
        self.TotalGPA += mark4*credit
class ChoseOne():
    def Main(self,items,number):
        #Chose 1 max Mark
        CacheList = []
        for line in items:
            CacheList.append(ConvertToFloat(line['col6']))
        
        self.MaxPosition = max(enumerate(CacheList),key=lambda x: x[1])
        if self.MaxPosition[1] > 4.4:
            self.Credit = ConvertToFloat(items[self.MaxPosition[0]]['col2'])
            self.Max10 = self.MaxPosition[1]
            self.Max4 = ConvertToFloat(items[self.MaxPosition[0]]['col8'])
        else:
            self.Credit = 0
            self.Max10 = 0
            self.Max4 = 0
    
        
class MarkConverter():
    def Main(self,Mark10):
        self.colour = ''
        if Mark10 == ' ':
            self.Mark4 = ' '
            self.MarkW = ' '
        elif Mark10 < 4.5:
            self.Mark4 = 0
            self.MarkW = 'F'
            self.colour = 'background:#6B2B4C'
        elif Mark10 <=4.9:
            self.Mark4 = 1
            self.MarkW = 'D'
            self.colour = 'background:#825934'
        elif Mark10 <=5.4:
            self.Mark4 = 1.5
            self.MarkW = 'D+'
            self.colour= 'background:#825934'
        elif Mark10 <=6.4:
            self.Mark4 = 2
            self.MarkW = 'C'
        elif Mark10 <=6.9:
            self.Mark4 = 2.5
            self.MarkW = 'C+'
        elif Mark10 <=7.9:
            self.Mark4 = 3
            self.MarkW = 'B'
        elif Mark10 <=8.4:
            self.Mark4 = 3.5
            self.MarkW = 'B+'
        elif Mark10 <=8.9:
            self.Mark4 = 4
            self.MarkW = 'A'
        else:
            self.Mark4 = 4
            self.MarkW = 'A+'
            
#Decode String from xmlcharref            
def DecodeString(string=''):
    decodedstring = BeautifulStoneSoup(string, convertEntities=BeautifulStoneSoup.HTML_ENTITIES )
    decodedstring = str(decodedstring)
    decodedstring = decodedstring.decode('utf8')
    return  decodedstring           
#get text from HMTL
def Clear(string=''):
    string = BeautifulSoup(str(string))
    string = string.findAll(text=True)
    return string

def ConvertToFloat(x):
    try:
        return float(x)
    except:
        return 0

def TableProcess(studentTable):
    #conver string to List
    #studentTable = studentTable.split(', ')
    
    #del title-line
    for line in range(8):
        del studentTable[0]
    
    #print studentTable
    CourseCode = []
    Attendance = []
    MidTerm = []
    Final = []
    CourseMark = []
    
    Result = {}
    countLine = 0
    countCol = 0
    
    #loop 8 items > 1 line, next line
    for line in studentTable:
        if countCol == 1:
            CourseCode.append(str(Clear(line)[0]))
            countCol += 1
        elif countCol == 4:
            CacheAttendance = Clear(line)
            countCol += 1
        elif countCol == 5:
            CacheMidTerm = Clear(line)
            countCol += 1
        elif countCol == 6:
            CacheFinal = Clear(line)
            countCol += 1
        elif countCol == 7:
            CacheCourseMark = Clear(line)
            
            #conver to float and reorganize
            #Course learned once
            if len(CacheFinal) == 1:
                Attendance.append(ConvertToFloat(CacheAttendance[0]))
                MidTerm.append(ConvertToFloat(CacheMidTerm[0]))
                Final.append(ConvertToFloat(CacheFinal[0]))
                CourseMark.append(ConvertToFloat(CacheCourseMark[0]))
            else:
                #Course learned more than once
                maxPosition = max(enumerate(CacheCourseMark),key=lambda x: x[1])[0]
                Attendance.append(ConvertToFloat(CacheAttendance[maxPosition]))
                MidTerm.append(ConvertToFloat(CacheMidTerm[maxPosition]))
                Final.append(ConvertToFloat(CacheFinal[maxPosition]))
                CourseMark.append(ConvertToFloat(CacheCourseMark[maxPosition]))
                
            countLine += 1
            countCol = 0
        else:
            countCol += 1
            
        
    Result['CourseCode'] = CourseCode
    Result['Attendance'] = Attendance
    Result['MidTerm'] = MidTerm
    Result['Final'] = Final
    Result['CourseMark'] = CourseMark

    return Result
            

def doRender(handler,tname = 'index.htm', values = { }):
    
    temp = os.path.join(
                        os.path.dirname(os.path.dirname(__file__)),
                        'views/' + tname)

    if not os.path.isfile(temp):
        return False

    """
    # Make a copy of the dictionary and add the path and session
    newval = dict(values)
    newval['path'] = handler.request.path
    handler.session = Session()
    if 'username' in handler.session:
        newval['username'] = handler.session['username']
    """
    logging.info(str(temp))
    handler.response.write(template.render(temp, values))
    return True

class MainGetInfo(ndb.Model):
    def LogIn(self,studentID,studentPass,shortPass):
        br = gaemechanize2.Browser()
        br.open('https://qldt2.neu.edu.vn/cmcsoft.iu.web.info/Login.aspx')
        logging.info("Dang vao qldt2")
        br.select_form(nr = 0)
        br.form['txtUserName'] = studentID
        br.form['txtPassword'] = studentPass

        br.submit()
        logging.info("Da submit form")
        
        if br.title() <> '.: Ðăng ký môn học :.':
            return False
        else:
            
            try:
                dfskj = 1/0
                StuSchedule = GetStudyingCourses(br.response(),studentID)
                #models.PutStuSchedule(StudentID, Classes, ScheduleOfClasses, LocationOfClasses)
                print 'Lich hoc tai trang chu'
            except:
                print 'Lich hoc tai trang chu bi xoa'
                br.open('https://qldt2.neu.edu.vn/CMCSoft.IU.Web.Info/Reports/Form/StudentTimeTable.aspx')
                br.select_form(nr = 0)
                resp = br.response()
                StuSchedule = StuSchedule2(resp)
  
            br.open('https://qldt2.neu.edu.vn/CMCSoft.IU.Web.info/StudentMark.aspx')
            logging.info("Vao Tra cuu diem")
            br.select_form(nr = 0)
            
            resp = BeautifulSoup(br.response())
            #print resp.prettify()
            
            studentName = resp.find(id="PageHeader1_lblUserFullName")
            studentName = str(Clear(studentName)[0])
            studentField = resp.find(id="drpField")
            studentField = str(Clear(studentField)[1])
            studentField = DecodeString(studentField)
            
            #Table of Marks
            studentTable = resp.findAll('td',style="BORDER-RIGHT:RosyBrown 1px solid;")
            
            if studentTable <> []:
                studentTable = TableProcess(studentTable)
            else:
                studentTable = {'CourseCode':[],
                             'Attendance':[],
                             'MidTerm':[],
                             'Final':[],
                             'CourseMark':[],
                             }

            models.PutNewStu(id_key = studentID,
                             StuName = studentName,
                             StuField = studentField,  
        
                             StuCourse = studentTable['CourseCode'],
                             StuAttendance = studentTable['Attendance'],
                             StuMidTerm = studentTable['MidTerm'],
                             StuFinal = studentTable['Final'],
                             StuCourseMark = studentTable['CourseMark'],
                             
                             BackUpStuCourse = studentTable['CourseCode'],
                             BackUpStuAttendance = studentTable['Attendance'],
                             BackUpStuMidTerm = studentTable['MidTerm'],
                             BackUpStuFinal = studentTable['Final'],
                             BackUpStuCourseMark = studentTable['CourseMark'],
                             
                             StuLearingCourse = StuSchedule['Classes'],
                             StuLearingCourseId = StuSchedule['ClassesId'],
                             StuLearingSchedule = StuSchedule['ScheduleOfClasses'],
                             StuLearingLocation =StuSchedule['LocationOfClasses'],
                             Feedback = shortPass,
                                 )
            
            logging.info("Get all Info and put Datastore")
            return True
        
        
class MainProcess():
    def TableShow(self,StuID,StuFieldFromUser=''):
        Result = []
        FinishedCredit = 0
        Overal = 0
        GPA = 0
        Info = {}
        StartDateExam = ''
        HocLai = []
        EnglishLevel = 0
    
        #Get Studen Infomartion
        StuInfo = models.QryStu(str(StuID))
        
        if StuFieldFromUser <> '':
            StuField = StuFieldFromUser
            
        else:
            try:
                StuField = StuInfo.StuField
            except:
                return None
     
        #Get Field Tree of Course

        FieldTree = models.QryField(StuField)
        #If no exist, direct to chose
        
        if FieldTree == None:
            return None
        elif FieldTree == "ImpossibleToFind":
            return "OverQuota"
        else:
            HocLai = []
            #else Process
            Info['Name'] = StuInfo.StuName
            Info['Field'] = StuField
            Info['NumOfCredits'] = FieldTree.NumOfCredits
            Info['Classes'] = StuInfo.StuLearingCourse
            #
            Info['ClassesId'] = StuInfo.StuLearingCourseId
            Info['GocHocTap'] =[]
            for ClassId in Info['ClassesId']:
                ClassLink = models.QryCourse(ClassId)
                Info['GocHocTap'].append(ClassLink.GocHocTap)
            Info['ScheduleOfClasses'] = StuInfo.StuLearingSchedule
            Info['LocationOfClasses'] = StuInfo.StuLearingLocation
            
            #Tinh GPA
            GPA = ClassGPA()
            
            for x, line in enumerate(FieldTree.GroupName):
                CourseCode = FieldTree.ListCourseId[x]
                GroupProperty = FieldTree.GroupProperty[x]
                
                if line == u'//':
                    line = ' '
                #Get Name and Credit
                try:
                    CourseInfo = models.QryCourse(str(CourseCode))
                    CourseName = CourseInfo.CourseName
                    CourseCredit = CourseInfo.CourseCredit
                except:
                    CourseName = ' '
                    CourseCredit = ' '
                    
                #Get Mark
                try:
                    #Find Course Code in list of Course user leanred
                    y = StuInfo.StuCourse.index(CourseCode)
                    StuAttendance = StuInfo.StuAttendance[y]
                    StuMidTerm = StuInfo.StuMidTerm[y]
                    StuFinal = StuInfo.StuFinal[y]
                    StuCourseMark = StuInfo.StuCourseMark[y]
                except:
                    StuAttendance = ' '
                    StuMidTerm = ' '
                    StuFinal = ' '
                    StuCourseMark = ' '
    
                ConvertedMark = MarkConverter()
                ConvertedMark.Main(StuCourseMark)
                Mark4 = ConvertedMark.Mark4
                
                Qua = ConvertToFloat(StuCourseMark) > 4.4
                HLai = ConvertToFloat(StuCourseMark) < 5.5
                MonTinhDiem = CourseCode[:2] <> 'GD'
                MonTinhDiem = MonTinhDiem * (CourseCode[:2] <> 'QP')
                MonTinhDiem = MonTinhDiem * (CourseCode[-2:] <> '.0')
                if Qua and HLai and MonTinhDiem:
                        HocLai.append({'CourseName':CourseName,
                                            'CourseCode':CourseCode,
                                       })
                        
                if CourseCode[-1:] == 'A':
                    EnglishLevel = 2 
                if (GroupProperty == 1 and ConvertToFloat(StuCourseMark) > 4.4):      
                    GPA.Main(CourseCredit,
                             StuCourseMark,
                             Mark4)
                elif GroupProperty > 1 :
                    #Have chose NumberChose in Number Courses
                    if GroupProperty < 100:
                        NumberChose = int(round(GroupProperty/10)) #{1,2)
                        Number = GroupProperty-10*NumberChose #{2,3,4}
                    else:
                        NumberChose = int(round(GroupProperty/100)) #{1,2)
                        Number = GroupProperty-100*NumberChose #{2,3,4}
                    #List of Number-1 items before in Result
                    CacheList = []
                    CacheList = Result[len(Result)-Number+1:]
                    #Add the last (not added to Result)
                    CacheList.append({'col1':CourseName,
                                      'col2':CourseCredit,
                                      'col6':StuCourseMark,
                                      'col8':Mark4})
                    for i in range(NumberChose):
                        Chose = ChoseOne()
                        Chose.Main(CacheList, NumberChose)
                        GPA.Main(Chose.Credit,Chose.Max10,Chose.Max4)
                        del CacheList[Chose.MaxPosition[0]]
                else:
                    pass
                
                #del CacheList[:]    

                Result.append({'col0':line,
                                    'col1':CourseName,
                                    'col2':CourseCredit,
                                    'col3':StuAttendance,
                                    'col4':StuMidTerm,
                                    'col5':StuFinal,
                                    'col6':StuCourseMark,
                                    'col7':ConvertedMark.MarkW,
                                    'col8':Mark4,
                                    'colour':ConvertedMark.colour,
                                                }                               
                                   )
            FinishedCredit = int(round(GPA.CountCredit,0))
            
            try:
                Mark4 = round(ConvertToFloat(GPA.TotalGPA)/ConvertToFloat(GPA.CountCredit),2)
                Overal = round(ConvertToFloat(GPA.TotalOveral)/ConvertToFloat(GPA.CountCredit),2)
            except:
                Mark4 = 0
                Overal = 0    
              
            #def GenerateTableHTML(self): <---------------------->
            if not Info['Classes']:
                HTML = '<p>Các thầy đang chuẩn bị cho kỳ mới đó :D</p>'
            else:
                Table = {'Period1':{'D2':[0,0],'D3':[0,0],'D4':[0,0],'D5':[0,0],'D6':[0,0],'D7':[0,0]},
                    'Period2':{'D2':[0,0],'D3':[0,0],'D4':[0,0],'D5':[0,0],'D6':[0,0],'D7':[0,0]},
                    'Period3':{'D2':[0,0],'D3':[0,0],'D4':[0,0],'D5':[0,0],'D6':[0,0],'D7':[0,0]},
                    'Period4':{'D2':[0,0],'D3':[0,0],'D4':[0,0],'D5':[0,0],'D6':[0,0],'D7':[0,0]},
                    'Period5':{'D2':[0,0],'D3':[0,0],'D4':[0,0],'D5':[0,0],'D6':[0,0],'D7':[0,0]},
                    'Period6':{'D2':[0,0],'D3':[0,0],'D4':[0,0],'D5':[0,0],'D6':[0,0],'D7':[0,0]},
                    'Period7':{'D2':[0,0],'D3':[0,0],'D4':[0,0],'D5':[0,0],'D6':[0,0],'D7':[0,0]},
                    'Period8':{'D2':[0,0],'D3':[0,0],'D4':[0,0],'D5':[0,0],'D6':[0,0],'D7':[0,0]},
                    'Period9':{'D2':[0,0],'D3':[0,0],'D4':[0,0],'D5':[0,0],'D6':[0,0],'D7':[0,0]},
                    'Period10':{'D2':[0,0],'D3':[0,0],'D4':[0,0],'D5':[0,0],'D6':[0,0],'D7':[0,0]},
                    }
                for x, ClassInfo in enumerate(Info['ScheduleOfClasses']):
                    numofperiods =  ClassInfo[2]
                    firstperiod =  ClassInfo[1]
                    day =  ClassInfo[0]
                    if day <> 8:
                        period = 'Period' + firstperiod
                        day = 'D'+ day
                        numofperiods = int(numofperiods)
                        content = '<a target="_blank" href="'+Info['GocHocTap'][x]+'"><b>'+Info['Classes'][x]+'</b><br><span style="color:#885F69;font-weight:bold;">'+Info['LocationOfClasses'][x]+'</span></br></a>'
                        Table[period][day] = [numofperiods,content]
                        for y in range(1,numofperiods):
                            period = 'Period' + str(y+int(firstperiod))
                            Table[period][day] = [-1,0]
                    else:
                        pass
                HTML = u"""<table class="table table-bordered" id="scheduleTable">
                <thead class="header">
                    <tr>
                        <th width="7%"></th>
    
                        <th width="15.5%">Thứ 2</th>
    
                        <th width="15.5%">Thứ 3</th>
    
                        <th width="15.5%">Thứ 4</th>
    
                        <th width="15.5%">Thứ 5</th>
    
                        <th width="15.5%">Thứ 6</th>
    
                        <th width="15.5%">Thứ 7</th>
                    </tr>
                </thead>
                <tbody>"""
                for x in range(1,11):
                    period = 'Period' + str(x)
                    if x == 6:
                        HTML = HTML + u'<tr style="border-top: solid #CBEBF7;"><td>Tiết '+str(x)+u'</td>'
                    else:
                        HTML = HTML + u'<tr><td>Tiết '+str(x)+u'</td>'
                    for y in range(2,8):
                        day = 'D'+str(y)
                        if Table[period][day][0] == 0:
                            HTML = HTML + u'<td></td>'
                        elif Table[period][day][0] <> -1:
                            HTML = HTML + u'<td class="tdhover" rowspan="' + str(Table[period][day][0]) + '">' + unicode(Table[period][day][1]) + '</td>'
                    HTML = HTML + u'</tr>'
                HTML = HTML + u'</tbody></table>'
           
        # def ScheduleExam(self): <---------------------->
            TimeInfo = models.QryTimeInfo('LichThi')
            if datetime.date(datetime.now()) > TimeInfo.expireddate:
                Exam = []
            else:
                StartDateExam = TimeInfo.startdate.strftime('%Y-%m-%d')
                Exam = []
                for Class in Info['Classes']:
                    ExamInfo = models.QryExamSchedule(Class)
                    if ExamInfo <> None:
                        Exam.append({'date':ExamInfo.Date.strftime('%Y-%m-%d'),
                                     'content':ExamInfo.Content
                                     })
            
            AllData = {'Result' : Result,
                       'FinishedCredit' : FinishedCredit,
                       'Overal' : Overal,
                       'GPA' : Mark4,
                       'Info' : Info,
                       'StartDateExam' : StartDateExam,
                       'HocLai' : HocLai,
                       'EnglishLevel' : EnglishLevel,
                       'Exam' : Exam,
                       'HTML' : HTML,
                       }
            return AllData


def GetStudyingCourses(resp,StudentID):
    resp = BeautifulSoup(resp)
    #print resp.prettify()
    Classes = []
    ScheduleOfClasses = []
    LocationOfClasses = []
    CoursesId=[]
    i = 2 
     
    for i in range (2,20):
        #Classes of Courses
        Class = 'gridRegistered__ctl'+str(i)+'_lblCourseClass'
        Class = resp.find(id=Class)
        #Check if end of table
        if (Class == None) and (i==2):
            #return None
            htmle = 1/0
        if  (Class == None) and (i>2):
            break
        
        Class = str(Clear(Class)[0])
        #gridRegistered__ctl4_lblCourseCode
        CourseId = 'gridRegistered__ctl'+str(i)+'_lblCourseCode'
        CourseId = resp.find(id=CourseId)
        CourseId = str(Clear(CourseId)[0])
        #Time of class
        Schedule = 'gridRegistered__ctl'+str(i)+'_lblLongTime'
        Schedule = resp.find(id=Schedule)
        Schedule = TimeCode(Schedule)
        #Time of class
        Schedule = 'gridRegistered__ctl'+str(i)+'_lblLongTime'
        Schedule = resp.find(id=Schedule)
        Schedule = TimeCode(Schedule)
        
        #Location of class
        Location = 'gridRegistered__ctl'+str(i)+'_lblLocation'
        Location = resp.find(id=Location)
        Location = str(Clear(Location)[0])
        
        Classes.append(Class)
        ScheduleOfClasses.append(Schedule)
        LocationOfClasses.append(Location)
        CoursesId.append(CourseId)
    
    Result = {'Classes':Classes, 
              'ClassesId':CoursesId,
              'ScheduleOfClasses':ScheduleOfClasses, 
              'LocationOfClasses':LocationOfClasses}
     
    return Result 
    
def PutChangedMark(StuID, CoursesID, CoursesMark, EnglishLevel, CerKind, EnglishScore):
    #read database
    StuInfo = models.QryStu(StuID)
    
    StuName = StuInfo.StuName
    StuField =  StuInfo.StuField
    
    StuCourse = StuInfo.StuCourse
    StuAttendance = StuInfo.StuAttendance
    StuMidTerm = StuInfo.StuMidTerm
    StuFinal = StuInfo.StuFinal
    StuCourseMark = StuInfo.StuCourseMark
    
    BackUpStuCourse = StuInfo.BackUpStuCourse
    BackUpStuAttendance = StuInfo.BackUpStuAttendance
    BackUpStuMidTerm = StuInfo.BackUpStuMidTerm
    BackUpStuFinal = StuInfo.BackUpStuFinal
    BackUpStuCourseMark = StuInfo.BackUpStuCourseMark
    StuGPA = StuInfo.StuGPA 
    StuOveral = StuInfo.StuOveral
    StuCreditCount = StuInfo.StuCreditCount
    StuLearingCourse = StuInfo.StuLearingCourse
    StuLearingCourseId = StuInfo.StuLearingCourseId
    StuLearingSchedule = StuInfo.StuLearingSchedule
    StuLearingLocation = StuInfo.StuLearingLocation
    
    Feedback = StuInfo.Feedback
    
    #add changed mark
    for x, Course in enumerate(CoursesMark):
        if Course == '' or ConvertToFloat(Course) < 5.5:
            pass
        else:
            StuCourse = [CoursesID[x]] + StuCourse
            StuCourseMark = [ConvertToFloat(Course)] + StuCourseMark
            
            StuAttendance = [0] + StuAttendance
            StuMidTerm = [0] + StuMidTerm
            StuFinal = [0] + StuFinal

    EnglishScore = ConvertToFloat(EnglishScore[0])
   
    if EnglishScore == 0:
        pass
    else:
        if EnglishLevel[0] == '1':
            CoursesID = ['NNKC1101A','NNKC1102A','NNKC1103A']
        elif EnglishLevel[0] == '2':
            CoursesID = ['NNKC1101B','NNKC1102B','NNKC1103B']
            
        EnglishMark1 = [8, 7]
        EnglishMark2 = [9,9,8]
        EnglishMark3 = [10,10,9]
        EnglishMark4 = [10,10,10]
        if CerKind[0] == 'ielts':
            if EnglishScore >= 6.5:
                CoursesMark = EnglishMark4
            elif EnglishScore >= 6.0:
                CoursesMark = EnglishMark3
            elif EnglishScore >= 5.0:
                CoursesMark = EnglishMark2
            elif EnglishScore >= 4.5:
                CoursesMark = EnglishMark1
                CoursesID.pop(2)
            else:
                CoursesID = []
                CoursesMark = []
        elif CerKind[0] == u'toeic':
            if EnglishScore >= 591:
                CoursesMark = EnglishMark4
            elif EnglishScore >= 541:
                CoursesMark = EnglishMark3
            elif EnglishScore >= 490:
                CoursesMark = EnglishMark2
            elif EnglishScore >= 450:
                CoursesMark = EnglishMark1
                CoursesID.pop(2)
            else:
                CoursesID = []
                CoursesMark = []
        elif CerKind[0] == 'toeflibt':
            if EnglishScore >= 71:
                CoursesMark = EnglishMark4
            elif EnglishScore >= 61:
                CoursesMark = EnglishMark3
            elif EnglishScore >= 55:
                CoursesMark = EnglishMark2
            elif EnglishScore >= 45:
                CoursesMark = EnglishMark1
                CoursesID.pop(2)
            else:
                CoursesID = []
                CoursesMark = []
        elif CerKind[0] == 'toeflpbt':
            if EnglishScore >= 530:
                CoursesMark = EnglishMark4
            elif EnglishScore >= 500:
                CoursesMark = EnglishMark3
            elif EnglishScore >= 480:
                CoursesMark = EnglishMark2
            elif EnglishScore >= 450:
                CoursesMark = EnglishMark1
                CoursesID.pop(2)
            else:
                CoursesID = []
                CoursesMark = []
        elif CerKind[0] == 'toeflcbt':
            if EnglishScore >= 195:
                CoursesMark = EnglishMark4
            elif EnglishScore >= 173:
                CoursesMark = EnglishMark3
            elif EnglishScore >= 155:
                CoursesMark = EnglishMark2
            elif EnglishScore >= 133:
                CoursesMark = EnglishMark1
                CoursesID.pop(2)
            else:
                CoursesID = []
                CoursesMark = []
    
        StuCourse = CoursesID + StuCourse
        StuCourseMark = CoursesMark + StuCourseMark
        if len(CoursesID) == 3:
            StuAttendance = [0,0,0] + StuAttendance
            StuMidTerm = [0,0,0] + StuMidTerm
            StuFinal = [0,0,0] + StuFinal
        elif len(CoursesID) == 2:
            StuAttendance = [0,0] + StuAttendance
            StuMidTerm = [0,0] + StuMidTerm
            StuFinal = [0,0] + StuFinal
    #update changed mark 
    models.PutNewStu(StuID,
                     StuName,
                     StuField,
                     
                     StuCourse,
                     StuAttendance,
                     StuMidTerm,
                     StuFinal,
                     StuCourseMark,
                     
                     BackUpStuCourse,
                     BackUpStuAttendance,
                     BackUpStuMidTerm,
                     BackUpStuFinal,
                     BackUpStuCourseMark,
                     
                     StuLearingCourse,
                     StuLearingCourseId,
                     StuLearingSchedule,
                     StuLearingLocation,
                     Feedback)
def RestoreStu(StuID):
    StuInfo = models.QryStu(StuID)
    models.PutNewStu(id_key = StuID, 
                     StuName = StuInfo.StuName, 
                     StuField = StuInfo.StuField, 
                     StuCourse = StuInfo.BackUpStuCourse, 
                     StuAttendance = StuInfo.BackUpStuAttendance,
                     StuMidTerm = StuInfo.BackUpStuMidTerm,
                     StuFinal = StuInfo.BackUpStuFinal,
                     StuCourseMark = StuInfo.BackUpStuCourseMark,
                     BackUpStuCourse = StuInfo.BackUpStuCourse,
                     BackUpStuAttendance = StuInfo.BackUpStuAttendance,
                     BackUpStuMidTerm = StuInfo.BackUpStuMidTerm,
                     BackUpStuFinal = StuInfo.BackUpStuFinal,
                     BackUpStuCourseMark = StuInfo.BackUpStuCourseMark,
                     StuLearingCourse = StuInfo.StuLearingCourse,
                     StuLearingCourseId = StuInfo.StuLearingCourseId,
                     StuLearingSchedule = StuInfo.StuLearingSchedule,
                     StuLearingLocation = StuInfo.StuLearingLocation,
                     Feedback = StuInfo.Feedback)
def UpdateStuField(StuID,field):    
    StuInfo = models.QryStu(StuID)
    
    models.PutNewStu(id_key = StuID, 
                     StuName = StuInfo.StuName, 
                     StuField = field, 
                     
                     StuCourse = StuInfo.BackUpStuCourse, 
                     StuAttendance = StuInfo.BackUpStuAttendance,
                     StuMidTerm = StuInfo.BackUpStuMidTerm,
                     StuFinal = StuInfo.BackUpStuFinal,
                     StuCourseMark = StuInfo.BackUpStuCourseMark,
                     
                     BackUpStuCourse = StuInfo.BackUpStuCourse,
                     BackUpStuAttendance = StuInfo.BackUpStuAttendance,
                     BackUpStuMidTerm = StuInfo.BackUpStuMidTerm,
                     BackUpStuFinal = StuInfo.BackUpStuFinal,
                     BackUpStuCourseMark = StuInfo.BackUpStuCourseMark,
                     
                     StuLearingCourse = StuInfo.StuLearingCourse,
                     StuLearingCourseId = StuInfo.StuLearingCourseId,
                     StuLearingSchedule = StuInfo.StuLearingSchedule,
                     StuLearingLocation = StuInfo.StuLearingLocation,
                     Feedback = StuInfo.Feedback)   
def DelRNT(string):
    string = string.replace('\r','')
    string = string.replace('\t','')
    string = string.replace('\n','') 
    return string          
def StuSchedule2(response):
    resp = BeautifulSoup(response)
    Schedule = resp.findAll('tr',{'class':"cssListItem"})
    Schedule = Schedule + resp.findAll('tr',{'class':"cssListAlternativeItem"})
    #models.PutStuSchedule(StudentID, Classes, ScheduleOfClasses, LocationOfClasses)
    
    Result = {}
    Classes = []
    ClassesId =[]
    ScheduleOfClasses = [] 
    LocationOfClasses = []
    for Class in Schedule:
        Class = str(Class)
        ClassInfo = BeautifulSoup(Class)
        ClassInfo = ClassInfo.findAll('td')
        
        ClassName = Clear(ClassInfo[1])
        ClassName = str(ClassName[0])
        ClassName = DelRNT(ClassName)
        Classes.append(ClassName)
        
        ClassId = Clear(ClassInfo[2])
        ClassId = str(ClassId[1])
        ClassId = DelRNT(ClassId)
        ClassesId.append(ClassId)
    
        ScheduleOfClass = ClassInfo[3]
        ScheduleOfClass = str(ScheduleOfClass)
        ScheduleOfClass = TimeCode(ScheduleOfClass)
        ScheduleOfClasses.append(ScheduleOfClass)
        
        LocationOfClass = Clear(ClassInfo[4])[0]
        LocationOfClass = str(LocationOfClass)
        LocationOfClass = DelRNT(LocationOfClass)
        LocationOfClasses.append(LocationOfClass)
        
    Result = {'Classes':Classes, 
              'ClassesId':ClassesId ,
              'ScheduleOfClasses':ScheduleOfClasses,
              'LocationOfClasses':LocationOfClasses}
    return Result
