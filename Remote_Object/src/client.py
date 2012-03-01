'''
Created on Jan 22, 2012

@author: mahmudulhaque
'''
import Pyro4
import sys
sys.excepthook=Pyro4.util.excepthook

if sys.version_info<(3,0):
    input=raw_input

class Quiz_game:
#getting the remote object
    def __init__(self):
        self.quiz=Pyro4.Proxy("PYRONAME:example.Quiz")
        
    def get_question(self, qid,ques_no):
        row=self.quiz.read_text(qid)
        statement, option_one, option_two, option_three, option_four = row
        print "Question No:%d." %ques_no + " %s" %statement
        print "(a) %s " %option_one
        print "(b) %s" %option_two
        print "(c) %s" %option_three
        print "(d) %s" %option_four
        val=input("Write your option: ").strip()
        return val
# quiz game is initializing with the remote object
quiz_game= Quiz_game()
ques_no=1
#get the "set id" from the remote object
#loop through all of the questions remain in the set
#initially responds with every answer is right or not
#at the end, give the final result 
id=quiz_game.quiz.start()
while True:
    qid=quiz_game.quiz.question(id)
    if qid >0:
        val=quiz_game.get_question(qid, ques_no)
        answer=quiz_game.quiz.answer(id, qid, val)
        if(answer==True):
            print "Great, Your answer is  right!!!"
        else:
            print "Sorry, your answer is wrong."
        ques_no=ques_no+1
    else:
        break
num=quiz_game.quiz.result(id) 
print "You have given %d right answers." %(num) 