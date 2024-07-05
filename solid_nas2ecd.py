#!/vcc/ans/sim/vccpython3/1.2_ln64/bin/python
# -*- coding: iso-8859-15 -*-
# Created by: Caroline de Coster
# Comments: 
#Updated by Karin Kvickstrom 2019-07-04
#########################
#
import pmob_ecd
import eigen_ecd
#import vtf_ecd
import static_stiffness_ecd
import eqs_ecd
import inertia_relief_stiffness_ecd
import freq_resp_ecd
import sys

#added
from os import listdir
from os.path import isfile, join

try:
		# for Python2
	from Tkinter import *   ## notice capitalized T in Tkinter 
except ImportError:
	# for Python3
	from tkinter import filedialog
from tkinter import *   ## notice lowercase 't' in tkinter here

master = Tk()
master.title('nas2ecd')

def errorWindow(title, descr, geo): #creates an error window with specified title, text and geometry
	window = Tk()
	window.title(title)
	Label(window, text=descr, fg='red').grid(row=0, column=0)
	window.columnconfigure(0, weight=1)
	window.rowconfigure(0, weight=1)
	window.geometry(geo)
	Label(window).grid(row=8,column=0)
	b1 = Button(window, text='OK', command=window.quit)
	b1.grid(row=9, column=0)
	mainloop()
	window.destroy()
	master.destroy()
	sys.exit()

def latestFile(filePath): #finds most recent material card
	files = [f for f in listdir(filePath) if isfile(join(filePath, f))] #takes all files in the directory
	dates = []
	for file in files: #make a list of the dates
		dateNas = file.split('_')[-1]
		date = dateNas.split('.')[0]
		date = int(date)
		dates.append(date)
	dates.sort()
	latest = dates[-1]  #choose the most recent date
	correctFile = ''
	for file in files:
		dateNas = file.split('_')[-1] #the date is at the end of the file name
		date = dateNas.split('.')[0] #remove the .nas
		date = int(date)
		if date == latest: #if the file has the most recent date, return it!
			correctFile = file 
	return correctFile

nasFile = filedialog.askopenfilename() #gets file from pop-up directory
if (nasFile == ()): #If cancel is pressed in file selection window
	errorWindow('Run ended', 'Application was cancelled, press OK', '250x100')


elif (nasFile.split('.')[-1] != 'nas'): #If a file other than .nas is chosen
	errorWindow('Wrong file type', 
			 'Did not provide .nas file. \n Press OK and try again with a different file', "250x100")

#below was replaced by the file selection window (filedialog.askopenfilename())
#Label(master).grid(row=0,column=0)
#Label(master, text='Nastran file with .nas:').grid(row=1, column=0)
#content0=nasFile
#e0=Entry(master, textvariable=content0).grid(row=1, column=1)

Label(master, text='Analysis type:').grid(row=1, column=0)
#option menu for analysis type
var1 = StringVar(master)
var1.set('') #default value
l1 = OptionMenu(master, var1, 'pmob', 'eigen' ,'vtf', 'static stiffness', 'eqs', 'body attachment stiffness', 'freq_resp')
l1.grid(row=1, column=1)

#fetching the latest material card in each directory.
polymerPath = '/vcc/cae/backup/common/spdrm/DM/LIBRARY_ITEMS/materials/nastran/91520_ansa_nastran_mat_polymers_and_foams'
polymerFile = latestFile(polymerPath) #file name
fullPolymer = polymerPath + '/' + polymerFile #full directory
matPath = '/vcc/cae/backup/common/spdrm/DM/LIBRARY_ITEMS/materials/nastran/91520_ansa_nastran_mat'
matFile = latestFile(matPath) #file name
fullMat = matPath + '/' + matFile #full directory
pidPath = '/vcc/cae/backup/common/spdrm/DM/LIBRARY_ITEMS/materials/nastran/91520_nastran_joining_pid'
pidFile = latestFile(pidPath) #file name
fullPid = pidPath + '/' + pidFile #full directory

#first drop-down list of materialcards
Label(master, text='Material card #1:').grid(row=2, column=0)
#option menu for analysis type
var2 = StringVar(master)
var2.set('') #default value
l2 = OptionMenu(master, var2, polymerFile,matFile,pidFile)
l2.grid(row=2, column=1)

#identical drop-down list, if a second material card is needed.
Label(master, text='Material card #2:').grid(row=3, column=0)
#option menu for analysis type
var3 = StringVar(master)
var3.set('') #default value
l3 = OptionMenu(master, var3, polymerFile,matFile,pidFile)
l3.grid(row=3, column=1)

#identical drop-down list, if a second material card is needed.
Label(master, text='Material card #3:').grid(row=4, column=0)
#option menu for analysis type
var4 = StringVar(master)
var4.set('') #default value
l4 = OptionMenu(master, var4, polymerFile,matFile,pidFile)
l4.grid(row=4, column=1)

Label(master,text='Specify the excitation points (commma separated) \n [pmob, vtf, static, eqs, freq_resp]:').grid(row=5, column=0)
content1=StringVar()
e1=Entry(master, textvariable=content1).grid(row=5, column=1)

Label(master,text='Maximum frequency? [eigen, freq_resp]:').grid(row=6,column=0)
content2=StringVar()
e2=Entry(master, textvariable=content2).grid(row=6, column=1)
content2.set('50')

Label(master,text='Specify the response points [vtf];').grid(row=7, column=0)
content3=StringVar()
e3=Entry(master, textvariable=content3).grid(row=7, column=1)

Label(master,text='SPC ID if needed:').grid(row=8, column=0)
content4=StringVar()
e4=Entry(master, textvariable=content4).grid(row=8, column=1)

Label(master,text='Which direction?(for freq_resp) 1=x, 2=y, 3=z').grid(row=9, column=0)
content5=StringVar()
e5=Entry(master, textvariable=content5).grid(row=9, column=1)

def callback():
	master.destroy()

def removeSpaces(string):
	string = string.replace(' ','')
	return string

Label(master).grid(row=10,column=0)
b1 = Button(master, text='OK', command=master.quit)
b1.grid(row=11, column=0)
b2 = Button(master, text='Cancel', command=callback)
b2.grid(row=11, column=1)

mainloop()

#We want the entire paths stored in the variable, but only the file in the window
#Therefore, we retrieve the full path for each of the chosen material cards
material1 = '' 
if (var2.get()==polymerFile):
	material1 = fullPolymer
elif (var2.get()==matFile):
	material1 = fullMat
elif (var2.get()==pidFile):
	material1 = fullPid

material2 = '' 
if (var3.get()==polymerFile):
	material2 = fullPolymer
elif (var3.get()==matFile):
	material2 = fullMat
elif (var3.get()==pidFile):
	material2 = fullPid

material3 = '' 
if (var4.get()==polymerFile):
	material3 = fullPolymer
elif (var4.get()==matFile):
	material3 = fullMat
elif (var4.get()==pidFile):
	material3 = fullPid

grid_values = content1.get()
#Empty input is OK, not necessary to give excitation points. 
#Otherwise, it must be comma separated values, not ex a string.
if (grid_values != ''): 
	grid_values = grid_values.split(',')
	grid_values = [removeSpaces(i) for i in grid_values]
	try: #Make the input an array of ints
		grid_values = [int(i) for i in grid_values]
	#Will throw value error if the input is not comma separated values. Instead, create an error window
	except (ValueError): 
		errorWindow('Run ended', 'Invalid input, press OK and try again', '250x100')
	grid_values = sorted(grid_values)
	grid_values = ' '.join(str(e) for e in grid_values) #sorted and space separated

frequency_value = content2.get()
response_values = content3.get()
spc_values = content4.get()
direction_values = content5.get()

try:
	callback()  #Need to close ecd-window if not already cancelled
except (TclError): #If already closed, it throws an TclError for trying to close an already destroyed application
	print('') #Don't need to do anything, the application is already closed.

if var1.get() == 'pmob':
	file = open('input_values.txt', 'w')
	file.write(nasFile)
	file.write('\n')
	file.write(grid_values)
	file.write('\n')
	file.write(spc_values)
	file.write('\n') 
	file.write(material1) 
	file.write('\n') 
	file.write(material2) 
	file.write('\n') 
	file.write(material3) 
	file.close()
	pmob_ecd.main()
elif var1.get() == 'eigen':
	file = open('input_values.txt', 'w')
	file.write(nasFile)
	file.write('\n')
	file.write(frequency_value)
	file.write('\n')
	file.write(spc_values)
	file.write('\n') 
	file.write(material1) 
	file.write('\n') 
	file.write(material2)
	file.write('\n') 
	file.write(material3) 
	file.close()
	eigen_ecd.main()
elif var1.get() == 'vtf':
	file = open('input_values.txt', 'w')
	file.write(nasFile)
	file.write('\n')
	file.write(grid_values)
	file.write('\n')
	file.write(response_values)
	file.write('\n')
	file.write(spc_values)
	file.write('\n') 
	file.write(material1) 
	file.write('\n') 
	file.write(material2)
	file.write('\n') 
	file.write(material3) 
	file.close()
	vtf_ecd.main()
elif var1.get() == 'static stiffness':
	file = open('input_values.txt', 'w')
	file.write(nasFile)
	file.write('\n')
	file.write(grid_values)
	file.write('\n')
	file.write(spc_values)
	file.write('\n') 
	file.write(material1) 
	file.write('\n') 
	file.write(material2)
	file.write('\n') 
	file.write(material3) 
	file.close()
	static_stiffness_ecd.main()
elif var1.get() == 'eqs':
	file = open('input_values.txt', 'w')
	file.write(nasFile)
	file.write('\n')
	file.write(grid_values)
	file.write('\n')
	file.write(spc_values)
	file.write('\n') 
	file.write(material1) 
	file.write('\n') 
	file.write(material2)
	file.write('\n') 
	file.write(material3) 
	file.close()
	eqs_ecd.main()
elif var1.get() == 'body attachment stiffness':
	file = open('input_values.txt', 'w')
	file.write(nasFile)
	file.write('\n')
	file.write(grid_values)
	file.write('\n')
	file.write(spc_values)
	file.write('\n') 
	file.write(material1) 
	file.write('\n') 
	file.write(material2)
	file.write('\n') 
	file.write(material3) 
	file.close()
	inertia_relief_stiffness_ecd.main()
elif var1.get() == 'freq_resp':
	file = open('input_values.txt', 'w')
	file.write(nasFile)
	file.write('\n')
	file.write(frequency_value)
	file.write('\n')
	file.write(grid_values)
	file.write('\n')
	file.write(direction_values)
	file.write('\n')
	file.write(spc_values)
	file.write('\n') 
	file.write(material1) 
	file.write('\n') 
	file.write(material2)
	file.write('\n') 
	file.write(material3) 
	file.close()
	freq_resp_ecd.main()
