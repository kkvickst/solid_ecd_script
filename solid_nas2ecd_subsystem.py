#!/vcc/ans/sim/vccpython3/1.2_ln64/bin/python
# -*- coding: iso-8859-15 -*-
# Created by: Anoob Basheer
# Comments: Skeleton is taken from nas2ecd script
#########################
#
import transient_resp_ecd_v1
import pmob_ecd
import eigen_ecd
#import vtf_ecd
import static_stiffness_ecd
import eqs_ecd
import inertia_relief_stiffness_ecd
#import freq_resp_ecd
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

import tkinter as tk


##nasFile = filedialog.askopenfilename() #gets file from pop-up directory
""" if (nasFile == ()): #If cancel is pressed in file selection window
	errorWindow('Run ended', 'Application was cancelled, press OK', '250x100') """


""" elif (nasFile.split('.')[-1] != 'nas'): #If a file other than .nas is chosen
	errorWindow('Wrong file type', 
			 'Did not provide .nas file. \n Press OK and try again with a different file', "250x100") """

#below was replaced by the file selection window (filedialog.askopenfilename())
#Label(master).grid(row=0,column=0)
#Label(master, text='Nastran file with .nas:').grid(row=1, column=0)
#content0=nasFile
#e0=Entry(master, textvariable=content0).grid(row=1, column=1)


#fetching the latest material card in each directory.
""" polymerPath = '/vcc/cae/backup/common/spdrm/DM/LIBRARY_ITEMS/materials/nastran/91520_ansa_nastran_mat_polymers_and_foams'
polymerFile = latestFile(polymerPath) #file name
fullPolymer = polymerPath + '/' + polymerFile #full directory
matPath = '/vcc/cae/backup/common/spdrm/DM/LIBRARY_ITEMS/materials/nastran/91520_ansa_nastran_mat'
matFile = latestFile(matPath) #file name
fullMat = matPath + '/' + matFile #full directory
pidPath = '/vcc/cae/backup/common/spdrm/DM/LIBRARY_ITEMS/materials/nastran/91520_nastran_joining_pid'
pidFile = latestFile(pidPath) #file name
fullPid = pidPath + '/' + pidFile #full directory """

#first drop-down list of materialcards


""" Label(master, text='Select sub-system nas file:').grid(row=2, column=0)
nassubFile = filedialog.askopenfilename() #gets file from pop-up directory
if (nassubFile == ()): #If cancel is pressed in file selection window
	errorWindow('Run ended', 'Application was cancelled, press OK', '250x100')

elif (nassubFile.split('.')[-1] != 'nas'): #If a file other than .nas is chosen
	errorWindow('Wrong file type', 
			 'Did not provide .nas file. \n Press OK and try again with a different file', "250x100") """

#option menu for analysis type

""" global res_file
res_file = filedialog.askopenfilename(title="Select sub-system file",
                                filetypes=(("*.nas files", "*.nas"), ("all files", "*.*"))) """
    #read_nodes()


""" 	filLabel = tk.Label(master, text=f"Open file: \n {res_file}", wraplength=300, justify="left")
	#filLabel.grid(row=2, column=2, padx=15, pady=15, sticky="w")

	#variable=filename
	#content2=StringVar()
	#content2=variable
	e2=Entry(master, textvariable=filLabel).grid(row=2, column=2)
	print(e2) """

#filLabel = tk.Label(master, text=f"Open file: \n {res_file}", wraplength=300, justify="left")
#filLabel.grid(row=2, column=2, padx=15, pady=15, sticky="w")

#content1=StringVar()
#e1=Entry(master, textvariable=content1).grid(row=2, column=1)

#var2 = StringVar(master)
#var2.set('') #default value
#l2 = OptionMenu(master, nassubFile)
#l2.grid(row=2, column=1)

#grid_values = grid_values.split(',')
#grid_values = [removeSpaces(i) for i in grid_values]
	#try: #Make the input an array of ints
	#	grid_values = [int(i) for i in grid_values]
	#Will throw value error if the input is not comma separated values. Instead, create an error window
	#except (ValueError): 
	#	
#grid_values = sorted(grid_values)
#grid_values = ' '.join(str(e) for e in grid_values) #sorted and space separated


master = Tk()
master.title('sub-system ecd')
selectedfile=StringVar()
selectedfile2=StringVar()
selectedfile3=StringVar()

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

def browseFiles():

	filename = filedialog.askopenfilename(title = "Select nastran File",
                                          filetypes = (("Nastran files",
                                                        "*.nas*"),
                                                       ("all files",
                                                        "*.*")))
	selectedfile.set(filename)
	


def browseFiles2():

	filename = filedialog.askopenfilename(title = "Select nastran File",
                                          filetypes = (("Nastran files",
                                                        "*.nas*"),
                                                       ("all files",
                                                        "*.*")))
	selectedfile2.set(filename)

def browseFiles3():

	filename = filedialog.askopenfilename(title = "Select RSP File",
                                          filetypes = (("RSP files",
                                                        "*.rsp*"),
                                                       ("all files",
                                                        "*.*")))
	selectedfile3.set(filename)

Label(master, text='Select subsystem:').grid(row=1, column=0)
#option menu for analysis type
var1 = StringVar(master)
var1.set('') #default value
l1 = OptionMenu(master, var1, 'door', 'tailgate' ,'IP')
l1.grid(row=1, column=1)

Label(master,text='Select sub-system nas file:').grid(row=2, column=0)

button_explore1 = Button(master,
                       text = "Browse",
                        command = browseFiles).grid(row=2, column=1)



e2=Entry(master, textvariable=selectedfile).grid(row=2, column=2)


Label(master,text='Select Eline nas file:').grid(row=3, column=0)
button_explore2 = Button(master,
                        text = "Browse",
                        command = browseFiles2).grid(row=3, column=1)

e3=Entry(master, textvariable=selectedfile2).grid(row=3, column=2)

Label(master,text='Path to rsp load file:').grid(row=4, column=0)
button_explore3 = Button(master,
                        text = "Browse",
                        command = browseFiles3).grid(row=4, column=1)

e4=Entry(master, textvariable=selectedfile3).grid(row=4, column=2)

Label(master,text='Specify node ids to apply enforced acc. load \n (commma separated):').grid(row=5, column=0)
content3=StringVar()
e3=Entry(master, textvariable=content3).grid(row=5, column=1)


Label(master,text='Maximum frequency? [eigen, freq_resp]:').grid(row=6,column=0)
content6=StringVar()
e6=Entry(master, textvariable=content6).grid(row=6, column=1)
content6.set('100')


Label(master,text='Specify rpc channel id as per the node id \n (3 for each node id commma separated):').grid(row=7,column=0)
content7=StringVar()
e7=Entry(master, textvariable=content7).grid(row=7, column=1)


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

subsystem = var1.get()
subsystem_file=selectedfile.get()
eline_file=selectedfile2.get()
rsp_file=selectedfile3.get()
subsystem = var1.get()
nodeset=content3.get()
maxfreq=content6.get()
rpcchannel=content7.get()

if nodeset=='':
	if subsystem == 'door':
		content3.set('1000,2000,3000,4000')
	elif subsystem == 'tailgate':
		content3.set('10,20,30,40')
	elif subsystem == 'IP':
		content3.set('100,200,300,400')

nodeset=content3.get()

if rpcchannel=='':
	if subsystem == 'door':
		content7.set('970,980,990,1000,1010,1020,1030,1040,1050,1060,1070,1080')
	elif subsystem == 'tailgate':
		content7.set('97,98,99,100,101,102,103,104,105,106,107,108')
	elif subsystem == 'IP':
		content7.set('7,8,9,10,11,12,13,14,15,16,17,18')

rpcchannel=content7.get()

#We want the entire paths stored in the variable, but only the file in the window
#Therefore, we retrieve the full path for each of the chosen material cards

#Empty input is OK, not necessary to give excitation points. 
#Otherwise, it must be comma separated values, not ex a string.

if (subsystem != ''): 
	print('Subsystem selected to analyse')
if subsystem_file.__contains__('.nas'):
	print('Nastran Subsystem file is selected')
if eline_file.__contains__('.nas'):
	print('Nastran Eline file is selected')
else:
	errorWindow('Run ended', 'Invalid input, press OK and try again', '250x100')

#frequency_value = content2.get()
#response_values = content3.get()
#spc_values = content4.get()
#direction_values = content5.get()

try:
	callback()  #Need to close ecd-window if not already cancelled
except (TclError): #If already closed, it throws an TclError for trying to close an already destroyed application
	print('') #Don't need to do anything, the application is already closed.

if subsystem != '':
	file = open('subsystem_input_values.txt', 'w')
	file.write(subsystem)
	file.write('\n')
	file.write(subsystem_file)
	file.write('\n')
	file.write(eline_file)
	file.write('\n')
	file.write(rsp_file)
	file.write('\n')
	file.write(nodeset)
	file.write('\n')
	file.write(maxfreq)
	file.write('\n')
	file.write(rpcchannel)
	file.write('\n')
	file.close()
	transient_resp_ecd_v1.main()