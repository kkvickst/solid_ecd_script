#!/usr/bin/python
import os
import sys
import getpass
import numpy as np
from time import gmtime, strftime
import rpcReadWrite_lib
from rpcReadWrite_lib import *

try:
		# for Python2
	from Tkinter import *   ## notice capitalized T in Tkinter 
except ImportError:
	# for Python3
	from tkinter import filedialog
	from tkinter import *   ## notice lowercase 't' in tkinter here

import tkinter as tk



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
	window.quit
	#window.destroy()
	sys.exit()


TEMPLATE = """$------------------------------------------------------------------$
$ Project         : {PROJECT}
$ Virtual Series  : Modell
$ Analysis Type   : transient response
$ Description     : None
$ Nastran Version : 2018
$ Run by          : {USER}
$ Date            : {DATE}
$------------------------------------------------------------------$
$                     Nastran System Cell Cards                    $
$------------------------------------------------------------------$
NASTRAN NLINES=33, BUFFSIZE=65537, SYSTEM(151)=1
NASTRAN QRMETH=5
$
$------------------------------------------------------------------$
$                      Executive Control Cards                     $
$------------------------------------------------------------------$
SOL 112
$TIME 900000 												$ KSK $
$DIAG 8
$DOMAINSOLVER,ACMS $ Need ACMS or not?
CEND
$
$------------------------------------------------------------------$
$                          Set definition                          $
$------------------------------------------------------------------$
$
$Nodes_SET_Elines                                                               
$SET 1000= 1001001 THRU 1001023,1002001 THRU 1002023,
$1003001 THRU 1003085,1004001 THRU 1004085,
$------------------------------------------------------------------$
$                      Case Control Cards                          $
$------------------------------------------------------------------$
$2345678$2345678$2345678$2345678$2345678$2345678$2345678$2345678$2345678
$
ECHO=NONE
SDAMP = 111
MAXLINES=10000000
TITLE = Transient response {FULLNAME}
$ITLE   
$
METHOD=20
  DLOAD=1000
SPC=1
NSM=1
MEFFMASS(PRINT,NOPUNCH,MEFFM) = YES
GROUNDCHECK(PRINT,SET=ALL)=YES
WEIGHTCHECK(PRINT,SET=ALL)=YES
RESVEC=(NOINRL,NOAPPLOAD,RVDOF,NODAMP,NOADJLOD,NODYNRESP)=SYSTEM

$
{SUBCASES}$
  LABEL = Modal transient analysis    
  DISPLACEMENT(PLOT)=ALL
  SPCFORCE(SORT1,PLOT)=ALL
  ACCELERATION(PLOT)=ALL

TSTEP=99
SDAMPING=2000

PARAM,POST,-2
PARAM, LFREQ, 0.5
PARAM,ENFMETH,ABS
PARAM,ENFMOTN,ABS
$------------------------------------------------------------------$
$                        Bulk Data  Cards                          $
$------------------------------------------------------------------$
BEGIN BULK
$
$----------------------------  definition -------------------------$
$
$
$---------------------------Transient Time Step--------------------------------
TSTEP,99,{timesteps},.001
$
$------------------------------------------------------------------$
{MATERIAL1}
{MATERIAL2}

$
PARAM      OGEOM      NO
PARAM     GRDPNT       0
PARAM    AUTOSPC     YES
PARAM     PRGPST      NO
PARAM   COUPMASS       1
PARAM      SNORM    20.0
PARAM     RESVEC     YES
PARAM   RESVINER      NO
PARAM      LFREQ     1.0
$
$PARAM      K6ROT     1.0
$PARAM       POST      -2
$PARAM   MAXRATIO  1.0E+7
$PARAM      EPPRT  1.0E-8
$
EIGRL         10           {eigenF}
$
$ DLOAD TLOAD SPCD
{DLOAD}{TLOAD1}{SPCD}{TABLRPC}{MATERIAL3}$
$
$ Structural Modal Damping (loss factor, G)
TABDMP1      111    CRIT
$     1+    FREQ    DAMP    FREQ    DAMP    FREQ    DAMP    FREQ    DAMP     10+
,0.0,0.03,12.0,0.03,15.0,0.15,1000.0,0.15
,ENDT
"""

SETS_TEMP = """SET {GRID} = {GRID}
"""
SUBCASE_TEMP = """SUBCASE {GRID}1
SUBTITLE={GRID} X
LABEL={GRID} X
DLOAD={GRID}1
DISP(PUNCH,SORT2,REAL)={GRID}
$
SUBCASE {GRID}2
SUBTITLE={GRID} Y
LABEL={GRID} Y
DLOAD={GRID}2
DISP(PUNCH,SORT2,REAL)={GRID}
$
SUBCASE {GRID}3
SUBTITLE={GRID} Z
LABEL={GRID} Z
DLOAD={GRID}3
DISP(PUNCH,SORT2,REAL)={GRID}
$
"""
DLOAD_TEMP = """DLOAD   {GRID7}1     1.0     1.0{GRID6}10
DLOAD   {GRID7}2     1.0     1.0{GRID6}20
DLOAD   {GRID7}3     1.0     1.0{GRID6}30
$
"""
TLOAD1_TEMP = """TLOAD1,{GRID6}1,{GRID6}1,,3,{GRID6}1
TLOAD1,{GRID6}2,{GRID6}2,,3,{GRID6}2
TLOAD1,{GRID6}3,{GRID6}3,,3,{GRID6}3
$
"""
SPCD_TEMP = """SPCD,{GRID6}1,{GRID6},1,1.0
SPCD,{GRID6}2,{GRID6},2,1.0
SPCD,{GRID6}3,{GRID6},3,1.0
$
""" 

TABLRPC_TEMP = """TABLRPC,{GRID6}1,LINEAR,LINEAR,1000,RPC,{channel[0]}
TABLRPC,{GRID6}2,LINEAR,LINEAR,1000,RPC,{channel[1]}
TABLRPC,{GRID6}3,LINEAR,LINEAR,1000,RPC,{channel[2]}
$
""" 

# DAREA_TEMP = """DAREA   {GRID6}1030079940       1     1.0

filename = 'subsystem_input_values.txt'
def get_values(file_path):
	nodebcacc = set()
	#subsystem_nas=''
	#spcs = set()
	with open(filename,'r') as ins:
		list = []
		for line in ins:
			list.append(line.strip().split(','))
	
	
	subsystem=list[0]
	subsystem_nas=list[1]
	subsystem_eline=list[2]
	subsystem_rsp=list[3]
	subsystem_loadid=np.array(list[4])
	subsystem_maxfreq=list[5]
	rpcchannel=list[6]
	#rsppath=str(subsystem_rsp)
	rsppath=str(subsystem_rsp).split('/')
	x, dt, names, units, scales = readsrpc(rsppath[7][0:-2],channels=[2])
	timesteps=(len(x))

	#print(x)
	return (subsystem, subsystem_nas, subsystem_eline, subsystem_rsp, subsystem_loadid, subsystem_maxfreq,rpcchannel,timesteps)


#Breaks up string in order to have the right width for the ecd file (68 chars)
def string_formatter(string):
	length = len(string)
	lineWidth = 68 #Width of the .ecd files
	n = lineWidth - 9 #9 since that is the number of characters in "INCLUDE '"
	formattedString = string[0: n]
	while (length > n): #split file path into rows while the string is too long
		formattedString = formattedString + '\n' + string[n: n + lineWidth]
		n = n + lineWidth
	return formattedString

def add_include(materialCard): #adds "INCLUDE" for the chosen material cards
	if materialCard != '':
		materialCard = "INCLUDE " + str(materialCard[1:-1])
	return materialCard

def add_include_rps(materialCard): #adds "INCLUDE" for the chosen material cards
	if materialCard != '':
		materialCard = "UDNAME    1000\n" +"        "+str(materialCard[1:-1])+"\n"
	return materialCard


def generate_output(subsystem, subsystem_nas, subsystem_eline, subsystem_rsp, subsystem_loadid, subsystem_maxfreq,nasFile,rspchannel,timesteps):
	sets_output = ''
	subcase_output = ''
	dload_output = ''
	tload1_output = ''
	spcd_output = ''
	tablrpc_output = ''
	icounter=0
	subsystem_maxfreq=str(subsystem_maxfreq[0])

	for rsp in subsystem_rsp:
		for grid in subsystem_loadid:
			if icounter==0:
				icounter+=1
				dload_output+="DLOAD,"+str(icounter*1000)+",1.0,1.0,"+grid+"1"+",1.0,"+grid+"2"+",1.0,"+grid+"3\n"
			else:
				dload_output+="        1.0,"+grid+"1"+",1.0,"+grid+"2"+",1.0,"+grid+"3\n"
		icounter=0

	icounter=0

	for rsp in subsystem_rsp:
		icounter+=1
		for grid in subsystem_loadid:
			sets_output += SETS_TEMP.format(GRID = grid)
			#subcase_output += SUBCASE_TEMP.format(GRID = grid)
			tload1_output += TLOAD1_TEMP.format(GRID6 = grid)
			spcd_output += SPCD_TEMP.format(GRID6 = grid)
			icounter=0
				
	icounter=0
	
	ilooprpc=len(rspchannel)/3
	
	rsppernode=np.array_split(rspchannel,ilooprpc)

	for grid in subsystem_loadid:
		tablrpc_output += TABLRPC_TEMP.format(GRID6 = grid,channel=rsppernode[icounter])
		icounter+=1
	
	user = getpass.getuser()
	date = strftime("%Y-%m-%d %H:%M:%S", gmtime())
	project = str(subsystem_nas).split('/')[-1].split('_')[0]
	fileName = str(subsystem_nas).split('.')[0].split('/')[-1] #gets filename by removing the .nas and the directory
	filePath = string_formatter(subsystem_nas) #makes full directory ecd compatible
	nasPath = add_include(string_formatter(str(subsystem_nas))) #makes string ecd compatible and adds INCLUDE
	elinePath = add_include(string_formatter(str(subsystem_eline))) #makes string ecd compatible and adds INCLUDE
	rspPath = add_include_rps(string_formatter(str(subsystem_rsp))) #makes string ecd compatible and adds INCLUDE

	return TEMPLATE.format(SPC = subsystem_loadid,
						SETS = sets_output,
						SUBCASES = subcase_output,
						DLOAD = dload_output,
						TLOAD1 = tload1_output,
						SPCD = spcd_output,
						TABLRPC = tablrpc_output,
						DATE = date,
						USER = user,
						PROJECT = project,
						FULLNAME = fileName,
						INPUTFILE = filePath,
						MATERIAL1 = nasPath,
						MATERIAL2 = elinePath,
						MATERIAL3 = rspPath,
						eigenF = subsystem_maxfreq,
						timesteps=timesteps)


def main(): 
	with open(filename,'r') as ins:
		list = []
		for line in ins:
			list.append(line.strip().split(','))
	nasFile = list[1][0] # fetch subsystem nas file name
	nasFile1 = nasFile.split('/')[-1]
	ecdFile = 'transient_resp_' + nasFile1.split('.')[0] + '.ecd' # ecd file name
		
	(subsystem, subsystem_nas, subsystem_eline, subsyste_rsp, subsystem_loadid, subsystem_maxfreq,rpcchannel,timesteps) = get_values(nasFile)

	if len(rpcchannel)/3!=len(subsystem_loadid):
		errorWindow('Run ended', 'Invalid input, Each node should have 3 channels, redefine node ids and channel ids and try again', '700x100')	

	output = generate_output(subsystem, subsystem_nas, subsystem_eline, subsyste_rsp, subsystem_loadid, subsystem_maxfreq,nasFile,rpcchannel,timesteps)

	with open(ecdFile, 'w') as output_file:
		output_file.write(output)
	if os.path.isfile(ecdFile):
		print ('Ecd file created successfully!')
	else:
		print ('File not created.')

if __name__ == '__main__':
  main()

