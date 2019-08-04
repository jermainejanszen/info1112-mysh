# ---------	#
# Imports	#
# ---------	#
import os
import sys
import time

# ---------------------------------------------	#
# Initial variables, lists, and dictionaries	#
# ---------------------------------------------	#
running = True 									# used to maintain interactive shell
shellVariables = {} 							# used to store shell variables
shellVariables["PS"] = "$"						# initializes 'PS' to '$'
inputList = []									# used to keep user input where each element is a new word/command
historyList = []								# used to store which directories have been visited
historyList.append(os.getcwd())					# adds starting directory to history list
redirectOut = False								# used to indicate whether output is to be directed to a file
redirectIn = False								# used to indicate whether input is coming from a file
hasRedirectIn = False							# remembers whether a redirection in has happened
piping = False									# used to indicate whether the user wishes to pipe
redirectOutIndex = 0							# remembers index of the '>' symbol
redirectInIndex = 0								# remembers index of the '<' symbol
outFile = None									# initializes a global file that will be used for redirected output
defaultStdOut = os.dup(sys.stdout.fileno())		# remembers fd of standard output
defaultStdIn = os.dup(sys.stdin.fileno())		# remembers fd of standard input
takeInput = False								# used to indicate whether or not the user must manually enter input

# -------------------------------------------------	#
# Define methods not directly used in this shell	#
# -------------------------------------------------	#

# readInput:
#		Reads input from standard input or a file and processes line continuation
#		Returns a list containing the input where each element is a word/command
def readInput(user = True, f = "") :
	global takeInput
	read = True		# used to loop for line continuation
	readList = []	# used to store input and returned when complete
	if(user) :
		if(not takeInput) :	# mostly used when running a script and instructions must be read off a file 
			a = input()
		else :
			a = input(shellVariables["PS"] + " ")
		if(a == "") :
			readList.append("")
			return readList
	else :
		a = f
	readList = a.split(" ")										# splits the input into its individual words
	while(read) :												# processing line continuation
		if(readList[len(readList) - 1] == "\\") :				# if the last element is '\'
			readList.pop(len(readList) - 1)
			if(not takeInput) :									# continue to read input for next line
				a = input()
			else :
				a = input("> ")
			nextLineList = a.split(" ")
			for index in range(len(nextLineList)) :				# append the next line input to the original list
				readList.append(nextLineList[index])
		elif(readList[len(readList) - 1].endswith("\\")) :		# if the last element ends with '\'
			lastElementLst = list(readList[len(readList) - 1])	# removing the '\' from the last element
			lastElementLst.remove("\\")
			lastElement = "".join(lastElementLst)
			readList.pop(len(readList) - 1)
			if(not takeInput) :									# continue to read input for the next line
				a = input()
			else :
				a = input("> ")
			nextLineList = a.split(" ")
			firstInput = lastElement + nextLineList[0]			# joins the last word of the original list with the first -
			nextLineList.pop(0)									# of the new line
			nextLineList.insert(0, firstInput)
			for index in range(len(nextLineList)) :				# append the next line input to the original list
				readList.append(nextLineList[index])
		else :													# otherwise input is complete and the list can be returned
			read = False
	while("" in readList) :
		readList.remove("")
	return readList

# ---------------------------------------------	#
# Define methods directly used in this shell	#
# ---------------------------------------------	#

# exit:
#		Terminates the program
#		Returns nothing
def exit() :
	sys.exit()
	return

# say:
#		Takes in a list and builds a string out of its elements.
#		Returns a string
def say(inputListTemp, hasRedirectIn) :
	outputStr = ""
	if(hasRedirectIn) :									# ensures output from a file is not returned
		return outputStr
	if(len(inputListTemp) == 1) :						# if no input beyond the 'say' command, returns empty string
		return outputStr
	for index in range(1, len(inputListTemp)) :			# adds each word to the output string
		if(index < (len(inputListTemp) - 1)) :
			outputStr += inputListTemp[index] + " "		# puts a " " between each word except
		if(index == len(inputListTemp) - 1) :
			outputStr += inputListTemp[index]			# does not add a " " after the last word
	return outputStr

# changedir:
#		Takes in a list of words, a dictionary of variables, and a historylist of directories.
#		Changes the current directly to that stated in the input list and updates the historylist.
#		If no directory is specified, the current directory is changed to the directory labeled 'HOME'.
#		If 'HOME' does not exist, do nothing.
#		Returns nothing
def changdir(inputList, shellVariables, historyList) :
	if(len(inputList) == 1) :						# if not input is given:
		if("HOME" in shellVariables) :				# if user defined a 'HOME' path change to it
			os.chdir(shellVariables["HOME"])
			historyList.insert(0, os.getcwd())
		else :
			return
	elif(os.path.isdir(inputList[1])) :				# otherwise change to the path the user has inputed
		os.chdir(inputList[1])
		historyList.insert(0, os.getcwd())
	else :
		return

# showdir:
#		Returns current directory as string
def showdir() :
	return os.getcwd()

# historylist:
#		Iterates through the given historylist and creates a string of the contents to return.
#		Returns historylist as string
def historylist(historyList) :
	historyStr = ""															# initialises empty string
	for index in range(len(historyList)) :
		historyStr += "{}: {}".format(index, historyList[index]) + "\n"		# adds each item in historylist
	historyStr = historyStr[:-1]											# removes final new line
	return historyStr

# cdn: 
#		Changes the current directory to a given index on the historylist and erases previous additions.
#		Returns nothing
def cdn(inputList, historyList) :
	if(len(inputList) == 1) :				# returns if no input is given
		return
	try :
		checkInt = int(inputList[1])		# checks if input given is an int
	except :
		return								# if not an int, continue without doing anything
	if(checkInt) >= len(historyList) :		# checks if int is within correct domain
		return
	os.chdir(historyList[checkInt])			# changes path to that specified on historylist
	for index in range(checkInt) :			# removes earlier entries on historylist
		historyList.pop(0)
	return

# show:
#		Shows the contents of files in the given input list.
#		If no files are given it allows the user to input text to be returned as a string.
# 		Returns a string
def show(inputList, shellVariables = None) :
	global hasRedirectIn
	if(len(inputList) == 1) :								# checks if user must input
		shellVariables["PS"] = ">"
		a = readInput()										# reads user input
		a.insert(0, "ignore")
		shellVariables["PS"] = "$"
		outStr = say(a, False)								# processes user input into a string
		return outStr
	else :
		contents = ""
		for index in range(1, len(inputList)) :
			if(not hasRedirectIn) :							# checks if input is already from a file or not
				if(os.path.isfile(inputList[index])) :		
					file = open(inputList[index], "r")
					if(file.readable()) :
						if(index == len(inputList) - 1) :	# appends contents of the file to a string
							contents += file.read()
						else :
							contents += file.read()
							contents += "\n"	
				else :										# if input is not a file
					if(index == len(inputList) - 1) :		
						contents += inputList[index]		# simply appends the input to a string
					else :
						contents += inputList[index] + " "	
			else :											# if input is already from a file
				if(index == len(inputList) - 1) :			
					contents += inputList[index]			# simply appends the input to a string
				else :
					contents += inputList[index] + " "
		return contents										# returns the string

# set:
#		Sets new shell variables based on given input list. If no input is given all existing variables
#		are printed in alphabetical order.
#		Returns variables as string if not setting new variables, otherwise returns nothing
def setvar(inputList, shellVariables) :
	if(len(inputList) == 1) :							# checks if user wishes to print list of variables
		varOutput = ""
		for key, value in sorted(shellVariables.items(), key=lambda x: x[0].lower()) :	# sorts variables alphabetically
			varOutput += key + "=" + value + "\n"
		varOutput = varOutput[:-1]						# removes final new line
		return varOutput
	elif(len(inputList) == 2) :							# creates new variable without a value (empty string)
		shellVariables[inputList[1]] = ""
	else :
		valueList = inputList.copy()
		valueList.pop(0)
		valueList.pop(0)
		value = " ".join(valueList)						# combines words after 'set' and the variable name into a string
		shellVariables[inputList[1]] = value			# creates new variable with value of the combined words
	return

# unset:
#		Deletes shell variables that are listed in input list
#		Returns nothing
def unset(inputList, shellVariables) :
	if(len(inputList) == 1) :
		return
	for index in range(1, len(inputList)) :				# checks each element in input after 'unset'
		if(inputList[index] in shellVariables) :
			shellVariables.pop(inputList[index])		# removes desired variable if it exists
	return

# sleep:
#		Sleeps for the given number of seconds in the input list
#		Returns nothing
def sleep(inputList) :
	if(len(inputList) == 1) :
		return
	try :
		timeToSleep = float(inputList[1])		# checks if input is a number
	except :
		return
	time.sleep(timeToSleep)						# sleeps desired number of seconds
	return

# -------------------------------------------------	#
# Main shell method where commands are processed	#
# -------------------------------------------------	#
def mainShell(givenList = inputList, hasRedirectIn = hasRedirectIn) :
	global shellVariables

	# replace shell variables
	for index in range(len(givenList)) :
		if(givenList[index].startswith("$")) :
			tempElementLst = list(givenList[index])					# removes '$' from variable element
			tempElementLst.remove("$")
			tempElement = "".join(tempElementLst)
			if(tempElement in shellVariables) :
				givenList[index] = shellVariables[tempElement]		# replaces variable with its value
			else :
				givenList[index] = ""
	if(len(givenList) > 1) :										# removes empty strings if invalid variables were given
		while "" in givenList :
			givenList.remove("")
	
	# piping:
	#		Creates left and right side of pipe in list form. Executes the left side and records output.
	#		Feeds output when executing the right side.
	#		Can run recursively if multiple pipes exist.
	if "|" in givenList :
		pipingIndex = givenList.index("|")
		leftSide = []
		rightSide = []
		for index in givenList :									# updates left side list
			if(index != "|") :
				leftSide.append(index)
			else :
				break
		for index in range((pipingIndex + 1), len(givenList)) :		# updates right side list
			rightSide.append(givenList[index])
		toWrite = mainShell(leftSide)								# executes left side and returns output
		leftFile = open("left", "w")								# writes output to file
		leftFile.write(toWrite)
		leftFile.close()
		if "|" in rightSide :										# updates right side to take file as input
			nextIndex = rightSide.index("|")
			rightSide.insert(nextIndex, "<")
			rightSide.insert(nextIndex + 1, "left")
		else :
			rightSide.append("<")
			rightSide.append("left")
		return mainShell(rightSide)									# executes right side.
																	# runs recursively if multiple pipes exist
	# redirect in:
	#		Replaces "< 'filename'" with contents of file.
	if("<" in givenList) :
		redirectIn = True
		hasRedirectIn = True
		redirectInIndex = givenList.index("<")
		if(os.path.isfile(givenList[redirectInIndex + 1])) :		# checks if redirecting in a file
			file = open(givenList[redirectInIndex + 1], "r")
			fileContents = file.read()								# reads file to a string
			givenList.remove("<")
			givenList.pop(redirectInIndex)
			fileContentsLst = readInput(False, fileContents)		# converts string to a list
			for index in range(0, len(fileContentsLst)) :			# appends list to the input list
				givenList.insert(redirectInIndex + index, fileContentsLst[index])
			file.close()
		else :
			givenList.remove("<")									# if file doesn't exist, gets rid of redirect in
			givenList.pop(redirectInIndex)
		
		redirectIn = False
				
	# redirect out:
	#		Creates a file where output will be written to.
	if(">" in givenList) :
		global redirectOut
		redirectOutIndex = givenList.index(">")
		if(redirectOutIndex != (len(givenList) - 1)) :				# checks if '>' is the last element in input
			redirectOut = True
		else :
			givenList.remove(">")
		if(redirectOut) :
			global outFile
			outFile = open(givenList[redirectOutIndex + 1], "w")	# creates file with desired name
			givenList.pop(redirectOutIndex)							# removes '>' and filename
			givenList.pop(redirectOutIndex)

	# if input is a path
	#		Forks and executes program at given path, redirecting standard output if necessary.
	if(givenList[0].startswith("/")) :
		if(os.path.exists(givenList[0])) :
			if(os.access(givenList[0], os.X_OK)) :
				pid = os.fork()
				if(pid == 0) :
					if(redirectOut) :									# updates standard output to redirect out file
						os.dup2(outFile.fileno(), sys.stdout.fileno())
					os.execv(givenList[0], givenList)					# executes program at given path
				else :
					os.wait()
					if(redirectOut) :									# resets standard output
						os.dup2(defaultStdOut, sys.stdout.fileno())
						redirectOut = False
		else :
			return "Unable to execute {}".format(givenList[0])			# return if unable to execute given path
	
# ------------------------------------- #
# Check for desired command to execute	#
# ------------------------------------- #
	# exit
	if(givenList[0] == "exit") :
		print("Goodbye!")
		return exit()
		
	# say
	if(givenList[0] == "say") :
		return say(givenList, hasRedirectIn)
	
	# changedir
	if(givenList[0] == "changedir") :
		return changdir(inputList, shellVariables, historyList)
	
	# showdir
	if(givenList[0] == "showdir") :
		return showdir()
	
	# historylist
	if(givenList[0] == "historylist") :
		return historylist(historyList)
	
	# cdn
	if(givenList[0] == "cdn") :
		return cdn(givenList, historyList)
	
	# show
	if(givenList[0] == "show") :
		return show(givenList, shellVariables)
	
	# set
	if(givenList[0] == "set") :
		return setvar(givenList, shellVariables)
	
	# unset
	if(givenList[0] == "unset") :
		return unset(givenList, shellVariables)
	
	# sleep
	if(givenList[0] == "sleep") :
		return sleep(givenList)

# -------------	#
# Shell loop	#
# -------------	#
try :
	while(running) :
		
		if(len(sys.argv) == 1) :					# check if mysh.py is to run interactively
			takeInput = True
		
		if(takeInput) :								# allow user input if in interactive mode
			inputList = readInput()
		else :
			inputList = sys.argv.copy()				# otherwise take commandline arguments given when mysh was called
			inputList.pop(0)
			running = False
		
		if(len(inputList) == 0) :					# do nothing if no input was given
			continue
		
		if "|" in inputList :						# checks for pipes
			piping = True
		
		# running scripts from external files
		if(not takeInput) :							# if not in interactive mode
			for index in inputList :
				if(os.path.isfile(index)) :
					execFile = open(index, "r")
					os.dup2(execFile.fileno(), sys.stdin.fileno())		# change given file to standard input
					try :
						while(True) :
							inputList = readInput()						# read commands from file
							toPrint = mainShell(inputList)				# execute commands
							if(toPrint == None) :						# if no output, print nothing
								continue
							else :
								if(not redirectOut) :					# print to std. out if not redirecting
									print(toPrint)
								else :									# otherwise write to given file name
									print(toPrint, end = "", file = outFile)
									outFile.close()
									redirectOut = False
					except :
						running = False
				else :
					print("Unable to execute {}".format(index))			# print if unable to find file
		else :															# if in interactive mode:
			toPrint = mainShell(inputList)								# execute commands given
			if(toPrint == None) :
				continue
			else :
				if(not redirectOut) :									# print to std. out if not redirecting
					print(toPrint)
				else :
					print(toPrint, end = "", file = outFile)			# write to file if redirecting out
					outFile.close()
					redirectOut = False
		
		os.dup2(defaultStdOut, sys.stdout.fileno())						# reset std out and in for the next loop
		os.dup2(defaultStdIn, sys.stdin.fileno())	
		
except :
	running = False														# stops the shell running

