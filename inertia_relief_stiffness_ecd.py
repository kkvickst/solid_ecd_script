#!/usr/bin/python
import os
import sys
import getpass
from time import gmtime, strftime

TEMPLATE = """$------------------------------------------------------------------$
$ Project         : {PROJECT}
$ Virtual Series  : Model
$ Analysis Type   : Inertial Relief Stiffness 
$ Description     : None
$ Nastran Version : 2019.1
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
SOL 101
TIME 900000
DIAG 5,8,12
CEND
$------------------------------------------------------------------$
$                      Case Control Cards                          $
$------------------------------------------------------------------$
$
ECHO=NONE
MAXLINES=10000000
TITLE = Inertial-Stiffness {FULLNAME}
$   
$
{SPC}
$
{SETS}$
{SUBCASES}$
$------------------------------------------------------------------$
$                        Bulk Data  Cards                          $
$------------------------------------------------------------------$
BEGIN BULK
$
$------------------------------------------------------------------$
INCLUDE '{INPUTFILE}'
{MATERIAL1}
{MATERIAL2}
{MATERIAL3}
$
PARAM      OGEOM      NO
PARAM     GRDPNT       0
PARAM    AUTOSPC     YES
PARAM     PRGPST      NO
PARAM   COUPMASS       1
PARAM      SNORM    20.0
PARAM     RESVEC     YES
PARAM   RESVINER      NO
$PARAM      LFREQ     1.0
PARAM, INREL , -2
PARAM, POST , -1
$
$PARAM      K6ROT     1.0
$PARAM       POST      -2
$PARAM   MAXRATIO  1.0E+7
$PARAM      EPPRT  1.0E-8
$
$
$
{FORCE}
ENDDATA
"""

SETS_TEMP = """SET {GRID} = {GRID}
"""
SUBCASE_TEMP = """SUBCASE {GRID}1
SUBTITLE={GRID} X
LABEL={GRID} X
LOAD={GRID}1
DISP(PUNCH,SORT2,REAL)={GRID}
$
SUBCASE {GRID}2
SUBTITLE={GRID} Y
LABEL={GRID} Y
LOAD={GRID}2
DISP(PUNCH,SORT2,REAL)={GRID}
$
SUBCASE {GRID}3
SUBTITLE={GRID} Z
LABEL={GRID} Z
LOAD={GRID}3
DISP(PUNCH,SORT2,REAL)={GRID}
$
"""
FORCE_TEMP = """FORCE {GRID9}1 {GRID7}              1.      1.      0.      0.
FORCE {GRID9}2 {GRID7}              1.      0.      1.      0.
FORCE {GRID9}3 {GRID7}              1.      0.      0.      1.
$
"""

filename = 'input_values.txt'
def get_values(file_path):
	grids = set()
	spcs = set()
	with open(filename,'r') as ins:
		list = []
		for line in ins:
			list.append(line.strip().split(','))
	grid_values_in = list[1][0]
	with open(file_path, 'r') as file:
		for line in file:
			values = line.split()      
			if len(values) > 0 and (values[0] == 'GRID' or values[0] == 'GRID*'):
				grids.add(values[1])
			if len(values) > 0 and (values[0] == 'SPC' or values[0] == 'SPC*'):
				spcs.add(values[1])
	# grid_values = raw_input('Specify the excitation points? ').split()
	grid_values = grid_values_in.split()
	for grid in grid_values:
		if grid not in grids:
			print ('Invalid grid ID: %s'%(grid))
			sys.exit()
	spc_string = "$"
	# spc_response = raw_input('Do you want to enter an SPC value [y/n]? ')
	if list[2][0] != '':
		spc_values_in = list[2][0]
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
	#Since input_values.txt has a row for each input, even if no card is chosen
	#for material1 or material2, they will have value '', which is fine.
	#For material3, however, it will give an index out of bounds exception if it is not 
	#assigned a value. Therefore, need an if-statement to check if there is a third material card.
	material1 = list[3][0]
	material2 = list[4][0]
	material3 = ''
	if len(list) > 5:
		material3 = list[5][0]
	return (grid_values, spc_string, material1, material2, material3)

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
		materialCard = "INCLUDE '" + materialCard + "'"
	return materialCard

def generate_output(grid_values, spc_value,nasFile, material1, material2, material3):
	sets_output = ''
	subcase_output = ''
	force_output = ''
	for grid in grid_values:
		sets_output += SETS_TEMP.format(GRID = grid)
		subcase_output += SUBCASE_TEMP.format(GRID = grid)
		force_output += FORCE_TEMP.format(GRID9 = grid.rjust(9), GRID7 = grid.rjust(7))
	user = getpass.getuser()
	date = strftime("%Y-%m-%d %H:%M:%S", gmtime())
	project = nasFile.split('/')[-1].split('_')[0]
	fileName = nasFile.split('.')[0].split('/')[-1] #gets filename by removing the .nas and the directory
	filePath = string_formatter(nasFile) #makes full directory ecd compatible
	materialPath1 = add_include(string_formatter(material1)) #makes string ecd compatible and adds INCLUDE
	materialPath2 = add_include(string_formatter(material2)) #makes string ecd compatible and adds INCLUDE
	materialPath3 = add_include(string_formatter(material3)) #makes string ecd compatible and adds INCLUDE
	return TEMPLATE.format(SPC = spc_value,
						SETS = sets_output,
						SUBCASES = subcase_output,
						FORCE = force_output,
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
	nasFile = list[0][0]
	nasFile1 = nasFile.split('/')[-1]
	ecdFile = 'inertial_stiffness_' + nasFile1.split('.')[0] + '.ecd'
	# nasFile = raw_input('Which .nas file? ')
	# ecdFile = raw_input('Name the .ecd file? ')
	(grid_values, spc_value, material1, material2, material3) = get_values(nasFile)
	output = generate_output(grid_values, spc_value, nasFile, material1, material2, material3)
	with open(ecdFile, 'w') as output_file:
		output_file.write(output)
	if os.path.isfile(ecdFile):
		print ('Ecd file created successfully!')
	else:
		print ('File not created.')

if __name__ == '__main__':
  main()

