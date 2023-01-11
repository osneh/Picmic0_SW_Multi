#!/usr/bin/python
# -*- coding: utf-8 -*-
"""  @DataReading.py

  Module for the file reading for data acquisition
  
"""
import logging
import numpy as np
## DLL Modules inclusion
from DLL.Mimosis0_dll_wrapper import VLib as MSIS0  # wrapper for the functions of the Mimosis0_dll.dll 


ErrFileFullName = "c:\\tmp\\log\\Msis0_DAQ_err_log.txt"
ErrLogLevel = 1
MsgFileFullName ="c:\\tmp\\log\\Msis0_DAQ_msg_log.txt"
MsgLogLevel = 1

## int: Result of the SSCI_FBegin function
VIntFuncResult = MSIS0._MIMOSIS0__FBegin(ErrLogLevel, ErrFileFullName.encode (),MsgLogLevel,MsgFileFullName.encode ())




def Generates_data_header_CSV(FilePath,Prefix,RunNo,OneFileByAcq):
    '''
    ...
    
    Read the binary save file, and generates a header and a data file in CSV format
    
    Param
    - FilePath : Path to the directory in which the data file is saved
    - Prefix : Prefix
    - RunNo : Number of the run
    - OneFileByAcq : number of files for the data saving csv file, can be:
        - 0 : one file for the entire run
        - 1 : one file by acquisition
    - VLogger : logger for the logging system
    
    Returns
        - result of the fonction : 0 : successfull / negative number : failed
    
    03/02/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI
    
    '''
    logger = logging.getLogger('datareading')
    
    logger.info('PArams: {:s} / {:s} /{:d}'.format(FilePath,Prefix,RunNo))
    
    #Generates the header file
    VRet = MSIS0._MIMOSIS0__FSaveCSVHeaderFile ( FilePath.encode(), Prefix.encode(), RunNo )
    if VRet < 0:
        logger.error('_MIMOSIS0__FSaveCSVHeaderFile failed, error:  /%d',VRet)
        return VRet
    logger.info('_MIMOSIS0__FSaveCSVHeaderFile successfull')
    
    #Generates the data file
    VRet = MSIS0._MIMOSIS0__FSaveCSVDataFile ( FilePath.encode(), Prefix.encode(), RunNo, OneFileByAcq )
    
    if VRet < 0:
        logger.error('_MIMOSIS0__FSaveCSVDataFile failed, error:  /%d',VRet)
        return VRet
    logger.error('_MIMOSIS0__FSaveCSVDataFile successfull')
    
    return 0


def FPrintFrameListFromBuffer(DataBuffer, VFrameSize, VTotalFrameNb):
    '''
    ...
    
    Print a list of frames from a buffer ( raw buffer)
    
    Param
    - DataBuffer : Array of ctype short ( W16 )
    - VFrameSize : number of elements of a frame65
    - VTotalFrameNb : frame number to be displayed
    
    Returns
        - nothing
    
    03/03/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI
    
    '''
    logger = logging.getLogger('datareading')
    ArraySize = VFrameSize * VTotalFrameNb
    
    logger.info('VFrameSize:{:d},VTotalFrameNb:{:d}'.format(VFrameSize,VTotalFrameNb))
    for FrameIndex in range (VTotalFrameNb):
        FrameList = []
        for VectorIndex in range (VFrameSize):
            FrameList.append(DataBuffer[FrameIndex][VectorIndex])
        logger.info('frame[{:04d}]:{}'.format(FrameIndex,','.join("{:04X}".format(Element) for Element in FrameList)))



def FPrintFrameListFromBufferCoords(DataBuffer, VFrameSize, VTotalFrameNb):
    '''
    ...
    
    Print a list of frames from a buffer ( extracted coords from the raw data)
    
    Param
    - DataBuffer : Array of ctype short ( W16 )
    - VFrameSize : number of elements of a frame
    - VTotalFrameNb : frame number to be displayed
    
    Returns
        - nothing
    
    03/03/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI
    
    '''
    logger = logging.getLogger('datareading')
    ArraySize = VFrameSize * VTotalFrameNb
    
    logger.info('VFrameSize:{:d},VTotalFrameNb:{:d}'.format(VFrameSize,VTotalFrameNb))
    #for FrameIndex in range (VTotalFrameNb):
    if 1==1:
        FrameIndex = 0
        #FrameList = []
        for VectorIndex in range (VFrameSize):
            if (DataBuffer[FrameIndex][VectorIndex] != 0):
                Row = DataBuffer[FrameIndex][VectorIndex] & 0x003F
                Col = (DataBuffer[FrameIndex][VectorIndex] & 0x1FC0)>>6
                logger.info("Frame:{:d}, hit nb:{:d}, col :{:d}, row:{:d}, result:{:d}(d) / {:x} (x)".format(VectorIndex,Col,Row,DataBuffer[FrameIndex][VectorIndex],DataBuffer[FrameIndex][VectorIndex]))
                #FrameList.append("{:d}/{:d}".format(Row,Col))
        #logger.info('frame[{:04d}]:{}'.format(FrameIndex,','.join("{:s}".format(Element) for Element in FrameList)))


def FCreateMatrixFromBuffer(DataBuffer, VTotalFrameNumber, VFrameSize, VFrameNo):
    '''
    ...
    
    Create a matrix from a linear buffer
    
    Param
    - DataBuffer : Array of ctype short ( W16 )
    - VTotalFrameNumber : Total Frame number of run4
    - VFrameSize : number of elements of a frame
    - VFrameNo : frame  to be displayed
    
    Returns
        - matrix : a 128 x 54 array55
    
    03/03/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI

    '''
    logger = logging.getLogger('datareading')
    
    logger.info('VFrameSize:{:d},VFrameNo:{:d}'.format(VFrameSize,VFrameNo))
    if (VFrameNo < 0 ):
        # VFrameNo negative : plot all frames
        Matrix = np.zeros((128,54,VTotalFrameNumber),dtype=int)
        
        for VFrameIndex in range (VTotalFrameNumber):
            for VectorIndex in range (0,VFrameSize):
                if ((DataBuffer[VFrameIndex][VectorIndex]) & 0x8000) != 0:
                    Row = (DataBuffer[VFrameIndex][VectorIndex]) & 0x007F
                    Col = ((DataBuffer[VFrameIndex][VectorIndex]) & 0x1F80)>>7
                    #logger.info(" Vector:{:d} Raw value :{:x}  Row:{:d} / Col:{:d}".format(VectorIndex, DataBuffer[VFrameIndex][VectorIndex],Row,Col))
                    try :
                        Matrix[Row,Col,VFrameIndex] = 1
                    except : 
                        logger.error("trying to write to  Row :{:d} / Col :{:d}".format(Row,Col))
    
    else:
        # VFrameNo positive : plot only one frame
        Matrix = np.zeros((128,54),dtype=int)
        
        for VectorIndex in range (1,VFrameSize):
            if ((DataBuffer[VFrameNo][VectorIndex]) & 0x8000) != 0:
                Row = (DataBuffer[VFrameNo][VectorIndex]) & 0x007F
                Col = ((DataBuffer[VFrameNo][VectorIndex]) & 0x1F80)>>7
                logger.info(" Vector:{:d} Raw value :{:x}  Row:{:d} / Col:{:d}".format(VectorIndex, DataBuffer[VFrameNo][VectorIndex],Row,Col))
                try :
                    Matrix[Row,Col] = 1
                except : 
                    logger.error("trying to write to  Row :{:d} / Col :{:d}".format(Row,Col))
    
    return Matrix

