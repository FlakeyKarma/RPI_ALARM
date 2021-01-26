#!/bin/python2.7

import RPi.GPIO as GPIO
import threading,proBuildr as PB
from time import sleep
# start main demo function
#main()

class LCD:
	# commands
	LCD_CLEARDISPLAY 		= 0x01
	LCD_RETURNHOME 		   = 0x02
	LCD_ENTRYMODESET 		= 0x04
	LCD_DISPLAYCONTROL 		= 0x08
	LCD_CURSORSHIFT 		= 0x10
	LCD_FUNCTIONSET 		= 0x20
	LCD_SETCGRAMADDR 		= 0x40
	LCD_SETDDRAMADDR 		= 0x80

	# flags for display entry mode
	LCD_ENTRYRIGHT 		= 0x00
	LCD_ENTRYLEFT 		= 0x02
	LCD_ENTRYSHIFTINCREMENT 	= 0x01
	LCD_ENTRYSHIFTDECREMENT 	= 0x00

	# flags for display on/off control
	LCD_DISPLAYON 		= 0x04
	LCD_DISPLAYOFF 		= 0x00
	LCD_CURSORON 		= 0x02
	LCD_CURSOROFF 		= 0x00
	LCD_BLINKON 		= 0x01
	LCD_BLINKOFF 		= 0x00

	# flags for display/cursor shift
	LCD_DISPLAYMOVE 	= 0x08
	LCD_CURSORMOVE 		= 0x00

	# flags for display/cursor shift
	LCD_DISPLAYMOVE 	= 0x08
	LCD_CURSORMOVE 		= 0x00
	LCD_MOVERIGHT 		= 0x04
	LCD_MOVELEFT 		= 0x00

	# flags for function set
	LCD_8BITMODE 		= 0x10
	LCD_4BITMODE 		= 0x00
	LCD_2LINE 			= 0x08
	LCD_1LINE 			= 0x00
	LCD_5x10DOTS 		= 0x04
	LCD_5x8DOTS 		= 0x00

	def __init__(self, pin_rs=7, pin_e=8, pins_db=[25, 24, 23, 22], GPIO = None):
		# Emulate the old behavior of using RPi.GPIO if we haven't been given
		# an explicit GPIO interface to use
		if not GPIO:
			import RPi.GPIO as GPIO
			self.GPIO = GPIO
			self.pin_rs = pin_rs
			self.pin_e = pin_e
			self.pins_db = pins_db

			self.used_gpio = self.pins_db[:]
			self.used_gpio.append(pin_e)
			self.used_gpio.append(pin_rs)

			self.GPIO.setwarnings(False)
			self.GPIO.setmode(GPIO.BCM)
			self.GPIO.setup(self.pin_e, GPIO.OUT)
			self.GPIO.setup(self.pin_rs, GPIO.OUT)

			for pin in self.pins_db:
				self.GPIO.setup(pin, GPIO.OUT)

		self.write4bits(0x33) # initialization
		self.write4bits(0x32) # initialization
		self.write4bits(0x28) # 2 line 5x7 matrix
		self.write4bits(0x0C) # turn cursor off 0x0E to enable cursor
		self.write4bits(0x06) # shift cursor right

		self.displaycontrol = self.LCD_DISPLAYON | self.LCD_CURSOROFF | self.LCD_BLINKOFF

		self.displayfunction = self.LCD_4BITMODE | self.LCD_1LINE | self.LCD_5x8DOTS
		self.displayfunction |= self.LCD_2LINE

		""" Initialize to default text direction (for romance languages) """
		self.displaymode =  self.LCD_ENTRYLEFT | self.LCD_ENTRYSHIFTDECREMENT
		self.write4bits(self.LCD_ENTRYMODESET | self.displaymode) #  set the entry mode

		self.clear()

	def begin(self, cols, lines):
		if (lines > 1):
			self.numlines = lines
			self.displayfunction |= self.LCD_2LINE
			self.currline = 0

	def home(self):
		self.write4bits(self.LCD_RETURNHOME) # set cursor position to zero
		self.delayMicroseconds(3000) # this command takes a long time!

	def clear(self):
		self.write4bits(self.LCD_CLEARDISPLAY) # command to clear display
		self.delayMicroseconds(3000)	# 3000 microsecond sleep, clearing the display takes a long time

	def setCursor(self, col, row):
		self.row_offsets = [ 0x00, 0x40, 0x14, 0x54 ]

		if ( row > self.numlines ):
			row = self.numlines - 1 # we count rows starting w/0

		self.write4bits(self.LCD_SETDDRAMADDR | (col + self.row_offsets[row]))

	def noDisplay(self):
		# Turn the display off (quickly)
		self.displaycontrol &= ~self.LCD_DISPLAYON
		self.write4bits(self.LCD_DISPLAYCONTROL | self.displaycontrol)

	def display(self):
		# Turn the display on (quickly)
		self.displaycontrol |= self.LCD_DISPLAYON
		self.write4bits(self.LCD_DISPLAYCONTROL | self.displaycontrol)

	def noCursor(self):
		# Turns the underline cursor on/off
		self.displaycontrol &= ~self.LCD_CURSORON
		self.write4bits(self.LCD_DISPLAYCONTROL | self.displaycontrol)

	def cursor(self):
		# Cursor On
		self.displaycontrol |= self.LCD_CURSORON
		self.write4bits(self.LCD_DISPLAYCONTROL | self.displaycontrol)

	def noBlink(self):
		# Turn on and off the blinking cursor
		self.displaycontrol &= ~self.LCD_BLINKON
		self.write4bits(self.LCD_DISPLAYCONTROL | self.displaycontrol)

	def noBlink(self):
		# Turn on and off the blinking cursor
		self.displaycontrol &= ~self.LCD_BLINKON
		self.write4bits(self.LCD_DISPLAYCONTROL | self.displaycontrol)

	def DisplayLeft(self):
		# These commands scroll the display without changing the RAM
		self.write4bits(self.LCD_CURSORSHIFT | self.LCD_DISPLAYMOVE | self.LCD_MOVELEFT)

	def scrollDisplayRight(self):
		# These commands scroll the display without changing the RAM
		self.write4bits(self.LCD_CURSORSHIFT | self.LCD_DISPLAYMOVE | self.LCD_MOVERIGHT);

	def leftToRight(self):
		# This is for text that flows Left to Right
		self.displaymode |= self.LCD_ENTRYLEFT
		self.write4bits(self.LCD_ENTRYMODESET | self.displaymode);

	def rightToLeft(self):
		# This is for text that flows Right to Left
		self.displaymode &= ~self.LCD_ENTRYLEFT
		self.write4bits(self.LCD_ENTRYMODESET | self.displaymode)

	def autoscroll(self):
		# This will 'right justify' text from the cursor
		self.displaymode |= self.LCD_ENTRYSHIFTINCREMENT
		self.write4bits(self.LCD_ENTRYMODESET | self.displaymode)

	def noAutoscroll(self):
		# This will 'left justify' text from the cursor
		self.displaymode &= ~self.LCD_ENTRYSHIFTINCREMENT
		self.write4bits(self.LCD_ENTRYMODESET | self.displaymode)

	def write4bits(self, bits, char_mode=False):
		# Send command to LCD
		#self.delayMicroseconds(1000) # 1000 microsecond sleep
		bits=bin(bits)[2:].zfill(8)
		self.GPIO.output(self.pin_rs, char_mode)
		for pin in self.pins_db:
			self.GPIO.output(pin, False)
		for i in range(4):
			if bits[i] == "1":
				self.GPIO.output(self.pins_db[::-1][i], True)
		self.pulseEnable()
		for pin in self.pins_db:
			self.GPIO.output(pin, False)
		for i in range(4,8):
			if bits[i] == "1":
				self.GPIO.output(self.pins_db[::-1][i-4], True)
		self.pulseEnable()

	def delayMicroseconds(self, microseconds):
		seconds = microseconds / float(1000000)	# divide microseconds by 1 million for seconds
		sleep(seconds)

	def pulseEnable(self):
		self.GPIO.output(self.pin_e, False)
		self.delayMicroseconds(1)		# 1 microsecond pause - enable pulse must be > 450ns
		self.GPIO.output(self.pin_e, True)
		self.delayMicroseconds(1)		# 1 microsecond pause - enable pulse must be > 450ns
		self.GPIO.output(self.pin_e, False)
		self.delayMicroseconds(1)		# commands need > 37us to settle

	def message(self, text):
		# Send string to LCD. Newline wraps to second line
		print "message: %s"%text
		for char in text:
			if char == '\n':
				self.write4bits(0xC0) # next line
			else:
				self.write4bits(ord(char),True)

	def destroy(self):
		print "clean up used_gpio"
		self.GPIO.cleanup(self.used_gpio)

						# GPIO Ports
Enc_A = 9  				# Encoder input A: input GPIO 4
global Enc_B
Enc_B = 10  			       # Encoder input B: input GPIO 14
Enc_C = 5

Rotary_counter = 0  			# Start counting from 0
Current_A = 1					# Assume that rotary switch is not
Current_B = 1					# moving while we init software
Current_C = 1

LockRotary = threading.Lock()		# create lock for rotary switch

# initialize interrupt handlers
def init():
	GPIO.setwarnings(True)
	GPIO.setmode(GPIO.BCM)					# Use BCM mode
									# define the Encoder switch inputs
	GPIO.setup(Enc_A, GPIO.IN)
	GPIO.setup(Enc_B, GPIO.IN)
	GPIO.setup(Enc_C, GPIO.IN)
									# use interrupts for all inputs
	GPIO.add_event_detect(Enc_A, GPIO.RISING, callback=rotary_interrupt) 				# NO bouncetime
	GPIO.add_event_detect(Enc_B, GPIO.RISING, callback=rotary_interrupt) 				# NO bouncetime
	GPIO.add_event_detect(Enc_C, GPIO.RISING, callback=rotary_interrupt) 				# NO bouncetime
	return



# Rotarty encoder interrupt:
# this one is called for both inputs from rotary switch (A and B)
def rotary_interrupt(A_or_B):
	global Rotary_counter, Current_A, Current_B, Current_C, LockRotary, RETURN_VAL
									# read both of the switches
	Switch_A = GPIO.input(Enc_A)
	Switch_B = GPIO.input(Enc_B)
	Switch_C = GPIO.input(Enc_C)


	if Current_A == Switch_A and Current_C == Switch_C and Current_B == Enc_B:		# Same interrupt as before (Bouncing)?
		return							# ignore interrupt!


	Current_A = Switch_A						# remember new state
	Current_B = Switch_B						# for next bouncing check
	Current_C = Switch_C						# for next bouncing check


	if (Switch_A and Switch_B and Switch_C):			# Both one active? Yes -> end of sequence
		LockRotary.acquire()					# get lock
		RETURN_VAL = A_or_B
		if A_or_B == Enc_B:					# Turning direction depends on
			Rotary_counter += 1				# which input gave last interrupt
		else:							# so depending on direction either
			Rotary_counter -= 1				# increase or decrease counter
		LockRotary.release()					# and release lock
	return								# THAT'S IT

# Main loop. Demonstrate reading, direction and speed of turning left/rignt
def main():
	global Rotary_counter, LockRotary
	SCREEN = ['PROBLEM', 'OPTION0', 'OPTION1', 'OPTION2']
	SCREEN_CHOICE = 0
	BOOLEAN_SELECT = False


	Volume = 0							# Current Volume
	NewCounter = 0							# for faster reading with locks


	init()								# Init interrupts, GPIO, ...

	while True :							# start test
		sleep(0.1)						# sleep 100 msec

									# because of threading make sure no thread
									# changes value until we get them
									# and reset them
		LockRotary.acquire()					# get lock for rotary switch
		NewCounter = Rotary_counter			# get counter value
		Rotary_counter = 0					# RESET IT TO 0
		LockRotary.release()					# and release lock

		if (NewCounter !=0):					# Counter has CHANGED
			Volume = Volume + NewCounter*abs(NewCounter)# Decrease or increase volume
			if Volume < 0:					# limit volume to 0...100
			   Volume = 0
			if Volume > 100:				# limit volume to 0...100
			   Volume = 100
			if RETURN_VAL == 9:
			   if SCREEN_CHOICE > 0:
			   	SCREEN_CHOICE -= 1
                            print("LEFT\tSCREEN:%d %s" % (SCREEN_CHOICE, SCREEN[SCREEN_CHOICE]))
			if RETURN_VAL == 5:
			   if SCREEN_CHOICE < len(SCREEN)-1:
				SCREEN_CHOICE += 1
			   print("RIGHT\tSCREEN:%d %s" % (SCREEN_CHOICE, SCREEN[SCREEN_CHOICE]))
			if RETURN_VAL == 10:
                            if SCREEN_CHOICE > 0:
				print("CLICK\tSELECT %s" % (SCREEN[SCREEN_CHOICE]))
				BOOLEAN_SELECT = True


def print_msg():
	print ("========================================")
	print ("|                LCD1602               |")
	print ("|    ------------------------------    |")
	print ("|         D4 connect to BCM25          |")
	print ("|         D5 connect to BCM24          |")
	print ("|         D6 connect to BCM23          |")
	print ("|         D7 connect to BCM18          |")
	print ("|         RS connect to BCM27          |")
	print ("|         CE connect to bcm22          |")
	print ("|          RW connect to GND           |")
	print ("|                                      |")
	print ("|           Control LCD1602            |")
	print ("|                                      |")
	print ("|                            SunFounder|")
	print ("========================================\n")
	print 'Program is running...'
	print 'Please press Ctrl+C to end the program...'
	raw_input ("Press Enter to begin\n")

def txtRet(FIL):
	if(FIL == 'EQUATION'):
		return str(open(FIL, 'r').read())[0:-1]
	if(FIL == 'RESULT'):
		return str(open(FIL, 'r').read()).replace('\t', "")

def main_lcd():
	global Rotary_counter, LockRotary, RETURN_VAL
	PROB = PB.pb()
	PROB.run()
	print(txtRet("EQUATION"), txtRet("RESULT"))
	RESULT = txtRet("RESULT")
	SCREEN = [txtRet("EQUATION"), 'OPTION0', 'OPTION1', 'OPTION2']
	R_VAL = random.randint(1, 3)
	SCREEN[R_VAL] = RESULT
	for i in range(1, 3):
		if i != R_VAL:
			SCREEN[i] = (random.random(0, RESULT+5) if (random.randint(0, 1) == 0) else random.randint(0, RESULT+5))
	SCREEN_CHOICE = 0
        LAST_CHOICE = None
	BOOLEAN_SELECT = False


	Volume = 0							# Current Volume
	NewCounter = 0							# for faster reading with locks


	init()								# Init interrupts, GPIO, ...

        global lcd
        #main()
	print_msg()
	lcd = LCD()

	lcd.clear()
	lcd.message("ALARM_PI\ninitializing...")
	sleep(3)
        lcd.clear()
        lcd.message(SCREEN[SCREEN_CHOICE])
        while True:# start test
            if SCREEN_CHOICE != LAST_CHOICE:
                lcd.clear()
                LAST_CHOICE = SCREEN_CHOICE
                lcd.message(SCREEN[SCREEN_CHOICE])
	   LockRotary.acquire()					# get lock for rotary switch
	   NewCounter = Rotary_counter			# get counter value
	   Rotary_counter = 0						# RESET IT TO 0
	   LockRotary.release()					# and release lock
            if NewCounter != 0:
	       LAST_CHOICE = SCREEN_CHOICE
                if RETURN_VAL == 9:
	           if SCREEN_CHOICE > 0:
		       SCREEN_CHOICE -= 1
                    print("LEFT\tSCREEN:%d %s" % (SCREEN_CHOICE, SCREEN[SCREEN_CHOICE]))
	       if RETURN_VAL == 5:
	           if SCREEN_CHOICE < len(SCREEN)-1:
		       SCREEN_CHOICE += 1
		   print("RIGHT\tSCREEN:%d %s" % (SCREEN_CHOICE, SCREEN[SCREEN_CHOICE]))
	       if RETURN_VAL == 10:
                    if SCREEN_CHOICE > 0:
		       print("CLICK\tSELECT %s" % (SCREEN[SCREEN_CHOICE]))
		       lcd.message('\nSELECTED')
                        BOOLEAN_SELECT = True
                        sleep(3)
                        lcd.clear()
                        lcd.destroy()
                        exit(0)

if __name__ == '__main__':
	try:
		main_lcd()
	except KeyboardInterrupt:
		lcd.clear()
		lcd.destroy()
