#!/bin/python2.7
import random,time,os

class pb:
    def __init__(self, FIL=None):
        self.RAND = random
        self.RAND.seed(time.time())
        #Operations set
        self.OPS = {"G":0,\
                 "E":0,\
                 "M":0,\
                 "D":0,\
                 "A":1,\
                 "S":1}
        #Greatest value to execute OP on
        self.GREATEST_VAL = 10
        #Including decimal values on mathematical OP
        self.FLOATZ = False
        #Object's problem string
        self.PROBLEM = ""
        #Object's way of identifying that a grouping is in progress
        self.GROUP_TF = False
        #List of OPS to execute
        self.OP_L = []
        #File to specify configs
        self.C_FIL = open("pb.cfg", 'r') if FIL is None else FIL
        #Default calculator cli tool
        self.CALCULATOR = 'calc'

    #Set with file
    def setcfg(self):
        #Read from file
        inpt = self.C_FIL.read().split('\n')
        #Drop empty char at end
        inpt.pop()
        i = -1
        #Remove all comments
        while(i < len(inpt)-1):
            i+=1
            #If starts with comment delimeter
            if inpt[i][0] == '$':
                #Pop and decrement 'i' val
                inpt.pop(i)
                i-=1
        #Set delimeter
        delim = inpt[0]
        #Dummy container just in case CONFIG is faulty
        OPS = {}
        #Set variables
        for i in range(1, len(inpt)):
            #Set calculator
            if i == 1:
                self.CALCULATOR = inpt[i].split(delim)[1]
                continue
            #Set configuration options
            OPS[inpt[i].split(delim)[0]] = int(inpt[i].split(delim)[1])
        #Close file
        self.C_FIL.close()

        GT_0 = False
        #Go through each of (M,D,A,S) to ensure one of them holds greater than 0
        for OP in ['M', 'D', 'A', 'S']:
            if OPS[OP] > 0:
                GT_0 = True
            if GT_0:
                break
        self.OPS = OPS

    #Make grouping
    def mkgrp(self, OTHER_VAL_AHEAD_IN_LIST):
        self.PROBLEM += str("%s " % ('+ (' if not self.GROUP_TF else ')'))
        self.GROUP_TF = not self.GROUP_TF

    #Make exponent
    def mkexp(self, OTHER_VAL_AHEAD_IN_LIST):
        self.PROBLEM += str("^(%d) " % (self.RAND.randint(a=0, b=self.GREATEST_VAL)))

    #Make multiplication
    def mkmul(self, OTHER_VAL_AHEAD_IN_LIST):
        self.PROBLEM += str("%s* %d " % ('1 ' if (self.GROUP_TF and OTHER_VAL_AHEAD_IN_LIST == 'G') else "", self.RAND.randint(a=0, b=self.GREATEST_VAL)))

    #Make division
    def mkdiv(self, OTHER_VAL_AHEAD_IN_LIST):
        self.PROBLEM += str("%s/ %d " % ('1 ' if (self.GROUP_TF and OTHER_VAL_AHEAD_IN_LIST == 'G') else "", self.RAND.randint(a=0, b=self.GREATEST_VAL)))

    #Make addition
    def mkadd(self, OTHER_VAL_AHEAD_IN_LIST):
        self.PROBLEM += str("+ %d " % (self.RAND.randint(a=0, b=self.GREATEST_VAL)))

    #Make subtraction
    def mksub(self, OTHER_VAL_AHEAD_IN_LIST):
        self.PROBLEM += str("- %d " % (self.RAND.randint(a=0, b=self.GREATEST_VAL)))

    #Initialize listing
    def initializeList(self):
        #Run through config file
        if self.C_FIL is not None:
            self.setcfg()
        op_chance_percent = 0
        #There will always be an OP running, but which one will be at random
        FOR_SURE_OP = False
        for OP in self.OPS:
            op_chance_percent += 33
            if OP in ['M', 'A', 'S'] and not FOR_SURE_OP and self.OPS[OP] != 0:
                if self.RAND.randint(a=0, b=100) < op_chance_percent:
                    FOR_SURE_OP = True
                    for i in range(self.OPS[OP]):
                        self.OP_L.append(OP)
            elif FOR_SURE_OP:
                for i in range((self.RAND.randint(a=0, b=self.OPS[OP]) if OP != 'G' else self.OPS[OP])):
                    self.OP_L.append(OP)

        #Randomize the list
        self.RAND.shuffle(self.OP_L)

        #Verify that GROUPINGS don't occur next to each other
        i = 0
        while(i < len(self.OP_L)):
            if i > 0 and self.OP_L[i] == 'G' and self.OP_L[i] == self.OP_L[i-1]:
                    i-=1
                    self.OP_L.pop(i)
                    self.OP_L.pop(i)
            i += 1


        #print(self.OP_L)

    #Run
    def run(self):
        while(self.PROBLEM == ""):
            #initialize listing
            self.initializeList()


            I = -1
            OP_LAST = "FILLER"
            for OP in self.OP_L:
                I+=1
                #Start off problem
                if I == 0:
                    self.PROBLEM = str("%d " % (self.RAND.randint(0, self.GREATEST_VAL)))
                #if OP not in ['G', 'E', 'M', 'D'] and I == 0:

                if OP == 'G':
                    self.mkgrp(OP_LAST)
                if OP == 'E' and I != 0 and not self.GROUP_TF:
                    self.mkexp(OP_LAST)
                if OP == 'M' and I != 0:
                    self.mkmul(OP_LAST)
                if OP == 'D' and I != 0:
                    self.mkdiv(OP_LAST)
                if OP == 'A':
                    self.mkadd(OP_LAST)
                if OP == 'S':
                    self.mksub(OP_LAST)
                if len(self.PROBLEM) > 0 and self.PROBLEM[0] in ['*', '/']:
                    self.PROBLEM = ""
                OP_LAST = OP

        print(self.PROBLEM)
        #Write equation to EQUATION file
        with open("EQUATION", 'w') as EQ:
            EQ.write(self.PROBLEM)

        #Calculate equation with calculator command
        os.system("%s \"%s\" > RESULT" % (self.CALCULATOR, self.PROBLEM))

prob = pb()
prob.run()
