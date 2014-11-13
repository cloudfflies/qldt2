#!/usr/bin/env python
# -*- coding: utf8 -*-


import logging
import webapp2
from webapp2_extras import sessions
import json

from controllers import models
from controllers import mainh
from datetime import datetime

#This is needed to configure the session secret key
#Runs first in the whole application
myconfig_dict = {}
myconfig_dict['webapp2_extras.sessions'] = {
    'secret_key': 'my-super-secret-key-somemorearbitarythingstosay',
}

#Session Handling class, gets the store, dispatches the request
class BaseHandler(webapp2.RequestHandler):
    def dispatch(self):
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)
 
        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)
 
    @webapp2.cached_property
    def session(self):
        # Returns a session using the default cookie key.
        return self.session_store.get_session()
#End of BaseSessionHandler Class

class LoginHandler(BaseHandler,mainh.MainGetInfo):
    def get(self):        
        """
        self.redirect('http://www.qldt2neu-backup2.appspot.com',True)
        """
        #If a session sent then delete
        if self.session.get('user'):
            del self.session['user']
               
        mainh.doRender(self,'login.html')

    def post(self):
        shortPass = self.request.get('shortPass')
        studentID = self.request.get('studentID')
        studentPass = self.request.get('studentPass')       
        logging.info("%s logging in" % studentID)
        self.session['user'] = studentID
        
        try:
            PassQLDT = self.LogIn(studentID, studentPass, shortPass)
        except:
            PassQLDT = True
        #Check login from qldt2
        if (PassQLDT) :
            logging.info("%s just logged in" % studentID)
            #direct to /
            self.redirect('/',permanent=True)
        else:
            mainh.doRender(self,'loginfail.html')
            
          
            
class LogoutHandler(BaseHandler):
    def get(self):
        #back to login site
        self.redirect('/login',permanent=True)
        
class UpdateData(BaseHandler):
    def get(self):
        models.UpdateData()
        models.UpdateField()
        self.response.write('Update thành công')
class FieldHandler(BaseHandler,mainh.MainProcess):
    def get(self):
        mainh.doRender(self,
                        'field.html')
    def post(self):
        if self.session.get('user'):
            StuID = self.session.get('user')
            field = self.request.get('chosenfield')
            
            try:
                mainh.UpdateStuField(StuID,field)
                
                AllData = self.TableShow(StuID,field)
                mainh.doRender(self,
                               'index.html',
                               {'Name' : AllData['Info']['Name'],
                                'Field' : AllData['Info']['Field'],
                                'NumOfCredits' : AllData['Info']['NumOfCredits'],
                                'Result' : AllData['Result'],
                                'FinishedCredit' : AllData['FinishedCredit'],
                                'Overal' : AllData['Overal'],
                                'GPA' : AllData['GPA'],
                                'HTMLTableSchedule':AllData['HTML'].encode('utf8'),
                                'ScheduleExam':AllData['Exam'],
                                'startdate':AllData['StartDateExam'],
                                'HocLai':AllData['HocLai'],
                                'EnglishLevel':AllData['EnglishLevel'],
                                                                }
                               )
                
            except:
                #if self.session.get('user'):
                #    del self.session['user']
                mainh.doRender(self,'overquota.html')
        
class updateExam(BaseHandler):
    def get(self):
        mainh.doRender(self,
                        'updateExam.html')
    def post(self):
        expireddate = self.request.get('expireddate')
        expireddate = datetime.strptime(expireddate,'%d/%m/%Y')
        expireddate = datetime.date(expireddate)
        startdate = self.request.get('startdate')
        startdate = datetime.strptime(startdate,'%d/%m/%Y')
        startdate = datetime.date(startdate)
        models.PutTimeInfo('LichThi', startdate, expireddate)
        file = self.request.get('ExamSchedule')
        models.PutExamSchedule(file)
        self.response.write('Update thành công')
class ChangeMarkHandler(BaseHandler,mainh.MainProcess):
    def post(self):
        if self.session.get('user'):
            StuID = self.session.get('user')

        #get Mark changed
        CoursesID = self.request.get_all('CourseID')
        CoursesMark = self.request.get_all('inputCourse',default_value="")
        
        #get English Score
        EnglishLevel = self.request.get_all('EnglishLevel')
        CerKind = self.request.get_all('CerKind')
        EnglishScore = self.request.get_all('EnglishScore')
        mainh.PutChangedMark(StuID, 
                            CoursesID, 
                            CoursesMark, 
                            EnglishLevel, 
                            CerKind, 
                            EnglishScore)
        #self.redirect('/changeMark')

        AllData = self.TableShow(StuID)
        output ={'GPA':AllData['GPA'],
                 'Overal':AllData['Overal'],
                 'FinishedCredit':AllData['FinishedCredit']}
        output = json.dumps(output)
        self.response.headers = {'Content-Type': 'application/json; charset=utf-8'}
        self.response.write(output)
        mainh.RestoreStu(StuID)
        
class SuaBanWordHandler(BaseHandler):
    def get(self):
        mainh.doRender(self, 'SuaBanWord.html')
        
        
#MainHandler class where we write code for ourselves
class MainHandler(BaseHandler,mainh.MainProcess):
    def get(self):
        """
        self.redirect('http://www.qldt2neu-backup2.appspot.com',True)
        """
        if self.session.get('user'):
            StuID = self.session.get('user')
            AllData = self.TableShow(StuID)
            
            if AllData =="ImpossibleToFind":
                self.redirect('/field',True)
            elif not AllData:
                self.redirect('/field',True)
            else:
                mainh.doRender(self,
                               'index.html',
                               {'Name' : AllData['Info']['Name'],
                                'Field' : AllData['Info']['Field'],
                                'NumOfCredits' : AllData['Info']['NumOfCredits'],
                                'Result' : AllData['Result'],
                                'FinishedCredit' : AllData['FinishedCredit'],
                                'Overal' : AllData['Overal'],
                                'GPA' : AllData['GPA'],
                                'HTMLTableSchedule':AllData['HTML'].encode('utf8'),
                                'ScheduleExam':AllData['Exam'],
                                'startdate':AllData['StartDateExam'],
                                'HocLai':AllData['HocLai'],
                                'EnglishLevel':AllData['EnglishLevel'],
                                                                }
                               )
        else:
            self.redirect('/login',True)




#End of MainHandler Class


application = webapp2.WSGIApplication([
                                            ('/login', LoginHandler),
                                            ('/logout', LogoutHandler),
                                            ('/field',FieldHandler),
                                            ('/update', UpdateData),
                                            ('/updateExam', updateExam),
                                            ('/changeMark', ChangeMarkHandler),
                                            ('/SuaBanWord', SuaBanWordHandler),
                                            ('/.*', MainHandler),
                                            
                                            #('/test', TestHandler)
                                          ],
                                             debug=True,
                                             config = myconfig_dict)




