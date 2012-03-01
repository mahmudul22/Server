#!/usr/bin/env python

'''
Created on Jan 19, 2012

@author: mahmudul
'''
import logging
import string 
import os
import sqlite3
import sys
import random
import Pyro4
import web, json
from web import form

question_set = {"set 1": [1,2,3], "set 2": [2,3,4], "set 3": [1,3,4]}
table=string.maketrans('', '',)
logging.basicConfig(level=logging.INFO)
log = logging.getLogger('Quiz')
hdlr = logging.FileHandler('quiz.log','a')
log.addHandler(hdlr)
render = web.template.render('../templates/')
DB_NAME = 'mydb1.sqlite'

class Question_bank:
    def __init__(self,DB_NAME, already_started):
        self.qid=0
        self.id=""
        self.already_started=already_started
        self.total_answer=[]
        self.initial=0
        self.question_list=[]
        self.DB_NAME = DB_NAME
        self.db_is_new =  not os.path.exists(DB_NAME)
        self.do_database_work()
    

        
    def create_tables(self,cursor):
        log.info('Creating tables')
        cursor.execute("create table qbank (ques_no integer primary key autoincrement not null,statement text, option_one text, option_two text,option_three text, option_four text, right_answer text )")

    def insert_data(self,cursor):
        for statement, option_one, option_two, option_three, option_four, right_answer in [('What is the colour of the cross on the flag of Switzerland?', 'Black', 'Red', 'White', 'Blue', 'White'),
                                ("Where did the car manufacturer Audi originate?", "France", "Italy", "sweden", "Germany", "Germany"),
                                ("What is the capital of Norway?", "London", "Oslo", "Stockholm", "Dhaka", "Oslo"),
                                ("Who is the first President of USA in 21st century?", "George Washington", "George W. Bush", "Barack Obama", "William J. Clinton", "George W. Bush"),
                                ]:
            log.info('Inserting %s %s %s %s %s (%s)', statement, option_one, option_two, option_three, option_four, right_answer)
            cursor.execute("insert into qbank (statement, option_one, option_two, option_three, option_four, right_answer) values (?, ?, ?, ?, ?, ?)", (statement, option_one, option_two, option_three, option_four, right_answer))
        return
    
    def started_exam(self):
        count=0
        with open('quiz.log') as myfile:
            row= list(myfile)[-1].strip()
            row_list= row.split(', ')
            stripped_lines=[line.translate(table,"[]''") for line in row_list]
            for line in stripped_lines:
                if(line=="T" or line=="F"):
                    count=count+1
            if question_set.has_key(stripped_lines[0]):
                if(len(question_set[stripped_lines[0]])==count):
                    return self.already_started
                else:
                    self.already_started=True
        return self.already_started
            
    def get_old_examset(self):
        with open('quiz.log') as myfile:
            row= list(myfile)[-1].strip()
            row_list= row.split(', ')
            stripped_lines=[line.translate(table,"[]''") for line in row_list]
            question_set=stripped_lines[0]
        return question_set    
    
    def start(self):
        if(os.path.exists('quiz.log')==True and self.started_exam()==True):
            id=self.get_old_examset()
            self.total_answer.append(id)
        else:
            question_set = "set " + str(random.randint(1,3))
            self.total_answer.append(question_set)
            id = question_set 
        return id
    
    def remaining_questions(self):
        count=0
        with open('quiz.log') as myfile:
            row= list(myfile)[-1].strip()
            row_list= row.split(', ')
            stripped_lines=[line.translate(table,"[]''") for line in row_list]
            for line in stripped_lines:
                if(line=="T" or line=="F"):
                    count=count+1
            if question_set.has_key(stripped_lines[0]):
                self.question_list=question_set[stripped_lines[0]][count:len(question_set[stripped_lines[0]])]
                self.total_answer=list(stripped_lines)
        return 
    
    def question(self, id):
        if (self.already_started==True):
            self.remaining_questions()
            print "if fails: %s" %(self.question_list)
        else:
            print self.question_list
            if question_set.has_key(id):
                if self.initial==0:
                    self.question_list = list(question_set[id])
                    self.initial = 1
                else:
                        pass
        if len(self.question_list)>0:
            qid=self.question_list.pop(-len(self.question_list))
            return qid
        else:
            self.initial = 0
            return 0
        
    def answer(self, id, qid, val):
        correct=False
        db = sqlite3.connect(self.DB_NAME)
        try:
            cursor = db.cursor()
            cmd ='select right_answer from qbank where ques_no = ' + str(qid)
            cursor.execute(cmd)
            row = cursor.fetchone()
            right_answer=row
            print "val %s and answer is: %s" %(val.upper(), "".join(row))
            if (val.upper()=="".join(row)):
                correct=True
                self.total_answer.append('T')
                log.info(self.total_answer)
            else:
                self.total_answer.append('F')
                log.info(self.total_answer)
            cursor.close()
        except:
            log.error('Data read failure')
        print self.total_answer
        return correct
    
    def result(self):
        num=0
        for result in self.total_answer:
            if (result.strip()=="T"):
                num=num +1
        self.total_answer=[]
        self.already_started=False
        print num
        return num
    
    def do_database_work(self):
            db = sqlite3.connect(self.DB_NAME)        
            try:
                cursor = db.cursor()
                if self.db_is_new:   
                    self.create_tables(cursor)
                    self.insert_data(cursor)
            except:
                db.rollback()
                log.error('Rolling back transaction')
                raise
            else:
                db.commit()
            return

    def read_text(self,qid):
        db = sqlite3.connect(self.DB_NAME)
        try:
            cursor = db.cursor()
            cmd ='select statement, option_one, option_two, option_three, option_four from qbank where ques_no = ' + str(qid)
            cursor.execute(cmd)
            row = cursor.fetchone()
            return row
            cursor.close()

        except:
            log.error('Data read failure')
        

qbank=Question_bank(DB_NAME, False)
urls = ('/quiz', 'quiz',
        '/quiz/(.*)', 'question',
        '/question', 'question', 
        '/answer', 'answer', 
        '/final_result', 'final_result',
        '/lastquiz', 'lastquiz', 
        )


app = web.application(urls, globals())

class lastquiz:
    
    def GET(self):
        id=qbank.start()
        qbank.id=id
        if (qbank.already_started==True):
            raise web.seeother('/quiz')
        else:
            return render.lastquiz()

class final_result:
    def GET(self):  
        score = qbank.result()
        print "final score %d" %(score) 
        return render.final_result(score)



class quiz:
    def GET(self):
        qbank.total_answer=[]
        id=qbank.start()
        qbank.id=id
        return render.quiz(qbank.already_started)

class answer:
    def GET(self):
        return json.dumps("First get the question")
    def POST(self):
        db = sqlite3.connect(DB_NAME)
        cursor = db.cursor()
        cmd ='select right_answer from qbank where ques_no = ' + str(qbank.qid)
        cursor.execute(cmd)
        row = cursor.fetchone()
        print "answer is: %s" %("".join(row))
        i=web.input()
        print "given:%s & ans is: %s" %(i.keys()[0], "".join(row))
        if (i.keys()[0]=="".join(row)):
            qbank.total_answer.append('T')
            log.info(qbank.total_answer)
            print "logging: %s" %qbank.total_answer
            return render.answer("Great your answer is right, please continue?")
        else:
            qbank.total_answer.append('F')
            log.info(qbank.total_answer)
            return render.answer("Sorry your answer is Wrong, please continue?")  


class question:

    def GET(self, name=None):
        id=web.websafe(name)
        question_form = []
        if(id==None):
            qbank.qid=qbank.question(qbank.id)
        elif(question_set.has_key(id)):
            qbank.total_answer=[]
            qbank.id=id
            qbank.total_answer.append(str(qbank.id))
            qbank.qid=qbank.question(id)
            print "qbank id is:" 
            print id
            print qbank.total_answer
        else:
            return json.dumps("Not a valid exam set") 
        row=qbank.read_text(qbank.qid)
        print "qid %s row: %s" %(qbank.qid,row)
        if (qbank.qid>0):
            for thing in row[1:]:
                question_form.insert(0, form.Checkbox(thing, value="on")) 
            qform = form.Form(*question_form)
            return render.question(qform, row[0] )
        else:
            raise web.seeother('/final_result')

    
    def POST(self, name=None): 
        question_form = []
        qbank.qid=qbank.question(qbank.id)
        row=qbank.read_text(qbank.qid)
        print "qid %s row: %s" %(qbank.qid,row)
        if (qbank.qid>0):
            for thing in row[1:]:
                question_form.insert(0, form.Checkbox(thing, value="on")) 
            qform = form.Form(*question_form)
            return render.question(qform, row[0])
        else:
            raise web.seeother('/final_result')


def main():
    try:
		app.run()
    except:
        log.exception('Error while doing database work')
        return 1
    else:
        return 0

if __name__ == "__main__":
	main()
	
