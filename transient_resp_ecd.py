#!/usr/bin/python
import os
import sys
import getpass
from time import gmtime, strftime

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
$
ECHO=NONE
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

TSTEP         99    2000    .001
$
$------------------------------------------------------------------$
INCLUDE '{INPUTFILE}'
{MATERIAL1}
{MATERIAL2}
{MATERIAL3}
$
PARAM      OGEOM     YES
PARAM     GRDPNT       0
PARAM    AUTOSPC     YES
PARAM     PRGPST      NO
PARAM   COUPMASS       1
PARAM      SNORM    20.0
PARAM     RESVEC      NO
PARAM   RESVINER      NO

$
$PARAM      K6ROT     1.0
$PARAM       POST      -2
$PARAM   MAXRATIO  1.0E+7
$PARAM      EPPRT  1.0E-8
$
$
FREQ          10{FREQ}
$
$
{DLOAD}$
{RLOAD}$
{DAREA}$
TABLED1       11
             0.0     1.0  2000.0     1.0    ENDT
TABLED1       12
             0.0     0.0  2000.0     0.0    ENDT
$
$ Structural Modal Damping (loss factor, G)
TABDMP1      200
             0.0    0.08  2000.0    0.08    ENDT
ENDDATA
"""
SUBCASE_TEMP = """SUBCASE {GRID}{GRID9}
SUBTITLE={GRID} {n}
LABEL={GRID} {n}
DLOAD={GRID}{GRID9}
DISP(PLOT)=ALL
$
"""
DLOAD_TEMP = """DLOAD   {GRID7}{GRID9}     1.0     1.0{GRID6}{GRID9}0
"""
RLOAD_TEMP = """RLOAD1  {GRID6}{GRID9}0{GRID6}{GRID9}0                      11      12
"""
DAREA_TEMP = """DAREA   {GRID6}{GRID9}0{GRID8}       {GRID9}     1.0
"""

filename = 'subsystem_input_values.txt'
def get_values(file_path):
	nodebcacc = set()
	#spcs = set()
	with open(filename,'r') as ins:
		list = []
		for line in ins:
			list.append(line.strip().split(','))
	
	subsystem=list[0]
	subsystem_nas=list[1]
	subsystem_eline=list[2]
	subsyste_rsp=list[3]
	subsystem_loadid=list[4]
	subsystem_maxfreq=list[5]
	#grid_values_in = list[4]
	return (subsystem, subsystem_nas, subsystem_eline, subsyste_rsp, subsystem_loadid, subsystem_maxfreq)


""" 	direction_values_in = list[3][0]
	with open(file_path, 'r') as file:
		for line in file:
			values = line.split()      
			if len(values) > 0 and (values[0] == 'GRID' or values[0] == 'GRID*'):
				grids.add(values[1])
			if len(values) > 0 and (values[0] == 'SPC' or values[0] == 'SPC*'):
				spcs.add(values[1])
	# grid_values = raw_input('Specify the excitation points? ').split()
	grid_values = grid_values_in.split()
	direction_values = direction_values_in.split()
	for grid in grid_values:
		if grid not in grids:
			print ('Invalid grid ID: %s'%(grid))
			sys.exit()
	spc_string = "$"
	# spc_response = raw_input('Do you want to enter an SPC value [y/n]? ')
	if list[4][0] != '':
		spc_values_in = list[4][0]
	# if spc_response == 'y':
		# spc_values = raw_input('What is the SPC ID? ').split()
		spc_values = spc_values_in.split()
		if len(spc_values) != 1:
			print ('Need exactly one SPC value.')
			sys.exit()
		for spc in spc_values:
			if spc not in spcs:
				print ('Invalid SPC value: %s'%(spc))
				sys.exit()
		spc_string = "SPC=" + spc_values[0]
 """
	

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

def add_include(path): #adds "INCLUDE" for the chosen material cards
	if path != '':
		path = "INCLUDE '" + str(path) + "'"
	return path

def generate_output(subsystem, subsystem_nas, subsystem_eline, subsystem_rsp, subsystem_loadid, subsystem_maxfreq,nasFile):
	user = getpass.getuser()
	date = strftime("%Y-%m-%d %H:%M:%S", gmtime())
	project = str(subsystem_nas).split('/')[-1].split('_')[0]
	fileName = str(subsystem_nas).split('.')[0].split('/')[-1] #gets filename by removing the .nas and the directory
	filePath = string_formatter(subsystem_nas) #makes full directory ecd compatible
	nasPath = add_include(string_formatter(subsystem_nas)) #makes string ecd compatible and adds INCLUDE
	elinePath = add_include(string_formatter(subsystem_eline)) #makes string ecd compatible and adds INCLUDE
	rspPath = add_include(string_formatter(subsystem_rsp)) #makes string ecd compatible and adds INCLUDE
	subcase_output = ''
	dload_output = ''
	rload_output = ''
	darea_output = ''
	real_frequency_value = str(subsystem_maxfreq) + ".0"
	orientation = ['x', 'y', 'z']
	for grid in subsystem_loadid:
		for direction in subsystem_loadid:
			subcase_output += SUBCASE_TEMP.format(GRID = grid, GRID9 = direction, n=orientation[int(direction)-1])
			dload_output += DLOAD_TEMP.format(GRID7 = grid.rjust(7), GRID6 = grid.rjust(6), GRID9 = direction)
			rload_output += RLOAD_TEMP.format(GRID6 = grid.rjust(6), GRID9 = direction)
			darea_output += DAREA_TEMP.format(GRID6 = grid.rjust(6), GRID8 = grid.rjust(8), GRID9 = direction)
	user = getpass.getuser()
	date = strftime("%Y-%m-%d %H:%M:%S", gmtime())
	return TEMPLATE.format(SPC = spc_value,
						SUBCASES = subcase_output,
						DLOAD = dload_output,
						RLOAD = rload_output,
						DAREA = darea_output,
						FREQ = real_frequency_value.rjust(8),
						DATE = date,
						USER = user,
						PROJECT = project,
						FULLNAME = fileName, 
						INPUTFILE = filePath,
						MATERIAL1 = materialPath1,
						MATERIAL2 = materialPath2,
						MATERIAL3 = materialPath3)



def generate_output(subsystem, subsystem_nas, subsystem_eline, subsystem_rsp, subsystem_loadid, subsystem_maxfreq,nasFile):
	sets_output = ''
	subcase_output = ''
	dload_output = ''
	rload_output = ''
	darea_output = ''
	for grid in grid_values:
		sets_output += SETS_TEMP.format(GRID = grid)
		subcase_output += SUBCASE_TEMP.format(GRID = grid)
		dload_output += DLOAD_TEMP.format(GRID7 = grid.rjust(7), GRID6 = grid.rjust(6))
		rload_output += RLOAD_TEMP.format(GRID6 = grid.rjust(6))
		darea_output += DAREA_TEMP.format(GRID6 = grid.rjust(6), GRID8 = grid.rjust(8))
	user = getpass.getuser()
	date = strftime("%Y-%m-%d %H:%M:%S", gmtime())
	project = str(subsystem_nas).split('/')[-1].split('_')[0]
	fileName = str(subsystem_nas).split('.')[0].split('/')[-1] #gets filename by removing the .nas and the directory
	filePath = string_formatter(subsystem_nas) #makes full directory ecd compatible
	nasPath = add_include(string_formatter(subsystem_nas)) #makes string ecd compatible and adds INCLUDE
	elinePath = add_include(string_formatter(subsystem_eline)) #makes string ecd compatible and adds INCLUDE
	rspPath = add_include(string_formatter(subsystem_rsp)) #makes string ecd compatible and adds INCLUDE
	return TEMPLATE.format(SPC = spc_value,
						SETS = sets_output,
						SUBCASES = subcase_output,
						DLOAD = dload_output,
						RLOAD = rload_output,
						DAREA = darea_output,
						DATE = date,
						USER = user,
						PROJECT = project,
						FULLNAME = fileName,
						INPUTFILE = filePath,
						MATERIAL1 = materialPath1,
						 MATERIAL2 = materialPath2,
						 MATERIAL3 = materialPath3)



def main(): 
	with open(filename,'r') as ins:
		list = []
		for line in ins:
			list.append(line.strip().split(','))
	nasFile = list[1][0] # fetch subsystem nas file name
	nasFile1 = nasFile.split('/')[-1]
	ecdFile = 'transient_resp_' + nasFile1.split('.')[0] + '.ecd' # ecd file name
	#frequency_value = list[1][0]
	# nasFile = raw_input('Which .nas file? ')
	# ecdFile = raw_input('Name the .ecd file? ')
	# (grid_values, direction_values, spc_value, material1, material2, material3) = get_values(nasFile)
	
	(subsystem, subsystem_nas, subsystem_eline, subsyste_rsp, subsystem_loadid, subsystem_maxfreq) = get_values(nasFile)

	output = generate_output(subsystem, subsystem_nas, subsystem_eline, subsyste_rsp, subsystem_loadid, subsystem_maxfreq,nasFile)

	with open(ecdFile, 'w') as output_file:
		output_file.write(output)
	if os.path.isfile(ecdFile):
		print ('Ecd file created successfully!')
	else:
		print ('File not created.')

if __name__ == '__main__':
  main()
