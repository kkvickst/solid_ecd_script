#!/vcc/ans/app/startup/vccpython3
import array
from collections import OrderedDict
from datetime import datetime
import numpy as np
import os

def rpcheader(filename):    
    ##############################################################################
    #
    # Function to read the header of a RPC III time history file  .
    #
    # Full syntax:
    # dic, rpcFile = rpcheader(filename)
    #
    #   where,
    #      dic      : Output variable.
    #                 Dictionary with RPC III files header.
    #                 Type: dict
    #
    #      rpcFile  : Output variable.
    #                 Opened binary file.
    #                 Type: class BufferedReader
    #
    #      filename : Input variable (required).
    #                 A string containing the rpc file name.
    #                 The file extension must be included.
    #                 Type: str
    #
    # 
    # Created on 2020-08-17
    # @author: Britta Kallman, bkallman
    ##############################################################################
    
    # Check that RPC III file exist
    if not os.path.isfile(filename):
        raise SystemExit('RPC File ' + filename + " not found.")
    
    # Open RPC file
    rpcFile = open(filename,'rb')
    
    # Reads first part of HEADER
    r0 = rpcFile.read(512)
    
    # Handling first part of header
    num =  int(len(r0)/128)
    dic    = {}
    for i in range(num):
        s = i*128
        e = s + 32
        key = r0[s:e].decode('utf-8')
        key = key.replace('\x00','')
        if key != '': 
            v = e+96
            value = r0[e:v].decode('utf-8')
            value = value.replace('\x00','')
            dic[key] = value
    
    # Check how long whole header is
    numHeader = int(dic['NUM_HEADER_BLOCKS'])
    
    # Reads rest of header
    r = rpcFile.read(512*(numHeader-1))
    
    # Handles rest of header
    num = int(len(r)/128)
    for i in range(num):
        s = i*128
        e = s + 32
        key = r[s:e].decode('utf-8')
        key = key.replace('\x00','')
        if key != '' : 
            v = e+96
            value = r[e:v].decode('utf-8')
            value = value.replace('\x00','')
            dic[key] = value
    
    return dic, rpcFile

def rpcchannels(filename):
    ##############################################################################
    #
    # Function to read the channels of a RPC III time history file .
    #
    # Full syntax:
    # channels = rpcchannels(filename)
    #
    #   where,
    #      channels : Output variable (required).
    #                 List with channel names.
    #                 Type: list
    #
    #      filename : Input variable (required).
    #                 A string containing the rpc file name.
    #                 The file extension must be included.
    #                 Type: str
    #
    # 
    # Created on 2020-08-17
    # @author: Britta Kallman, bkallman
    ##############################################################################
    
    # Read header
    dic, _ = rpcheader(filename)
    
    # Info from header
    NumChan = int(dic['CHANNELS'])
    channels = [dic['DESC.CHAN_%d' % no].strip() for no in range(1,NumChan+1)]

    return channels

def rpcunits(filename):
    ##############################################################################
    #
    # Function to read the units for channels of a RPC III time history file .
    #
    # Full syntax:
    # units = rpcunits(filename)
    #
    #   where,
    #      units    : Output variable (required).
    #                 List with units.
    #                 Type: list
    #
    #      filename : Input variable (required).
    #                 A string containing the rpc file name.
    #                 The file extension must be included.
    #                 Type: str
    #
    # 
    # Created on 2020-08-17
    # @author: Britta Kallman, bkallman
    ##############################################################################
    
    # Read header
    dic, _ = rpcheader(filename)
    
    # Info from header
    NumChan = int(dic['CHANNELS'])
    channels = [dic['UNITS.CHAN_%d' % no] for no in range(1,NumChan+1)]

    return channels

def readsrpc(filename, channels = [], t0 = 0, tend = None, method = 'time'):
    ##############################################################################
    #
    # Function to read RPC III time history from RPC III format binary files. 
    #
    # Full syntax:
    # x, dt, names, units, scales = readsrpc(filename, channels, t0, tend, method)
    #
    #   The left hand side need to take all output data into account such as:
    #      x, dt, names, units, scales =
    #   But if some variables not are wanted they can be replaced by '_':
    #      x, _, names, units, scales =
    #      x, dt, _, units, _ =
    #   If only first variable/variables is wanted, rest of output can be replaced by '*_':
    #      x, *_ =
    #      x, dt, names, *_ =
    #
    #   The right hand side need to include filename, rest variables are optional, ex:
    #      readsrpc(filename)
    #      readsrpc(filename, channels, t0, tend)
    #   If the variables not are inputed in order use 'variablename = ' before you input:
    #      readsrpc(filename, t0 = 2)
    #      readsrpc(filename, channels, tend = 300, method = 'point')
    #
    #   where,
    #      x        : Output variable (required).  
    #                 Name of an numpy array where you want the time history 
    #                 to be stored. There will be one column per channel.
    #                 Type: numpy array (numpy.ndarray)
    #
    #      dt       : Output variable (optional).
    #                 The delta_t of the time history data.
    #                 Type: float
    #
    #      names    : Output variable (optional).
    #                 List with channel names.
    #                 Type: list
    #
    #      units    : Output variable (optional).
    #                 List with channel units.
    #                 Type: list
    #                    
    #      scales   : Output variable (optional)
    #                 Numpy array where the scale factors from the rpc file 
    #                 header is stored.
    #                 Type: numpy array (numpy.ndarray)
    #
    #      filename : Input variable (required).
    #                 A string containing the rpc file name.
    #                 The file extension must be included.
    #                 Type: str
    #
    #      channels : Input variable (optional). 
    #                 A one dimensional array containing the list of channel
    #                 numbers for which the time histories are to be extracted.
    #                 If omitted, or null, defaults to all the channles in the
    #                 file.
    #                 Type: list of integers OR numpy array  (numpy.ndarray)
    #                 
    #      t0       : Input variable (optional). 
    #                 if method = 'time' (default) then t0 denote the start times 
    #                 for extracting data.
    #                 if method = 'point' then t0 denote the starting point for 
    #                 extracting data.
    #                 If t0 are omitted, the time history is extracted from beginning.
    #                 Type: int OR float
    #
    #      tend     : Input variable (optional). 
    #                 if method = 'time' (default) then tend denote the end times 
    #                 for extracting data.
    #                 if method = 'point' then tend denote the ending point for 
    #                 extracting data.
    #                 If tend are omitted, the time history is extracted to the end.
    #                 Type: int OR float
    #
    #      method   : Input variable (optional).
    #                 Input should be 'time' (default) or 'point'.
    #                 if method = 'time' then t0 and tend denote the start and 
    #                 end times for extracting data. 
    #                 if method = 'point' then t0 and tend denote the starting
    #                 point and end point for extracting data.
    #                 Type: str
    #
    #   Examples:
    #      Load all the channels and the entire duration of time history in
    #      file phh_pass1.rsp
    #         import readsrpc_lib as rr
    #         x, *_ = rr.readsrpc('phh_pass1.rsp')
    #      or,
    #         from readsrpc_lib import readsrpc
    #         file = 'phh_pass1.rsp'
    #         x, *_ = readsrpc(file)
    #
    #      Load channels 1, 2 and 5, data up tp 3.5 seconds. 
    #      Also obtain delta_t and the names of the three channels.
    #         from readsrpc_lib import readsrpc
    #         p, dt, names, *_ = readsrpc('phh_pass1.rsp', [1, 2, 5], tend = 3.5, method = 'time')
    #      or,
    #         from readsrpc_lib import readsrpc
    #         channels = [1, 2, 5]
    #         p, dt, names, *_ = readsrpc('phh_pass1.rsp', channels, tend = 3.5)
    #
    #      Load the above channels with starting point 1 and ending point 1024.
    #      Retrive data (here p), channel names and units
    #         from readsrpc_lib import readsrpc
    #         p, _, names, units, _ = readsrpc('phh_pass1.rsp', channels, 1, 1024, 'point')
    #      or, 
    #         from readsrpc_lib import readsrpc
    #         p, _, names, units, _ = readsrpc('phh_pass1.rsp', channels, t0 = 1, tend = 1024, method = 'point')
    #
    # 
    # Created on 2020-08-14
    # @author: Britta Kallman, bkallman
    #
    # update log:
    # kcarls19 20210503 - Added more checks on file format 
    ##############################################################################
    
    # Check that method input is correct
    if not isinstance(method,str):
        raise SystemExit("METHOD must be one of the strings: 'time','point'.")
    elif not (method == 'time' or method == 'point'):
        raise SystemExit("METHOD must be one of the strings: 'time','point'.")
    # Check that RPC III file exist
    if not os.path.isfile(filename):
        raise SystemExit('RPC File ' + filename + " not found.")
    # Check that t0, tend is of correct type
    if not isinstance(t0,(int,float)):
        raise SystemExit('t0 must be of type integer or float.')
    if not (isinstance(tend,(int,float)) or tend is None):
        raise SystemExit('tend must be of type integer or float.')
    
    import numpy as np
    
    # Read header
    dic, rpcFile = rpcheader(filename)
    
    # Control that the file is the right format
    if not dic['FORMAT'][:6] == 'BINARY':
         raise Exception('ERROR: File format error. ',filename,' is not BINARY.')

    if "FILE_TYPE" in dic:
        if not dic['FILE_TYPE'] == 'TIME_HISTORY':
            raise Exception('ERROR: File format error. ',filename,' is not TIME_HISTORY.')
    else:
        # Assuming TIME_HISTORY as default (Adams will sometimes write rpc without FILE_TYPE )
        pass

    if "DATA_TYPE" in dic:
        if not dic['DATA_TYPE'] == 'SHORT_INTEGER':
            raise Exception('ERROR: File format error. ',filename,' is not SHORT_INTEGER.')
    else:
        # Assuming SHORT_INTEGER as default (Adams will write rpc without DATA_TYPE in SHORT_INTEGER)
        pass

    # Info from header
    NumChan = int(dic['CHANNELS'])
    NumFrame = int(dic['FRAMES'])
    GroupSize = int(dic['PTS_PER_GROUP'])
    FrameSize = int(dic['PTS_PER_FRAME'])
    HalfFrame = int(dic['HALF_FRAMES'])
    dt = float(dic['DELTA_T'])
    
    # Retrieve channel descriptions, units and scales
    names = [dic['DESC.CHAN_%d' % no] for no in range(1,NumChan+1)]
    units = [dic['UNITS.CHAN_%d' % no] for no in range(1,NumChan+1)]
    scales = np.array([float(dic['SCALE.CHAN_%d' % no]) for no in range(1,NumChan+1)])
    
    # Frames and Time in RPC-file
    NumFrame = NumFrame + HalfFrame
#    NumberOfFramesPerGroup = GroupSize/FrameSize
#    NumberOfGroups = int(np.ceil(float(NumFrame)/float(NumberOfFramesPerGroup)))
    TotalNumOfPoints = NumFrame*FrameSize
    Duration = (TotalNumOfPoints-1)*dt
    TimePerGroup = (GroupSize-1)*dt
    
    # If End time (or point) is not specified it is as default set to end of file
    if tend == None:
        tend = Duration
    
    # If no channels are specified - read all
    if not channels:
        channels = np.array([i for i in range(1,NumChan+1)])
    # Convert channels variable to numpy array if it is a list
    elif isinstance(channels,list):
        channels = np.array(channels)
    # Make sure the requested channel numbers do not exceed what is available. 
    if min(channels) < 1:
        raise Exception('Channel Numbers should be >= 1')
    elif max(channels) > NumChan:
        raise Exception('Channel Numbers should be <=  %d \nTry with different channel numbers' % (NumChan))
    
    # Channel names, units and scales only for channels that are of interest
    names = [names[i-1] for i in channels]
    units = [units[i-1] for i in channels]
    scales = scales[channels-1]
    
    # Sorted index for channels
    indSorted = np.argsort(channels)
    
    # Control that t0 and tend is float or integer
    if (not isinstance(t0,(float,int))) or (not isinstance(tend,(float,int))):
        raise Exception('t0 and tend should be scalar numbers')
    # Control that tend is larger than t0
    if tend < t0:
        raise Exception('End (tend) < Start (t0)')
    
    # Groups and Points to read depending on t0, tend and method
    if method == 'time':
        StartingGroup = int(np.floor(t0/TimePerGroup))+1
        StartingPoint = int(np.ceil(t0/dt))+1
        EndingGroup = int(np.ceil(tend/TimePerGroup))
        EndingPoint = int(round(tend/dt))+1
        NumOfPointsReq = EndingPoint - StartingPoint + 1
        if NumOfPointsReq > TotalNumOfPoints:
            raise Exception('Number of Points Requested Exceeds the number in File')
    else:
        if t0 == 0.:
            t0 = 1
        t0 = int(np.ceil(t0))
        tend = int(np.ceil(tend))
        NumOfPointsReq = tend - t0 + 1
        if NumOfPointsReq > TotalNumOfPoints:
            raise Exception('Number of Points Requested Exceeds the number in File')
        StartingGroup = int(np.ceil(t0/GroupSize))
        StartingPoint = int(t0)
        EndingGroup = int(np.ceil(tend/GroupSize))
        EndingPoint = int(tend)
    # Preallocate
    x = np.zeros((NumOfPointsReq,len(channels)))
    ReadCounter = 0
    LengthinGroupOld = 0
    
    # Loop over number of groups
    for CurrentGroup in range(StartingGroup,EndingGroup+1):
        # Set start and end points in group
        StartingPointinGroup = 1
        EndingPointinGroup = GroupSize
        if CurrentGroup == StartingGroup:
            StartingPointinGroup = StartingPoint - GroupSize*(StartingGroup-1)
            EndingPointinGroup = GroupSize
        if CurrentGroup == EndingGroup:
            StartingPointinGroup = 1
            EndingPointinGroup = EndingPoint - GroupSize*(EndingGroup-1)
        if StartingGroup == EndingGroup:
            StartingPointinGroup = StartingPoint - GroupSize*(StartingGroup-1)
            EndingPointinGroup = EndingPoint - GroupSize*(EndingGroup-1)
        # Calculate length of group
        LengthinGroup = EndingPointinGroup-StartingPointinGroup+1
        # Loop over channels to be saved
        for no in indSorted:
            # Data not to process
            LengthNotRead = GroupSize*(channels[no]-1+(CurrentGroup-1)*NumChan)+StartingPointinGroup-1-ReadCounter
            if LengthNotRead:
                np.fromfile(rpcFile,np.dtype(np.int16),LengthNotRead)
            # Data to read
            records = np.fromfile(rpcFile,np.dtype(np.int16),LengthinGroup)
            # Read counter
            ReadCounter += LengthNotRead + LengthinGroup
            # Process read data and save to numpy array
            x[LengthinGroupOld:LengthinGroupOld+LengthinGroup,no] = [xi*scales[no] for xi in records.tolist()]
        
        # Length of previous group
        LengthinGroupOld += LengthinGroup
    
    ## Old MATLAB code kept and can be convertet to Python if needed. 
    ##------Jan Granng 2003-01-17 modification because some name files includ a empty first row
    # if length(deblank(char(names(1,:))))==0
    #    names2=[];
    #    for i=1:length(channels)
    #        names2(i,:) = names((channels(1,i)+1),:);
    #    end
    #    %names2=names2(channels,:);
    #else
    #    names2 = names(channels,:);
    #end
    #names=char(names2);
    ##----End modification for empty first rows--
    
    rpcFile.close()

    return x, dt, names, units, scales


def rpcmakeheader(x, dt=1.0, names=[], units=[], scales=np.empty(0), types=0, FrameSize=1024, GroupSize=2048):
    #######################################################################
    #
    # dic = rpcmakeheader(x, dt, names, units, scales, type, FrameSize, GroupSize)
    #
    # Make up the header of a time history. All argumets, except x, are optional.
    # More info about input variables in function "savesrpc".
    # 
    # Output variable:
    #   dic : Dictionary with all header information
    #         Type: dictionary (collections.OrderedDict)
    #
    #
    # Created on 2021-02-22
    # @author: Britta Kallman, bkallman
    #
    #######################################################################
    
    # Size of data
    Npoint, NumChan = x.shape
    
    # === CHECK CORRECT INPUT ===
    # Check that input dt is float or integer, make it float if integer
    if isinstance(dt,int):
        dt = float(dt)
    elif not isinstance(dt,(float,int)):
        raise Exception('Input ''dt'' must be float or integer.')
    # Create default channel names if no input
    if not names:
        names = [('Channel %4d' % i) for i in range(1,NumChan+1)]
    # Crete default units if no input
    if not units:
        units = ['Eng. Units' for i in range(1,NumChan+1)]
    # Create default scales if no input
    largest = 32752
    if not any(scales):
        scales = np.max(abs(x),0)/largest
        scales[scales==0] = 1e-8 # Avoiding having scales = 0
    else:
        # Check that scales is numpy array, otherwise make it one
        if not isinstance(scales,np.ndarray):
            scales = np.array(scales)
        # If scales are defined, see if data does not exceed the full scale value. 
        m1,n1 = x.shape
        BadScalChan = np.where((1.0001*scales-np.max(abs(x/largest),0))<0)
        if any(BadScalChan):
            print('\nDATA EXCEEDS FULL SCALE VALUE. RESCALE THE DATA\n')
            print('-------------------------------------------------\n')
            print('Channel #\tCurrent Scale\tRecommended Scale\n')
            print('-------------------------------------------------\n')
            for ChanNo in BadScalChan:
                print('%g\t\t%e\t%e\n' % (ChanNo,scales(ChanNo),np.max(abs(x[:,ChanNo]/32752),0)))
            print('-------------------------------------------------\n')
            raise Exception('Retry with New Scales')
    # File type
    FileType = ['RESPONSE', 'DRIVE   ']
    # =================================
    
    Npar = int(NumChan*6 + 18)
    Nhead = int(np.ceil(float(Npar)/4))
    Nframe = int(np.ceil(Npoint/FrameSize))
    
    dic = OrderedDict() # Dictionary that keeps order as they are inputted in
    dic['FORMAT'] = 'BINARY'
    dic['NUM_HEADER_BLOCKS'] = str(Nhead)
    dic['NUM_PARAMS'] = str(Npar)
    dic['FILE_TYPE'] = 'TIME_HISTORY'
    dic['TIME_TYPE'] = FileType[types]
    dic['DELTA_T'] = ('%12.6e' % dt)
    dic['PTS_PER_FRAME'] = str(FrameSize)
    dic['CHANNELS'] = str(NumChan)
    dic['PTS_PER_GROUP'] = str(GroupSize)
    dic['BYPASS_FILTER'] = '0'
    dic['HALF_FRAMES'] = '0'
    dic['REPEATS'] = '0'
    dic['FRAMES'] = str(Nframe)
    # Channel specifics for header
    for i in range(1,NumChan+1):
        dic['SCALE.CHAN_' + str(i)] = ('%12.6e' % scales[i-1])
        dic['UPPER_LIMIT.CHAN_' + str(i)] = '1.0'
        dic['LOWER_LIMIT.CHAN_' + str(i)] = '-1.0'
        dic['MAP.CHAN_' + str(i)] = str(i)
    
    dic['PARTITIONS'] = '1'
    dic['PART.CHAN_1'] = '1'
    dic['PART.NCHAN_1'] = str(NumChan)
    # Channel specifics for header
    for i in range(1,NumChan+1):
        dic['DESC.CHAN_' + str(i)] = names[i-1]
        dic['UNITS.CHAN_' + str(i)] = units[i-1]
    
    # Set current date and time
    now = datetime.now()
    # Fix format
    Date = now.strftime("%Y-%m-%d  %H:%M:%S")
    dic['DATE'] = Date
    
    dic['OPERATION'] = 'SaveRPC (Python)'
    
    return dic

def rpcwriteheader(fid, dic):
    #######################################################################
    #
    # rpcwriteheader(fid, dic)
    #
    # Write the header of a time history file already open.
    #
    # More info about how these binary files is built is found here:
    # https://www.mts.com/cs/groups/public/documents/library/mts_007569.pdf
    #
    # Input variables:
    #   fid : file ID for binary file to write RPC header to.
    #
    #   dic : Dictionary with all header information
    #         Type: dictionary (collections.OrderedDict)
    # 
    #
    # Created on 2021-02-22
    # @author: Britta Kallman, bkallman
    #
    #######################################################################
    
    # === CHECK CORRECT INPUT ===
    # Check that input dt is float or integer, make it float if integer
    if not isinstance(dic,(dict,OrderedDict)):
        raise Exception('Variable ''dic'' need to be a dictionary.')
    # =================================
    
    # Define block size
    BlockSize = 512
    
    # Define head size
    Nhead = int(dic['NUM_HEADER_BLOCKS'])
    keyLength = 32
    valLength = 96
    totLength = keyLength + valLength
    
    # Preallocate head size
    head = np.zeros(Nhead*BlockSize)
    # Preallocate binary string
    headStr = b''
    
    # Loop over each key in the dictionary
    for i, key in enumerate(dic):
        # Add key for header
        if len(key) > keyLength:
            key = key[:keyLength]
        keyVec = [ord(k) for k in key]
        head[totLength*i:totLength*i+len(keyVec)] = keyVec
        headStr += key.encode('ascii')
        headStr += b'\x00'*((totLength*i+keyLength)-(totLength*i+len(keyVec)))
        
        # Add value to key for header
        val = dic[key]
        if len(val) > valLength:
            val = val[:valLength]
        valVec = [ord(v) for v in val]
        startInd = totLength*i+keyLength
        head[startInd:startInd+len(valVec)] = valVec
        headStr += val.encode('ascii')
        headStr += b'\x00'*(totLength*(i+1)-(startInd+len(valVec)))
    
    # Fill out head
    if len(headStr) < Nhead*BlockSize:
        headStr += b'\x00'*(Nhead*BlockSize-len(headStr))
    
    # Write everything to file
    fid.write(headStr)

def rpcwritetime(fid, x, dic):
    #######################################################################
    #
    # rpcwritetime(fid, x, dic)
    #
    # Write the time history to a file already open, and
    # positioned at the beginning of the data segment. 
    #
    # More info about how these binary files is built is found here:
    # https://www.mts.com/cs/groups/public/documents/library/mts_007569.pdf
    #
    # Input variables:
    #   fid : file ID for binary file to write RPC header to.
    #
    #   x   : Array with the time history to be written to file. One column 
    #         per channel.
    #         Type: list or numpy array (numpy.ndarray)
    #
    #   dic : Dictionary with all header information
    #         Type: dictionary (dict or collections.OrderedDict)
    # 
    #
    # Created on 2021-02-22
    # @author: Britta Kallman, bkallman
    #
    #######################################################################
    
    # === CHECK CORRECT INPUT ===
    # Check that x data is numpy array, otherwise make it one
    if isinstance(x,list):
        x = np.array(x)
    elif not isinstance(x,np.ndarray):
        raise Exception('Wrong input data for ''x''.')
    # Check that input dt is float or integer, make it float if integer
    if not isinstance(dic,(dict,OrderedDict)):
        raise Exception('Variable ''dic'' need to be a dictionary.')
    # =================================
    
    # Data from header needed to process and write data
    NumChan = int(dic['CHANNELS'])
    NumFrame = int(dic['FRAMES'])
    GroupSize = int(dic['PTS_PER_GROUP'])
    FrameSize = int(dic['PTS_PER_FRAME'])
    scales = np.array([float(dic[temp]) for temp in dic if 'SCALE' in temp])
    HalfFrame = int(dic['HALF_FRAMES'])
    NumFrame = NumFrame + HalfFrame
    
    NumberOfFramesPerGroup = GroupSize/FrameSize
    NumberOfGroups = int(np.ceil(float(NumFrame)/float(NumberOfFramesPerGroup)))
#    TotalDataPoints = NumberOfGroups*GroupSize*NumChan
    TotalDataPerChannel = NumberOfGroups*GroupSize
    
    y = np.zeros((TotalDataPerChannel, NumChan))
    l, m = x.shape
    y[:l,:] = x/scales
    y = np.rint(y)  # Round to closest integer
    y = y.astype(int)   # Transform to integers (from float)
    
    # pad the end of x with the last data point in each channel
    fill = y[l-1,:]
    y[l:TotalDataPerChannel,:] = fill
    
     # Loop over groups with data
    for i in range(NumberOfGroups):
        z = np.reshape(y[i*GroupSize:(i+1)*GroupSize,:], GroupSize*NumChan,'F')
        xStr = array.array('h',z)
        fid.write(xStr)


def savesrpc(fileName, x, dt=1.0, names=[], units=[], scales=np.empty(0), types=0, FrameSize=1024, GroupSize=2048):
    ##############################################################################
    #
    # Function to write (save) rpc-3 time history data file. 
    #
    # Full syntax:
    # savesrpc(file, x, dt, names, units, scales, types, FrameSize, GroupSize)
    #
    #   The arguments are,
    #     fileName : Input variable (required).
    #                A string containing the rpc file name.
    #                The file extension must be included.
    #                Type: string
    #
    #     x        : Input variable (required).  
    #                An array containing the time history to be stored.
    #                each column represents a channel of data.
    #                Type: List or numpy array (np.ndarray)
    #
    #     dt       : Input variable (required for appending the data).
    #                The delta_t of the time history data. defaults to 1.0
    #                Type: float or integer
    #
    #     names    : Input variable (reuired for appending the data).
    #                A list of strings containing channel names. 
    #                Defaults to 'Channel 1', 'Channel 2', etc..
    #                Type: list
    #
    #     units    : Input variable (required for appending the data).
    #                A list of strings containing channel units.
    #                Defaults to 'Eng. Units'.
    #                Type: list
    #
    #     scales   : Input variable (required for appending data).
    #                An array of scale values for each channel. saverspc uses
    #                the scale to convert the data, represented in engineering
    #                units in the array x, into 2-byte integer numbers required
    #                by RPC format. For channel i, a data point d will be 
    #                converted as, ix = d/scale(i). For drive files, the scale 
    #                should be chosen so that the "full scale" value in 
    #                engineering units will correspond to the integer vaue,  
    #                32752. i.e., scale = full_scale_value/32752. If the scale 
    #                is not specified when the first segment of data is being 
    #                written, then the scales are created automatically.
    #                Type: list or numpy array (np.ndarray)
    #
    #     types    : Type of rpc time history file (optional), default = 0. 
    #                0=response, 1=drive
    #
    #     FrameSize: Number of points per frame (optional), default = 1024
    #
    #     GroupSize: Number of points per group (optional), default = 2048
    #
    # 
    # Created on 2021-02-22
    # @author: Britta Kallman, bkallman
    ##############################################################################
    
    # Check that x data is numpy array, otherwise make it one
    if isinstance(x,list):
        x = np.array(x)
    elif not isinstance(x,np.ndarray):
        raise Exception('Wrong input data for ''x''.')
    
    # Size of data
    Npoint, NumChan = x.shape
    
    # === CHECK CORRECT INPUT ===
    # Check that the input file name (fileName) is a string
    if not isinstance(fileName,str):
        raise Exception('Input ''fileName'' needs to be a string.')
    else:
        # Remove any trailing blanks in the filename
        fileName = fileName.replace(' ','')
    # Check that input dt is float or integer, make it float if integer
    if isinstance(dt,int):
        dt = float(dt)
    elif not isinstance(dt,(float,int)):
        raise Exception('Input ''dt'' must be float or integer.')
    # Create default channel names if no input
    if not names:
        names = [('Channel %4d' % i) for i in range(1,NumChan+1)]
    # Crete default units if no input
    if not units:
        units = ['Eng. Units' for i in range(1,NumChan+1)]
    # Create default scales if no input
    largest = 32752
    if not any(scales):
        scales = np.max(abs(x),0)/largest
        scales[scales==0] = 1e-8 # Avoiding having scales = 0
    else:
        # Check that scales is numpy array, otherwise make it one
        if not isinstance(scales,np.ndarray):
            scales = np.array(scales)
        # If scales are defined, see if data does not exceed the full scale value. 
        m1,n1 = x.shape
        BadScalChan = np.where((1.0001*scales-np.max(abs(x/largest),0))<0)
        if any(BadScalChan):
            print('\nDATA EXCEEDS FULL SCALE VALUE. RESCALE THE DATA\n')
            print('-------------------------------------------------\n')
            print('Channel #\tCurrent Scale\tRecommended Scale\n')
            print('-------------------------------------------------\n')
            for ChanNo in BadScalChan:
                print('%g\t\t%e\t%e\n' % (ChanNo,scales(ChanNo),np.max(abs(x[:,ChanNo]/32752),0)))
            print('-------------------------------------------------\n')
            raise Exception('Retry with New Scales')
    # =================================
    
    # Open the new file to write to
    fid = open(fileName,'wb')
    
    # New file, i.e. first time --> create header, writeheader and write data
    dic = rpcmakeheader(x, dt, names, units, scales, types, FrameSize, GroupSize)
    rpcwriteheader(fid, dic)
    rpcwritetime(fid, x, dic)
    
    # Close file
    fid.close()
    
