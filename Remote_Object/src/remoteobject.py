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
import web

#set of questions and additional global variables are initialized
question_set = {"set 1": [1,2,3], "set 2": [2,3,4], "set 3": [1,3,4]}
table=string.maketrans('', '',)
logging.basicConfig(level=logging.INFO)
log = logging.getLogger('Quiz')
hdlr = logging.FileHandler('quiz.log','a')
log.addHandler(hdlr)


class Question_bank:
    def __init__(self,DB_NAME, already_started):
        self.already_started=already_started
        self.total_answer=[]
        self.initial=0
        self.question_list=[]
        self.DB_NAME = DB_NAME
        self.db_is_new =  not os.path.exists(DB_NAME)
        self.do_database_work()
    

# sql commands for creating the question database
    def create_tables(self,cursor):
        log.info('Creating tables')
        cursor.execute("create table qbank (ques_no integer primary key autoincrement not null,statement text, option_one text, option_two text,option_three text, option_four text, right_answer text )")

    def insert_data(self,cursor):
        for statement, option_one, option_two, option_three, option_four, right_answer in [('What is the colour of the cross on the flag of Switzerland?', 'Black', 'Red', 'White', 'Blue', 'C'),
                                ("Where did the car manufacturer Audi originate?", "France", "Italy", "sweden", "Germany", "D"),
                                ("What is the capital of Norway?", "London", "Oslo", "Stockholm", "Dhaka", "B"),
                                ("Who is the first President of USA in 21st century?", "George Washington", "George W. Bush", "Barack Obama", "William J. Clinton", "B"),
                                ]:
            log.info('Inserting %s %s %s %s %s (%s)', statement, option_one, option_two, option_three, option_four, right_answer)
            cursor.execute("insert into qbank (statement, option_one, option_two, option_three, option_four, right_answer) values (?, ?, ?, ?, ?, ?)", (statement, option_one, option_two, option_three, option_four, right_answer))
        return
    
#checks whether a quiz has already started and incomplete or not
#if the log files last line contains all the answers for that set 
#then it is completed otherwise not

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
    
#return the last exam set that has not been completed

    def get_old_examset(self):
        with open('quiz.log') as myfile:
            row= list(myfile)[-1].strip()
            row_list= row.split(', ')
            stripped_lines=[line.translate(table,"[]''") for line in row_list]
            question_set=stripped_lines[0]
        return question_set   
     
#starts the quiz session 

    def start(self):
        if(os.path.exists('quiz.log')==True and self.started_exam()==True):
            id=self.get_old_examset()
            self.total_answer.append(id)
        else:
            question_set = "set " + str(random.randint(1,3))
            self.total_answer.append(question_set)
            id = question_set 
        return id
    
#get the remaining set of questions from the last set and put then into the list

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
# return the appropriate question_id from the database
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
        
#checks the given answer with the actual answer 
#append the answer with the list of the total answer    
     
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

# return the final right answers

    def result(self,id):
        num=0
        for result in self.total_answer:
            if (result.strip()=="T"):
                num=num +1
        self.total_answer=[]
        self.already_started=False
        return num

# creating the database for the first time
   
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

# return the question from the database

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
        

def main():
    DB_NAME = 'mydb1.sqlite'
    qbank=Question_bank(DB_NAME)
    try:
        qbank.do_database_work()
        qbank.read_data()
    except:
        log.exception('Error while doing database work')
        return 1
    else:
        return 0

if __name__ == '__main__':
    main()
