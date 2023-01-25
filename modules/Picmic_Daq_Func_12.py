#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Module containing the class for the high level functions for the picmic slow control software
 


Version V1.1

Versions list

V1.0 24/1/2022 - MS
V1.1 24/11/2022 - MS : changed the module import system : added a file (Module.conf)  to store all the modules names: only one place to modify the modules name on name change
V1.2 02/12/2022 - MS : added the SCurveTakeOneStep function to automatise the data taking for the discriminators s-curves
"""

__author__ = "Matthieu Specht"
__version__ = '0.1.2'
__maintainer__ = "Matthieu Specht"
__email__ = "matthieu.specht@iphc.cnrs.fr"
__date__ = "2022-12-02"



# ===========================================================================
# Modules import
# ===========================================================================

import os
import logging     # for the logging system 
import threading
import sys
import time
import ctypes as ct 
import _ctypes
import numpy as np
import importlib
from importlib import reload
import configparser    # for the ini file configuration retrieving 


# DLL Modules inclusion
from DLL.PM0D_dll_wrapper import VLib as PM0D  # wrapper for the functions of the picmic0_data_dll.dll 
from DLL.Msis0_LV_dll_wrapper import VLib as MSIS0LV  # wrapper for the functions of the Msis0_LV_dll.dll 



# retrieve the modules names from the Modules.conf file
config = configparser.ConfigParser(allow_no_value=True)
config.read("modules/Modules.conf")


DataReadingName = config['ModuleName']['dataReading']
DataReading= importlib.import_module(DataReadingName, package=None)


Matrix_plottingName = config['ModuleName']['matrixPlotting']
MPlot= importlib.import_module(Matrix_plottingName, package=None)




class Picmic_DAQ_Functs():
    """
        Class for the Acquisition methods for picmic
    """

    def __init__ (self):
        """
            Constructor of the class
        """

        self.VGMaxDataBufferSize = 10000000
        self.VGMaxStatusBufferSize = 512
        self.VGFrameNbByAcq = 100
        self.VGTotalFrameNb = 1000
        self.VGFrameLength = 16500

        self.VGFilePath = "C:\\python\\Picmic0_daq\\data"

        self.VGFilePrefix  = "Test_File"

        self.VGRunNb = 666

        self.VGFrameToPlot = ct.c_int(0)
        
        self.VGDLLInitilased = False
        
        self.logger = logging.getLogger('pm0ddf')
        self.logger.error('Logging Started')


    def Init_DLL(self):
        '''
        ...
        
        Initialise the DLL used for the acquisition
        
        Param
        - None
        
        Returns
        - result of the fonction : 0 : successfull / negative number : failed
        
        03/02/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI
        
        '''
        ## DLL Modules inclusion
        #from DLL.PM0D_dll_wrapper import VLib as PM0D  # wrapper for the functions of the Mimosis0_dll.dll 
        #from DLL.Msis0_LV_dll_wrapper import VLib as MSIS0LV  # wrapper for the functions of the Msis0_LV_dll.dll 
        #PM0D = reload(PM0D)
        #MSIS0LV = reload(MSIS0LV)
        ErrFileFullName = "c:\\tmp\\log\\Picmic0_DAQ_err_log.txt"
        ErrLogLevel = 1
        MsgFileFullName ="c:\\tmp\\log\\Picmic0_DAQ_msg_log.txt"
        MsgLogLevel = 1
        
        VIntFuncResult = PM0D._PM0D__FBegin(ErrLogLevel, ErrFileFullName.encode (),MsgLogLevel,MsgFileFullName.encode ())
        if  (VIntFuncResult < 0 ):
            self.logger.error('MIMOSIS0__FBegin FAILED')
            return -1
        else :
            self.logger.info('MIMOSIS0__FBegin successfull')
            
        VIntFuncResult = PM0D._PM0D__FSetErrorLogLevel(ErrLogLevel)
        if  (VIntFuncResult < 0 ):
            self.logger.error('_PM0D__FSetErrorLogLevel FAILED')
            return -2
        else :
            self.logger.info('_PM0D__FSetErrorLogLevel successfull')
        self.VGDLLInitilased = True
        return 0


    def __del__(self):
        """
            Destructor of the class
        """
        pass


    def Free_DLL(self):
        '''
        ...
        
        Free the DLL used for the acquisition
        
        Param
        - None
        
        Returns
        - result of the fonction : 0 : successfull / negative number : failed
        
        03/02/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI
        
        '''
        
        StatusBuffer      = ct.create_string_buffer(self.VGMaxStatusBufferSize) 
        StatusBufferLength = ct.c_int()
        Result = ct.c_ubyte()
        testvalue = ct.c_int()
        Instrument_Initialized = ct.c_byte()
        if (self.VGDLLInitilased == True) :
            try:
                MSIS0LV.GetGlobalVar(Instrument_Initialized,testvalue)
                self.logger.info('Before free dll:Instrument iniftialized :%d', Instrument_Initialized.value)
                if (Instrument_Initialized.value == 1) :
                    VIntFuncResult = MSIS0LV.Close_hdsio(StatusBuffer, ct.byref(Result),StatusBufferLength)
                    if  (VIntFuncResult < 0 ):
                        self.logger.error('Close_hdsio FAILED')
                        return -1
                    else :
                        self.logger.info('Close_hdsio successfull')
                
                    #print("Close_hdsio: string result :{:s} , length :{:d}, result IntResult:{:d} , BoolResult :{:d}".format (StatusBuffer.value,StatusBufferLength.value,VIntFuncResult,Result.value))
                else:
                    self.logger.error('HDSIO board was not opened, Close_hsdio function not called')
                ct.windll.kernel32.FreeLibrary(MSIS0LV._handle)
                del (MSIS0LV)
            except :
                self.logger.error('MSIS0LV DLL not loaded : cannot free it')
            
            try :
                VIntFuncResult = PM0D._PM0D__FEnd()
                print('_PM0D__FEnd:  result :{:d}'.format(VIntFuncResult))
                if  (VIntFuncResult < 0 ):
                    self.logger.error('_PM0D__FEnd FAILED')
                    return -2
                else :
                    self.logger.info('_PM0D__FEnd successfull')
                ct.windll.kernel32.FreeLibrary(PM0D._handle)
                del (PM0D)
            except :
                self.logger.error('PM0D DLL not loaded : cannot free it')
                
            self.VGDLLInitilased = False
        
        return 0
            



    def SetSaveFileName(self,FilePath,RunNo,Prefix):
        '''
        ...
        
        Set the file name for the data saving file
        
        Param
        - FilePath : Path to the directory in which the data file is saved
        - RunNo : Number of the run
        - Prefix : Prefix
        
        
        Returns
        - result of the fonction : 0 : successfull / negative number : failed
        
        03/02/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI
        
        '''
        VResult = PM0D._PM0D__FSetFileSaveFile ( FilePath.encode() , Prefix.encode() ,RunNo )
        return VResult


    def Start_Run(self,ClockRate=20000000.0,DataRate=1,SamplingEdge=18,FrameLength=16500,FrameNbByAcq=100,TotalFrameNb=1000):
        '''
        ...
        
        Start the run:
            - initiates the NI 6562 board
            - creates the savefile for the data saving
        
        Param
            - ClockRate: clock frequency used for the data sampling (default=20000000.0)
            - DataRate: selection of the data rate of the sampling (default=1) can be :
                - 1 : Single Data Rate (SDR)
                - 2 : Double Data Rate (DDR)
            - SamplingEdge: edge of the clock used for the sampling (default=18) can be:
                - 18 : falling edge
                - 19 : rising edge
                - 20 : rising edge + delay
            - FrameLength: size of the frame in clock count (default=16500)
            - FrameNbByAcq: number of frames by acquisition (default=100)
            - TotalFrameNb: total frame number of a run (default=1000)
        
        Returns
            - result of the fonction : 0 : successfull / negative number : failed
        
        03/02/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI
        
        '''
        StatusBuffer      = ct.create_string_buffer(self.VGMaxStatusBufferSize) 
        StatusBufferLength = ct.c_int()
        SmpNbAcquiredAcq = ct.c_int()
        Result = ct.c_ubyte()
        self.VGFrameLength = FrameLength
        self.VGFrameNbByAcq = FrameNbByAcq
        self.VGTotalFrameNb = TotalFrameNb
        StatusBufferLength.value = self.VGMaxStatusBufferSize
        if ((FrameNbByAcq  * FrameLength) > self.VGMaxDataBufferSize):
            # Bad acquisition params
            self.logger.error('Size of the acquisition exceeding the buffer size of :%d', self.VGMaxDataBufferSize)
            return -10
        else:
            #Start the acquisition with the mimosis0 dll
            VIntFuncResult = PM0D._PM0D__FStartRun (TotalFrameNb ,FrameNbByAcq , FrameLength , 0 , 0 ,  ClockRate) 
            if  (VIntFuncResult < 0 ):
                print('_PM0D__FStartRun FAILED')
                self.logger.error('_PM0D__FStartRun FAILED')
                return -1
            else :
                print('_PM0D__FStartRun successfull')
            
            # Start the acquisition on the NI6562 board
            VIntFuncResult = MSIS0LV.Start_acq_ext( ClockRate,  DataRate , SamplingEdge , FrameLength,  FrameNbByAcq, StatusBuffer,  SmpNbAcquiredAcq, ct.byref(Result),StatusBufferLength )
            if  (VIntFuncResult < 0 ):
                print('Start_acq_ext FAILED')
                self.logger.error('Start_acq_ext failed :%s', StatusBuffer.value)
                return -1
            else :
                print('Start_acq_ext successfull')
                self.logger.info('Start_acq_ext successfull :%s', StatusBuffer.value)
            return 0


    def Acq_Polling( self,GetDataBack = 0, verbose = 1):
        '''
        ...
        
        do the acquisition polling, for each acquisition do:
            - read the board memory
            - deals with the data as defined by the GetDataBack param
        
        Param
            - GetDataBack : acquired data use :
                    - 0 : data saving on files
                    - 1 : data saving on files and data logging
                    - 2 : only data logging
                    - 3 : Data emulation : real data ignored 
        
        Returns
            - result of the fonction : 0 : successfull / negative number : failed
        
        03/02/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI
        
        '''
        
        TotalAcqNb = self.VGTotalFrameNb // self.VGFrameNbByAcq
        self.logger.debug('Thread started for ',TotalAcqNb,' iterations, at : ',time.perf_counter())
        StatusBuffer      = ct.create_string_buffer(self.VGMaxStatusBufferSize) 
        StatusBufferLength = ct.c_int()
        Tn2DshortArray = ct.c_ushort * self.VGMaxDataBufferSize # Creates the type : array of 16 bits words with a size of VGMaxDataBufferSize
        RawDataBuffer = Tn2DshortArray()
        DataBuffer = Tn2DshortArray()
        DataBufferLength = ct.c_int()
        Result = ct.c_ubyte()
        SmpNbAcquired = ct.c_int()
        ValidSmpNb = ct.c_int()
        GlobalValidSmpNb = np.empty((0,0),dtype=ct.c_short)
        
        VLoop = 0
        #CurrentAcqIndex.value = 0
        DataBufferLength.value = self.VGMaxDataBufferSize
        StatusBufferLength.value = self.VGMaxStatusBufferSize
        if GetDataBack == 0 :
            for VLoop in range( TotalAcqNb ) :
                if verbose == 1:
                    print ("Acq No:{:d} out of {:d}".format(VLoop,TotalAcqNb))
                # Read the memory of the last frames
                VResult = MSIS0LV.Read_Waveform_ext( Result, ct.byref(SmpNbAcquired), RawDataBuffer, StatusBuffer, DataBufferLength, StatusBufferLength)
                # save the current acq with the mimosis0 dll
                PM0D._PM0D__FAcq ( RawDataBuffer, SmpNbAcquired.value,  ct.byref(ValidSmpNb),  0,  1 )
                GlobalValidSmpNb = np.append(GlobalValidSmpNb,ValidSmpNb)
                
            # run is finished, closing the ni 6562 board
            PM0D._PM0D__FStopRun()
            VIntFuncResult = MSIS0LV.Close_hdsio(StatusBuffer, ct.byref(Result),StatusBufferLength)
            if  (VIntFuncResult < 0 ):
                print('Close_hdsio FAILED')
                self.logger.error('Close_hdsio failed :%s, status :%d', StatusBuffer.value,Result.value)
                return -1,GlobalValidSmpNb
            else :
                self.logger.info('Close_hdsio successfull :%s', StatusBuffer.value)
                print('Close_hdsio successfull')
            return 0,GlobalValidSmpNb
            
        elif GetDataBack == 1 :
            self.logger.info('Acquisition with return of data and data saving')
            for VLoop in range( TotalAcqNb ) :
                if verbose == 1:
                    print ("Acq No:{:d} out of {:d}".format(VLoop,TotalAcqNb))
                # Read the memory of the last frames
                VResult = MSIS0LV.Read_Waveform_ext( Result, ct.byref(SmpNbAcquired), RawDataBuffer, StatusBuffer, DataBufferLength, StatusBufferLength)
                # save the current acq with the mimosis0 dll
                PM0D._PM0D__FAcqRetData ( RawDataBuffer, SmpNbAcquired.value, DataBuffer,ct.byref(ValidSmpNb), 0, 1 )
                GlobalValidSmpNb = np.append(GlobalValidSmpNb,ValidSmpNb)
                BufferArray = np.ndarray(shape=(self.VGFrameNbByAcq,self.VGFrameLength),dtype=np.ushort,buffer=DataBuffer)
                if VLoop == 0:
                    GlobalBufferArray = np.copy(BufferArray)
                else:
                    GlobalBufferArray = np.concatenate((GlobalBufferArray,BufferArray),axis=0)            
                #self.logger.info('Iteration:{:d} array shape :{} '.format(VLoop, np.shape(GlobalBufferArray)))
                #self.logger.info(GlobalBufferArray)
            
            # run is finished, closing the ni 6562 board
            PM0D._PM0D__FStopRun()
            
            VIntFuncResult = MSIS0LV.Close_hdsio(StatusBuffer, ct.byref(Result),StatusBufferLength)
            if  (VIntFuncResult < 0 ):
                print('Close_hdsio FAILED')
                self.logger.error('Close_hdsio failed :%s, status :%d', StatusBuffer.value,Result.value)
                return -1,GlobalValidSmpNb,GlobalBufferArray
            else :
                self.logger.info('Close_hdsio successfull :%s', StatusBuffer.value)
                print('Close_hdsio successfull')
            
            return 0,GlobalValidSmpNb,GlobalBufferArray
        elif GetDataBack == 2 :
            self.logger.info('Acquisition with return of data')
            for VLoop in range( TotalAcqNb ) :
                if verbose == 1:
                    print ("Acq No:{:d} out of {:d}".format(VLoop,TotalAcqNb))
                # Read the memory of the last frames
                VResult = MSIS0LV.Read_Waveform_ext( Result, ct.byref(SmpNbAcquired), RawDataBuffer, StatusBuffer, DataBufferLength, StatusBufferLength)
                
                # save the current acq with the mimosis0 dll
                PM0D._PM0D__FAcqRetDataNoSaving ( RawDataBuffer, SmpNbAcquired.value, DataBuffer,ct.byref(ValidSmpNb), 0, 1 )
                GlobalValidSmpNb = np.append(GlobalValidSmpNb,ValidSmpNb)
                
                BufferArray = np.ndarray(shape=(self.VGFrameNbByAcq,self.VGFrameLength),dtype=np.ushort,buffer=DataBuffer)
                if VLoop == 0:
                    GlobalBufferArray = np.copy(BufferArray)
                else:
                    GlobalBufferArray = np.concatenate((GlobalBufferArray,BufferArray),axis=0)            
                    self.logger.info('Iteration:{:d} array shape :{} '.format(VLoop, np.shape(GlobalBufferArray)))
                    
            # run is finished, closing the ni 6562 board
            PM0D._PM0D__FStopRun()
            
            VIntFuncResult = MSIS0LV.Close_hdsio(StatusBuffer, ct.byref(Result),StatusBufferLength)
            if  (VIntFuncResult < 0 ):
                print('Close_hdsio FAILED')
                self.logger.error('Close_hdsio failed :%s, status :%d', StatusBuffer.value,Result.value)
                return -1,GlobalValidSmpNb,GlobalBufferArray
            else :
                self.logger.info('Close_hdsio successfull :%s', StatusBuffer.value)
                print('Close_hdsio successfull')
            
            return 0,GlobalValidSmpNb,GlobalBufferArray
        elif GetDataBack == 3 :
            for VLoop in range( TotalAcqNb ) :
                if verbose == 1:
                    print ("Acq No:{:d} out of {:d}".format(VLoop,TotalAcqNb))
                # save the current acq with the mimosis0 dll
                PM0D._PM0D__FAcqEmulData ( RawDataBuffer, SmpNbAcquired.value,  ct.byref(ValidSmpNb),  0, 0,   1 )
                
                GlobalValidSmpNb = np.append(GlobalValidSmpNb,ValidSmpNb)
                
            PM0D._PM0D__FStopRun()
            # run is finished, closing the ni 6562 board
            VIntFuncResult = MSIS0LV.Close_hdsio(StatusBuffer, ct.byref(Result),StatusBufferLength)
            if  (VIntFuncResult < 0 ):
                print('Close_hdsio FAILED')
                self.logger.error('Close_hdsio failed :%s, status :%d', StatusBuffer.value,Result.value)
                return -1
            else :
                self.logger.info('Close_hdsio successfull :%s', StatusBuffer.value)
                print('Close_hdsio successfull')
            return 0,GlobalValidSmpNb    


    def  GenerateHeaderDataCSVFiles(self,FilePath,Prefix,RunNo,OneFileByAcq):
        '''
        ...
        
        Generates CSV files with the header and data 
        
        Param
        - FilePath : Path to the directory in which the data file is saved
        - RunNo : Number of the run
        - Prefix : Prefix
        - OneFileByAcq : if 1 : generates one data file per Acquisition
                         if 0 : generates only one data file for the whole run
        
        
        Returns
        - result of the fonction : 0 : successfull / negative number : failed
        
        24/10/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI
        
        '''
        
        VErr = DataReading.Generates_data_header_CSV(FilePath,Prefix,RunNo,OneFileByAcq)
        VStatus = "Generates_data_header_CSV done - result = {:d}".format ( VErr)
        if (VErr >= 0):
            self.logger.info(VStatus)
        else:
            self.logger.error(VStatus)
        return VErr


    def PrintDataFromFile(self, FilePath,Prefix,RunNo,PrintFormat):
        '''
        ...
        
        Print the data stored in a file into the console
        
        Param
        - FilePath : Path to the directory in which the data file is saved
        - RunNo : Number of the run
        - Prefix : Prefix
        
        
        Returns
        - result of the fonction : 0 : successfull / negative number : failed
        
        24/10/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI
        
        '''
        
        Tn2DshortArray = ct.c_ushort * self.VGMaxDataBufferSize # Creates the type : array of 16 bits words with a size of VGMaxDataBufferSize
        DataBuffer = Tn2DshortArray()
        VFrameSize = ct.c_int(0)
        VTotalFrameNb = ct.c_int(0)
        
        VErr = PM0D._PM0D__FGetDataFromFile(DataBuffer,FilePath.encode(),Prefix.encode(),RunNo,ct.byref(VFrameSize),ct.byref(VTotalFrameNb),0)
        self.logger.info('Frame size :{:d}    /     TotalFrameNb :{:d}'.format(VFrameSize.value,VTotalFrameNb.value))
        VStatus = "_PM0D__FGetDataFromFile done - result = {:d}".format ( VErr)
        BufferArray = np.ndarray(shape=(VTotalFrameNb.value,VFrameSize.value),dtype=np.ushort,buffer=DataBuffer)
        if PrintFormat == 1:
            DataReading.FPrintFrameListFromBuffer(BufferArray, VFrameSize.value, VTotalFrameNb.value)
        elif PrintFormat == 2:
            DataReading.FPrintFrameListFromBufferCoords(BufferArray, VFrameSize.value, VTotalFrameNb.value)
        
        if (VErr >= 0):
            self.logger.info(VStatus)
        else:
            self.logger.error(VStatus)
        return VErr


    def PlotDataFromFile(self, FilePath,FilePrefix,RunNb,PlotType) :
        '''
        ...
        
        Plot the data stored in a file in a matplotlib plot
        
        Param
        - FilePath : Path to the directory in which the data file is saved
        - RunNo : Number of the run
        - FilePrefix : Prefix
        
        
        Returns
        - result of the fonction : 0 : successfull / negative number : failed
        
        24/10/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI
        
        '''
        
        self.VGFrameToPlot.value = -1
        
        Tn2DshortArray = ct.c_ushort * self.VGMaxDataBufferSize # Creates the type : array of 16 bits words with a size of VGMaxDataBufferSize
        DataBuffer = Tn2DshortArray()
        
        VFrameSize = ct.c_int(0)
        VTotalFrameNb = ct.c_int(0)
        
        
        VErr = PM0D._PM0D__FGetDataFromFile(DataBuffer,FilePath.encode(),FilePrefix.encode(),RunNb,ct.byref(VFrameSize),ct.byref(VTotalFrameNb),0)
        if VErr < 0 :
            self.logger.error("Error while reading file :{}".format(VErr))
        self.logger.info('Frame size :{:d}    /     TotalFrameNb :{:d}'.format(VFrameSize.value,VTotalFrameNb.value))
        VStatus = "_PM0D__FGetDataFromFile done - result = {:d}".format ( VErr)
        BufferArray = np.ndarray(shape=(VTotalFrameNb.value,VFrameSize.value),dtype=np.ushort,buffer=DataBuffer)
        MatrixToPlot = DataReading.FCreateMatrixFromBuffer(BufferArray,VTotalFrameNb.value, VFrameSize.value, self.VGFrameToPlot.value)
        
        MPlot.PlotMatrix (MatrixToPlot,PlotType)  


    def PlotDataFromBuffer(self, DataBuffer,PlotType) :
        '''
        ...
        
        Plot the data stored in a file in a matplotlib plot
        
        Param
        - DataBuffer : Buffer to be plot
        
        
        Returns
        - result of the fonction : 0 : successfull / negative number : failed
        
        24/10/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI
        
        '''
        
        self.VGFrameToPlot.value = -1
        
        #Tn2DshortArray = ct.c_ushort * self.VGMaxDataBufferSize # Creates the type : array of 16 bits words with a size of VGMaxDataBufferSize
        #DataBuffer = Tn2DshortArray()
        
        VFrameSize = ct.c_int(0)
        VTotalFrameNb = ct.c_int(0)
        VFrameSize.value = self.VGFrameLength
        VTotalFrameNb.value = self.VGTotalFrameNb
        BufferArray = np.ndarray(shape=(VTotalFrameNb.value,VFrameSize.value),dtype=np.ushort,buffer=DataBuffer)
        MatrixToPlot = DataReading.FCreateMatrixFromBuffer(BufferArray,VTotalFrameNb.value, VFrameSize.value, self.VGFrameToPlot.value)
        
        MPlot.PlotMatrix (MatrixToPlot,PlotType)  



    def GetNormalisedDataFromFile(self, FilePath,FilePrefix,RunNb,WriteFile) :
        '''
        ...
        
        Get the data stored in a file generates a file with the normalised data for each pixel
        
        Param
        - FilePath : Path to the directory in which the data file is saved
        - RunNo : Number of the run
        - FilePrefix : Prefix
        - WriteFile : if 0 : do not write data into file
                         1 : write whole matrix into file
                         2 : write only touched pixels into file
        
        Returns
        - result of the fonction : 0 : successfull / negative number : failed
        
        24/10/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI
        
        '''
        self.logger.info('GetNormalisedDataFromFile started,WriteFile:{}'.format(WriteFile))
        VPixelList = []
        
        self.VGFrameToPlot.value = -1
        Tn2DshortArray = ct.c_ushort * self.VGMaxDataBufferSize # Creates the type : array of 16 bits words with a size of VGMaxDataBufferSize
        DataBuffer = Tn2DshortArray()
        
        VFrameSize = ct.c_int(0)
        VTotalFrameNb = ct.c_int(0)
        
        VErr = PM0D._PM0D__FGetDataFromFile(DataBuffer,FilePath.encode(),FilePrefix.encode(),RunNb,ct.byref(VFrameSize),ct.byref(VTotalFrameNb),0)
        if VErr < 0:
            self.logger.error('Error in data file reading :{:d}'.format(VErr))
        
        self.logger.info('Frame size :{:d}    /     TotalFrameNb :{:d}'.format(VFrameSize.value,VTotalFrameNb.value))
        VStatus = "_PM0D__FGetDataFromFile done - result = {:d}".format ( VErr)
        BufferArray = np.ndarray(shape=(VTotalFrameNb.value,VFrameSize.value),dtype=np.ushort,buffer=DataBuffer)
        FullMatrix = DataReading.FCreateMatrixFromBuffer(BufferArray,VTotalFrameNb.value, VFrameSize.value, self.VGFrameToPlot.value)
        self.logger.info('FullMatrix {}'.format(FullMatrix.shape))
        NormMatrix = (FullMatrix.sum(2))/VTotalFrameNb.value
        self.logger.info('NormMatrix {}'.format(NormMatrix.shape))
        # convert Matrix to text
        TextMatrix = ""
        RowNb = NormMatrix.shape[0]
        ColNb = NormMatrix.shape[1]
        self.logger.info('RowNb {} /  ColNb {}'.format(RowNb,ColNb))
        for Row in range (RowNb):
            for Col in range (ColNb):
                if (WriteFile == 0):
                    #No  file saving : only print touched pixels in logging
                    if (NormMatrix[Row,Col]> 0.0):
                        self.logger.info('W0: Row {} ,  Col {}  value :{}'.format(Row,Col,NormMatrix[Row,Col]))
                        if [Row,Col] not in VPixelList:
                            VPixelList.append([Row,Col])
                elif (WriteFile == 1):
                        #save text to file : all matrix
                        TextMatrix += str(Row) + ' ; ' + str(Col) + ' ; ' + str(NormMatrix[Row,Col]) + '\n' 
                        if (NormMatrix[Row,Col]> 0.0):
                            self.logger.info('W1: Row {} ,  Col {}  value :{}'.format(Row,Col,NormMatrix[Row,Col]))
                            if [Row,Col] not in VPixelList:
                                VPixelList.append([Row,Col])
                elif (WriteFile == 2):
                        #save text to file : only  touched pixels 
                        if (NormMatrix[Row,Col] > 0.0):
                            TextMatrix += str(Row) + ' ; ' + str(Col) + ' ; ' + str(NormMatrix[Row,Col]) + '\n' 
                            self.logger.info('W2: Row {} ,  Col {}  value :{}'.format(Row,Col,NormMatrix[Row,Col]))
                            if [Row,Col] not in VPixelList:
                                VPixelList.append([Row,Col])
        if (WriteFile != 0):
            FileName = FilePath+'/'+FilePrefix+str(RunNb)+ 'Norm' +".txt"
            self.logger.info(FileName)
            self.logger.info('TextMatrix:{}'.format(TextMatrix))
            fichier = open(FileName, "w", encoding = "utf8")
            #fichier.write(str(TextMatrix))
            fichier.write(TextMatrix)
            fichier.close()
            
        return NormMatrix,VPixelList


    def SCurveTakeOneStep(self,FilePath,RunNo,Prefix,FrameLength):
        '''
        ...
        
        Take one step of acquisition in order to make SCurve of discriminators
        
        Param
        - FilePath : Path to the directory in which the data file is saved
        - RunNo : Number of the run
        - FilePrefix : Prefix
        - FrameLength : size of the frame
        
        
        Returns
        - result of the fonction : 0 : successfull / negative number : failed
        
        24/10/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI
        
        '''
        VPixelList = []
        # change filename
        VResult = self.SetSaveFileName(FilePath,RunNo,Prefix)
        if VResult < 0 :
            self.logger.error('Error while changing the save file name:{}'.format(VResult))
        else:
            # start run
            self.logger.info('File name changed, starting run')
            VResult = self.Start_Run(ClockRate=20000000.0,DataRate=1,SamplingEdge=18,FrameLength=FrameLength,FrameNbByAcq=100,TotalFrameNb=1000)
            if VResult < 0 :
                self.logger.error('Error while starting the run:{}'.format(VResult))
            else:
                self.logger.info('Run started, acquisition polling')
                # Acq polling
                ## VResult,GlobalValidSmpNb = self.Acq_Polling( GetDataBack = 0, verbose = 0) # previous 10.01.2023
                VResult,GlobalValidSmpNb,GlobalBufferArray = self.Acq_Polling( GetDataBack = 2, verbose = 0) 
                if VResult < 0 :
                    self.logger.error('Error while starting the run:{}'.format(VResult))
                else:
                    # get norm data from file
                    self.logger.info('Acquisition completed, getting normalised data')
                    NormMatrix,VPixelList = self.GetNormalisedDataFromFile(FilePath,Prefix,RunNo,WriteFile = 2)
                    
        return VResult,VPixelList


