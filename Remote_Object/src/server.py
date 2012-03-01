'''
Created on Jan 20, 2012

@author: mahmudul
'''
import sys
import os
import Pyro4
from remoteobject import Question_bank

DB_NAME = 'mydb.sqlite'
ns=Pyro4.naming.locateNS()
daemon=Pyro4.core.Daemon()
uri=daemon.register(Question_bank(DB_NAME, False))
ns.register("example.Quiz",uri)
daemon.requestLoop()


