#!/usr/bin/python
import os
import sys
import getpass
from time import gmtime, strftime

TEMPLATE = """$------------------------------------------------------------------$
$ Project         : {PROJECT}
$ Virtual Series  : Modell
$ Analysis Type   : frequency response
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
SOL 108
TIME 900000
DIAG 5,8,12
CEND
$------------------------------------------------------------------$
$                      Case Control Cards                          $
$------------------------------------------------------------------$
$
ECHO=NONE
MAXLINES=10000000
TITLE = Direct frequency response {FULLNAME}
$ITLE   
$
FREQ=10
{SPC}
$
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

filename = 'input_values.txt'
def get_values(file_path):
	grids = set()
	spcs = set()
	with open(filename,'r') as ins:
		list = []
		for line in ins:
			list.append(line.strip().split(','))
	grid_values_in = list[2][0]
	direction_values_in = list[3][0]
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
	#Since input_values.txt has a row for each input, even if no card is chosen
	#for material1 or material2, they will have value '', which is fine.
	#For material3, however, it will give an index out of bounds exception if it is not 
	#assigned a value. Therefore, need an if-statement to check if there is a third material card.
	material1 = list[5][0]
	material2 = list[6][0]
	material3 = ''
	if len(list) > 7:
		material3 = list[7][0]
	return (grid_values, direction_values, spc_string, material1, material2, material3)

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

def generate_output(grid_values,spc_value,nasFile,frequency_value,direction_values,material1,material2,material3):
	user = getpass.getuser()
	date = strftime("%Y-%m-%d %H:%M:%S", gmtime())
	project = nasFile.split('/')[-1].split('_')[0]
	fileName = nasFile.split('.')[0].split('/')[-1] #gets filename by removing the .nas and the directory
	filePath = string_formatter(nasFile) #makes full directory ecd compatible
	materialPath1 = add_include(string_formatter(material1)) #makes string ecd compatible and adds INCLUDE
	materialPath2 = add_include(string_formatter(material2)) #makes string ecd compatible and adds INCLUDE
	materialPath3 = add_include(string_formatter(material3)) #makes string ecd compatible and adds INCLUDE
	subcase_output = ''
	dload_output = ''
	rload_output = ''
	darea_output = ''
	real_frequency_value = frequency_value + ".0"
	orientation = ['x', 'y', 'z']
	for grid in grid_values:
		for direction in direction_values:
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

def main(): 
	with open(filename,'r') as ins:
		list = []
		for line in ins:
			list.append(line.strip().split(','))
	nasFile = list[0][0]
	nasFile1 = nasFile.split('/')[-1]
	ecdFile = 'freq_resp_' + nasFile1.split('.')[0] + '.ecd'
	frequency_value = list[1][0]
	# nasFile = raw_input('Which .nas file? ')
	# ecdFile = raw_input('Name the .ecd file? ')
	(grid_values, direction_values, spc_value, material1, material2, material3) = get_values(nasFile)
	output = generate_output(grid_values,spc_value,nasFile,frequency_value,direction_values,material1,material2,material3)
	with open(ecdFile, 'w') as output_file:
		output_file.write(output)
	if os.path.isfile(ecdFile):
		print ('Ecd file created successfully!')
	else:
		print ('File not created.')

if __name__ == '__main__':
  main()

