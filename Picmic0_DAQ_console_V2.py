#!/usr/bin/env python3
# -*- coding: utf-8 -*-
##@file Picmic0_DAQ_console.py
#
#@brief Software using the picmic0_data_dll and the Msis0_LV_dll to acquire data from picmic0 in console mode
#  


# *****************************************************************************************************************
#
# Script goal
#
# This script is a demo, not a final sw ready to use to configure PICMIC. 
# Its main goal is to be used as an example to build your own application 
# a console menu, commands in Python interpreter, a GUI demo with Python QT
#
# Therefore
#
#
# Version V1.0
#
# Versions list
#
# V1.0 03/02/2022 - MS
#
# *****************************************************************************************************************


# ===========================================================================
# Modules import
# ===========================================================================

import os
import logging     # for the logging system 
import logging.config
import threading
import sys
import time
import ctypes as ct 
import _ctypes
import numpy as np
#import matplotlib.pyplot as plt
#from matplotlib.widgets import RadioButtons,Slider,RangeSlider,Button
import importlib
from importlib import reload
import configparser    # for the ini file configuration retrieving 


# retrieve the modules names from the Modules.conf file
config = configparser.ConfigParser(allow_no_value=True)
config.read("modules/Modules.conf")

sys.path.append('..')







LoggingFileName =  os.path.abspath(os.path.join(os.getcwd(),'logging','logging_DAQ.conf'))
print(LoggingFileName)
try:
    logging.config.fileConfig(LoggingFileName)
except:
    pass
#logging.config.fileConfig('logging/logging.conf')
logger = logging.getLogger('pm0ddaq')
logger.error('Logging Started')







## DLL Modules inclusion
#from DLL.PM0D_dll_wrapper import VLib as PM0D  # wrapper for the functions of the picmic0_data_dll.dll 
#from DLL.Msis0_LV_dll_wrapper import VLib as MSIS0LV  # wrapper for the functions of the Msis0_LV_dll.dll 

PM0_DAQ_Func_Name = config['ModuleName']['daqFuncts']
#import Picmic_Daq_Func_11 as PM0_DAQ_Func    # Acquisitions functions  for picmic
PM0_DAQ_Func= importlib.import_module(PM0_DAQ_Func_Name, package=None)
PM0_DF = PM0_DAQ_Func.Picmic_DAQ_Functs()



Matrix_plottingName = config['ModuleName']['matrixPlotting']
#import import Matrix_plotting as MPlot
MPlot= importlib.import_module(Matrix_plottingName, package=None)

DataReadingName = config['ModuleName']['dataReading']
#import DataReading
DataReading= importlib.import_module(DataReadingName, package=None)



#from Picmic_Daq_Func_10 import Picmic_DAQ_Functs as PM0_DF
#import DataReading
#import Matrix_plotting as MPlot


# ===========================================================================
# Constants
# ===========================================================================





# ===========================================================================
# Global variables
# ===========================================================================

# For menu handling

VGChoiceStr = ""
VGChoiceInt = 0
VGQuit      = False
VGBadCmd    = False
VGStatus    = "No status yet"

# For log level in Arduino DUE console

VGLogRaw    = 0 # If 1 => it logs commands RAW data buffers in Arduino DUE console window
VGLogCmd    = 0 # If 1 => it logs commands names and param in Arduino DUE console window
                # If 2 => it logs commands names, param and registers data in Arduino DUE console window
                
# For error messages in PC Python console  

VGLogErrMode = 2 # 0 = log and clear, 1 = print message and wait 5 seconds, 2 = print message and wait CR, 3 = let all message in console = dones't clear screen before menu printing
  



VGMaxDataBufferSize = 10000000
VGMaxStatusBufferSize = 512
VGFrameNbByAcq = 100
VGTotalFrameNb = 1000
VGFrameLength = 16500


VGFilePath = "C:\\python\\Mimosis0_daq\\data"

VGFilePrefix  = "Test_File"

VGRunNb = 666
VGPrintFormat = 1
loggerName = "MSIS0_DAQ_Cons"
#logger = logging.getLogger(loggerName)
VOneFileByAcq = 0
VGFrameToPlot = ct.c_int(0)
VGFirstFrameToPlot = ct.c_int(0)
VGLastFrameToPlot = ct.c_int(0)
VGPlotType = ct.c_int(0)
VGSaveNormData = ct.c_int(0)


VGChipSelected = 0



# ===========================================================================
# Functions
# ===========================================================================





def FClear () :

    '''
    ...
    
    Clears screen, used to display only the menu options list 
    
    Param
    - None
    
    Returns
    - Nothing
    
    26/12/2021 G.CLAUS CNRS/IN2P3/IPHC/C4PI
    
    '''



    os.system ( 'cls' )


def FMenu1Print ( Status ) :
  
    '''
    ...
    
    Displays the menu commands list 
    
    Param
    - None
    
    Returns
    - Nothing
    
    03/02/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI
    
    '''
  
    if ( VGLogErrMode != 3 ) :
        FClear ()  

    print ( "" )
    print ( "Picmic0_DAQ_console.py" )
    print ( "" )    
    print ( "------- Menu -------" )	
    print ( "100 - Quit" )
    print ( "-----------------------" )
    print ( "10 - Init DLL " )
    print ( "-----------------------" )
    print ( "20 - Set saving file name " )    
    print ( "21 - Start run " )    
    print ( "22 - Acquisition polling" )	
    print ( "23 - Generate Header and data csv files " )    
    print ( "24 - Print the data from file " )  
    print ( "25 - Plot Frame ")  
    print ( "26 - Generate Normalised data from file")
    print ( "-----------------------" )
    print ( "30 - Take run and generates normalised data" )
    print ( "31 - Take several runs and generates normalised data" )
    print ( "-----------------------" )
    print ( "90 - Free DLL" )


    print ( "-----------------------" )
    print ( "" )	
    print ( "Status :", Status )
    print ( "" )	

 


def FMenu1Exec ( Choice ) :

    '''
    ...
    
    Executes menu action selected by user
    
    Param
    - Choice = The No (menu command) of the action to execute
    
    Returns
    - VQuit = bool : true if a quit command has been issued
    - VBadCmd = bool : true if the last command was not correct
    - VStatus = string returning the status of the function
    
    03/02/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI
    
    '''

    global VGLogErrMode
    global VGMaxDataBufferSize
    global VGFrameNbByAcq
    global VGTotalFrameNb
    global VGFrameLength
    global VGSaveNormData

    global VGFilePath
    global VGFilePrefix
    global VGRunNb
    global VOneFileByAcq
    global VGPrintFormat
    global VGFrameToPlot
    global VGPlotType
    global VGFirstFrameToPlot
    global VGLastFrameToPlot

    
    global VGChipSelected
    global logger
    global loggerName
   
   
    VErr    = 0
    VQuit   = False
    VBadCmd    = False
    VStatus = ""	
        
    print ( "" )		

    # Init DLL

    if Choice == 10 :
        VErr = PM0_DF.Init_DLL()
        VStatus = "Init DLL done - Result = {:d}".format (VErr)
        if (VErr >= 0):
            logger.info(VStatus)
        else:
            logger.error(VStatus)


    # Set saving file name

    elif Choice == 20 :

        print( "FilePath: directory where the data saving file ")
        print("previous was :{:s}".format(VGFilePath))
        FilePath = input ("Choice :")
        if FilePath != "" :
            VGFilePath = FilePath
        print( "Prefix: prefix of the save file name ")
        print("previous was :{:s}".format(VGFilePrefix))
        FilePrefix = input ("Choice :")
        if FilePrefix != "" :
            VGFilePrefix = FilePrefix
        print( "Run No Number of the run to be taken")
        print("previous was :{:d}".format(VGRunNb))
        RunNb = input ("Choice :")
        if RunNb != "" :
            VGRunNb = int(RunNb,10)

        VErr = PM0_DF.SetSaveFileName(VGFilePath,VGRunNb,VGFilePrefix)
        VStatus = "SetSaveFileName done - Result = {:d}".format (VErr)
        if (VErr >= 0):
            logger.info(VStatus)
        else:
            logger.error(VStatus)

    # Start run

    elif Choice == 21 :
        ClockRateStr = input ("ClockRate (default:20 MHz):")
        if ClockRateStr == "" :
            ClockRate = 20000000.0
        else:
            ClockRate = int(ClockRateStr,10) * 1000000.0
        print( "DataRate: selection of the data rate of the sampling (default=1) can be :")
        print("    - 1 : Single Data Rate (SDR)")
        print("    - 2 : Double Data Rate (DDR)")
        DataRateStr = input ("Choice (default:1:SDR):")
        if DataRateStr == "" :
            DataRate = 1
        else:
            DataRate = int(DataRateStr,10)
        
        print("- SamplingEdge: edge of the clock used for the sampling (default=18) can be:")
        print("    - 18 : falling edge")
        print("    - 19 : rising edge")
        print("    - 20 : rising edge + delay")
        SamplingEdgeStr = input ("Choice (default:18:falling edge):")
        if SamplingEdgeStr == "" :
            SamplingEdge = 18
        else:
            SamplingEdge = int(SamplingEdgeStr,10)
        
        FrameLengthStr = input("FrameLength: size of the frame in clock count (default=16500) :")
        if FrameLengthStr == "" :
            FrameLength = 16500
        else:
            FrameLength = int(FrameLengthStr,10)
        VGFrameLength = FrameLength
        FrameNbByAcqStr = input("FrameNbByAcq: number of frames by acquisition (default=100)")
        if FrameNbByAcqStr == "" :
            FrameNbByAcq = 100
        else:
            FrameNbByAcq = int(FrameNbByAcqStr,10)
        
        VGFrameNbByAcq = FrameNbByAcq

        TotalFrameNbStr = input("- TotalFrameNb: total frame number of a run (default=1000)")
        if TotalFrameNbStr == "" :
            TotalFrameNb = 1000
        else:
            TotalFrameNb = int(TotalFrameNbStr,10)
        VGTotalFrameNb = TotalFrameNb
        
        VErr = PM0_DF.Start_Run(ClockRate,DataRate,SamplingEdge,FrameLength,FrameNbByAcq,TotalFrameNb)
        VStatus = "Start run done- result = {:d}".format ( VErr)
        if (VErr >= 0):
            logger.info(VStatus)
        else:
            logger.error(VStatus)

    # Acquisition polling

    elif Choice == 22 :
        print("Acquisition polling")
        print("  - 0 : acquisition with data saving on files")
        print("  - 1 : acquisition with data saving on files and data logging")
        print("  - 2 : acquisition with only data logging")
        print("  - 3 : emulate datas ")
        AcqTypeStr = input ("Choice (default:0:only data saving on disk ):")
        if AcqTypeStr == "" :
            AcqType = 0
        else:
            AcqType = int(AcqTypeStr,10)
            
        #PM0_DF.Acq_Polling(AcqType)

        if AcqType in [0,3]:
            # Acquisition with only data saving
            VErr,TotalSmpNbByAcq = PM0_DF.Acq_Polling(AcqType)
            VStatus = "Acq polling done - result = {:d}".format ( VErr)
            if (VErr >= 0):
                logger.info(VStatus)
            else:
                logger.error(VStatus)
        elif AcqType in [1,2] :
            # acquisition with data saving and return 
            VErr,TotalSmpNbByAcq,Data = PM0_DF.Acq_Polling(AcqType)
            if (VErr >= 0):
                logger.info(VStatus)
                PM0_DF.PlotDataFromBuffer( Data,0)
                #DataReading.FPrintFrameListFromBuffer(Data, VGFrameLength, VGTotalFrameNb)
            else:
                logger.error(VStatus)




        

    # Generate header and data csv files

    elif Choice == 23 :

        print( "FilePath: directory where the data saving file ")
        print("previous was :{:s}".format(VGFilePath))
        FilePath = input ("Choice :")
        if FilePath != "" :
            VGFilePath = FilePath
        print( "Prefix: prefix of the save file name ")
        print("previous was :{:s}".format(VGFilePrefix))
        FilePrefix = input ("Choice :")
        if FilePrefix != "" :
            VGFilePrefix = FilePrefix
        print( "Run No : Number of the run to be taken")
        print("previous was :{:d}".format(VGRunNb))
        RunNb = input ("Choice :")
        if RunNb != "" :
            VGRunNb = int(RunNb,10)
        print( "Multiple data files ?")
        print( "0 : only one file")
        print ("1 : one file by acquisition")
        print("previous was :{:d}".format(VOneFileByAcq))
        OneFile = input("Choice:")
        if OneFile != "" :
            VOneFileByAcq = int(OneFile,10)
        VErr = PM0_DF.GenerateHeaderDataCSVFiles(VGFilePath,VGFilePrefix,VGRunNb,VOneFileByAcq)
        VStatus = "Generates_data_header_CSV done - result = {:d}".format ( VErr)
        if (VErr >= 0):
            logger.info(VStatus)
        else:
            logger.error(VStatus)
 
    # Print Data from file

    elif Choice == 24 :

        print( "FilePath: directory where the data saving file ")
        print("previous was :{:s}".format(VGFilePath))
        FilePath = input ("Choice :")
        if FilePath != "" :
            VGFilePath = FilePath
        print( "Prefix: prefix of the save file name ")
        print("previous was :{:s}".format(VGFilePrefix))
        FilePrefix = input ("Choice :")
        if FilePrefix != "" :
            VGFilePrefix = FilePrefix
        print( "Run No : Number of the run to be taken")
        print("previous was :{:d}".format(VGRunNb))
        RunNb = input ("Choice :")
        if RunNb != "" :
            VGRunNb = int(RunNb,10)
        print( "Print format :")
        print (" 1: Raw data")
        print (" 2: Row / Col ")
        print("previous was :{:d}".format(VGPrintFormat))
        PrintFormat = input ("Choice :")
        if PrintFormat != "" :
            VGPrintFormat = int(PrintFormat,10)

        VErr = PM0_DF.PrintDataFromFile(VGFilePath,VGFilePrefix,VGRunNb,VGPrintFormat)
        if (VErr >= 0):
            logger.info(VStatus)
        else:
            logger.error(VStatus)

   # Plot Data from file

    elif Choice == 25 :

        print( "FilePath: directory where the data saving file ")
        print("previous was :{:s}".format(VGFilePath))
        FilePath = input ("Choice :")
        if FilePath != "" :
            VGFilePath = FilePath
        print( "Prefix: prefix of the save file name ")
        print("previous was :{:s}".format(VGFilePrefix))
        FilePrefix = input ("Choice :")
        if FilePrefix != "" :
            VGFilePrefix = FilePrefix
        print( "Run No : Number of the run to be taken")
        print("previous was :{:d}".format(VGRunNb))
        RunNb = input ("Choice :")
        if RunNb != "" :
            VGRunNb = int(RunNb,10)
        
        print( "Plot Type  ")
        print (" 0: One Frame")
        print (" 1: Sum of several frames ")
        print("previous was :{:d}".format(VGPlotType.value))
        PlotType = input ("Choice :")
        if PlotType != "" :
            VGPlotType.value = int(PlotType,10)

        VGFrameToPlot.value = -1

        PM0_DF.PlotDataFromFile(VGFilePath,VGFilePrefix,VGRunNb,VGPlotType.value)

   # Generate normalised data from file

    elif Choice == 26 :

        print( "FilePath: directory where the data saving file ")
        print("previous was :{:s}".format(VGFilePath))
        FilePath = input ("Choice :")
        if FilePath != "" :
            VGFilePath = FilePath
        print( "Prefix: prefix of the save file name ")
        print("previous was :{:s}".format(VGFilePrefix))
        FilePrefix = input ("Choice :")
        if FilePrefix != "" :
            VGFilePrefix = FilePrefix
        print( "Run No : Number of the run to be taken")
        print("previous was :{:d}".format(VGRunNb))
        RunNb = input ("Choice :")
        if RunNb != "" :
            VGRunNb = int(RunNb,10)
        
        print( "Save data on disk ?  ")
        print (" 0: No")
        print (" 1: Save data on disk")
        print (" 2: Save only touched pixels data on disk")
        print("previous was :{:d}".format(VGSaveNormData.value))
        SaveData = input ("Choice :")
        if SaveData != "" :
            VGSaveNormData.value = int(SaveData,10)

        #VGSaveNormData.value = -1

        NormMatrix,VPixelList = PM0_DF.GetNormalisedDataFromFile(VGFilePath,VGFilePrefix,VGRunNb,VGSaveNormData.value)
        input('Press return to continue')
        #MPlot.PlotMatrix2D (NormMatrix)  
        
        
   # Generate normalised data from file

    elif Choice == 30 :

        print( "FilePath: directory where the data saving file ")
        print("previous was :{:s}".format(VGFilePath))
        FilePath = input ("Choice :")
        if FilePath != "" :
            VGFilePath = FilePath
        print( "Prefix: prefix of the save file name ")
        print("previous was :{:s}".format(VGFilePrefix))
        FilePrefix = input ("Choice :")
        if FilePrefix != "" :
            VGFilePrefix = FilePrefix
        print( "Run No : Number of the run to be taken")
        print("previous was :{:d}".format(VGRunNb))
        RunNb = input ("Choice :")
        if RunNb != "" :
            VGRunNb = int(RunNb,10)
            
        print( "Framelength  ")
        print("previous was :{:d}".format(VGFrameLength))
        Framelength = input ("Choice :")
        if Framelength != "" :
            VGFrameLength = int(Framelength,10)
            
        VResult, VPixelList = PM0_DF.SCurveTakeOneStep(VGFilePath,VGRunNb,VGFilePrefix,VGFrameLength)
        if VResult < 0:
            print('ERROR :{}'.format(VResult))
        else:
            print('Pixel list :{}'.format(VPixelList))
        
        input('Press return to continue')
        
   # Generate normalised data from file several consecutive runs

    elif Choice == 31 :

        print( "FilePath: directory where the data saving file ")
        print("previous was :{:s}".format(VGFilePath))
        FilePath = input ("Choice :")
        if FilePath != "" :
            VGFilePath = FilePath
        print( "Prefix: prefix of the save file name ")
        print("previous was :{:s}".format(VGFilePrefix))
        FilePrefix = input ("Choice :")
        if FilePrefix != "" :
            VGFilePrefix = FilePrefix
        print( "Run No : Number of the run to be taken")
        print("previous was :{:d}".format(VGRunNb))
        RunNb = input ("Choice :")
        if RunNb != "" :
            VGRunNb = int(RunNb,10)
        
        print( "Framelength  ")
        print("previous was :{:d}".format(VGFrameLength))
        Framelength = input ("Choice :")
        if Framelength != "" :
            VGFrameLength = int(Framelength,10)

        #VGSaveNormData.value = -1
        for VRunIndex in range (VGRunNb):
            VResult, VPixelList = PM0_DF.SCurveTakeOneStep(VGFilePath,VRunIndex,VGFilePrefix,VGFrameLength)
            if VResult < 0:
                print('ERROR :{}'.format(VResult))
            else:
                print('run {} out of {} done'.format(VRunIndex,VGRunNb))
        
        input('Press return to continue')
        
        

    # Free DLL

    elif Choice == 90 :
        VErr = PM0_DF.Free_DLL()
        VStatus = "Free dll done - result = {:d}".format ( VErr)
        if (VErr >= 0):
            logger.info(VStatus)
        else:
            logger.error(VStatus)



    elif Choice == 100 :
    
            
        VQuit = True
        VStatus = "Quit has been selected"
        logger.info(VStatus)
        
    else :
        VBadCmd = True
        VStatus = "Unkown choice !" 
        logger.error(VStatus)
        # Bad cmd


    if ( VErr != 0 ) :
    
        # VGLogErrMode = 0 # 0 = No errors messages, 1 = print message and wait 5 seconds, 2 = print message and wait CR, 3 = let all message in console = dones't clear screen before menu printing

        if ( VGLogErrMode == 1 ) :
             time.sleep(5)
        
        elif ( VGLogErrMode == 2 ) :
            print ( "" )
            input ( "Error - Enter CR to continue " )
       

    print ( "" )	

    return ( VQuit, VBadCmd, VStatus )






# ===========================================================================
# Main "function" executed at script startup
#
# 04/02/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI
# ===========================================================================



if __name__ == '__main__':

    
    vg_time_beg = 0


    
    #logger = Init_Logging("MSIS0_DAQ_Cons")
        
    ##  DirPath : absolute path to the working directory
    DirPath = os.path.abspath('')
    ## VGFilePath : Full path for data savnig directory
    VGFilePath = os.path.join(DirPath, 'data')
        

    logger.error('VGFilePath:{}'.format(VGFilePath))

    VGFilePrefix = "Test_File"
    VGRunNb = 666
    
    
    while VGQuit == False :

        FMenu1Print ( VGStatus )
        VGChoiceStr = input ( "Choice ? " ) 

        try :
            VGChoiceInt = int ( VGChoiceStr, 10 )
            VGQuit, VGBadCmd, VGStatus = FMenu1Exec ( VGChoiceInt )
        
        except :
        
          while (1) :
            
            # In case it is not one of the previous cases, to avoid endless loop  ;-)
            # For example => exception generated when users enters a command which is not a number
            break    
            
        
          VGStatus = VGStatus + "\n\n" + "Exception : " + str ( sys.exc_info () )    
         

    PM0_DF.Free_DLL()    
    logger.critical("Picmic0 DAQ now ending")


    #try :
    #    del (PM0D)
    #except NameError:
    #    logger.error('deleting PM0D FAILED')
    #try :
    #    del (MSIS0LV)
    #except NameError:
    #    logger.error('deleting MSIS0LV FAILED')


    # Release all the logging handlers

    # handlers = logging.getLogger("MSIS0_DAQ_Cons").handlers[:]
    # for handler in handlers:
        # logging.getLogger("MSIS0_DAQ_Cons").removeHandler(handler)


    handlers = logger.handlers[:]
    for handler in handlers:
        handler.close()
        logger.removeHandler(handler)
   
    logging.shutdown() 
    sys.path.remove('..')

