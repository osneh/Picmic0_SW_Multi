#!/usr/bin/python
# -*- coding: utf-8 -*-
"""  @file dll_wrapper.py

  Wrapper for the Cfunctions of the picmic0_data_DLL
  
"""
# import ctypes for the function calls of the DLL
import ctypes as ct

import os

##  DirPath : absolute path to the working directory
DirPath = os.path.abspath('')
## DllFullName : Full path for the SSCI dll
DllFullName = os.path.join(DirPath, 'DLL\picmic0_data_dll.dll')

# load the library
## @brief VLib : Reference to the library
try:
    VLib = ct.cdll.LoadLibrary (DllFullName) 
except :
    print("failed to load library:{}".format(DllFullName))
    

# Define functions paramters list and returned type


# SInt32 PM0D__FBegin ( SInt8 ErrLogLvl, char* ErrFile, SInt8 MsgLogLvl, char* MsgFile )
VLib._PM0D__FBegin.argtypes = [ ct.c_byte, ct.c_char_p,ct.c_byte, ct.c_char_p]
VLib._PM0D__FBegin.restype = ct.c_int

# SInt32 PM0D__FEnd ()
VLib._PM0D__FEnd.restype = ct.c_int

# SInt32 PM0D__FSetErrorLogLevel ( SInt8 Level );)
VLib._PM0D__FSetErrorLogLevel.argtypes = [ ct.c_byte]
VLib._PM0D__FSetErrorLogLevel.restype =  ct.c_byte
# SInt32 PM0D__FSetMsgLogLevel ( SInt8 Level );)
VLib._PM0D__FSetMsgLogLevel.argtypes = [ ct.c_byte]
VLib._PM0D__FSetMsgLogLevel.restype =  ct.c_byte


# SInt32 PM0D__FPrintFrame (  SInt32 FrameNo, SInt32 Verbose );)
VLib._PM0D__FPrintFrame.argtypes = [ ct.c_int, ct.c_int ]
VLib._PM0D__FPrintFrame.restype = ct.c_int

# SInt32 PM0D__FAcq ( UInt16* PtSrcW16, SInt32 EltNb, SInt32 * AcqStatus, SInt8 TrigStatus, SInt32 Verbose );)
VLib._PM0D__FAcq.argtypes = [ ct.POINTER (ct.c_ushort), ct.c_int,ct.POINTER(ct.c_int), ct.c_byte,ct.c_int]
VLib._PM0D__FAcq.restype = ct.c_int

# SInt32 PM0D__FAcqRetData ( UInt16* PtSrcW16, SInt32 EltNb, UInt16 * PtDataW16,SInt32 * AcqStatus, SInt8 TrigStatus, SInt32 Verbose );)
VLib._PM0D__FAcqRetData.argtypes = [ ct.POINTER (ct.c_ushort), ct.c_int,ct.POINTER (ct.c_ushort), ct.POINTER(ct.c_int), ct.c_byte,ct.c_int]
VLib._PM0D__FAcqRetData.restype = ct.c_int

#SInt32 PM0D__FAcqEmulData ( UInt16* PtSrcW16, SInt32 EltNb, SInt32 * AcqStatus, SInt8 TrigStatus, SInt32 EmulationFonction, SInt32 Verbose )
VLib._PM0D__FAcqEmulData.argtypes = [ ct.POINTER (ct.c_ushort), ct.c_int, ct.POINTER(ct.c_int), ct.c_byte,ct.c_int,ct.c_int]
VLib._PM0D__FAcqEmulData.restype = ct.c_int

#SInt32 PM0D__FAcqRetDataNoSaving ( UInt16* PtSrcW16, SInt32 EltNb, UInt16 * PtDataW16,SInt32 * AcqStatus, SInt8 TrigStatus, SInt32 Verbose )
VLib._PM0D__FAcqRetDataNoSaving.argtypes = [ ct.POINTER (ct.c_ushort), ct.c_int,ct.POINTER (ct.c_ushort), ct.POINTER(ct.c_int), ct.c_byte,ct.c_int]
VLib._PM0D__FAcqRetDataNoSaving.restype = ct.c_int


# SInt32 PM0D__FStartRun (SInt32 TotalFrameNumber,SInt32 FrameNbByAcq, UInt16 FrameLength, UInt16 MaxFrameSize, UInt16 Flush,  double ClockFreq  );)
VLib._PM0D__FStartRun.argtypes = [  ct.c_int,ct.c_int,ct.c_ushort, ct.c_ushort,ct.c_ushort,ct.c_double]
VLib._PM0D__FStartRun.restype = ct.c_int

# SInt32 PM0D__FStopRun (  );)
VLib._PM0D__FStopRun.restype = ct.c_int


# SInt32 PM0D__FSetFileSaveFile (   char *  VRunDir, char * VFileNamePrefix, SInt32 VRunNo );)
VLib._PM0D__FSetFileSaveFile.argtypes = [ ct.c_char_p, ct.c_char_p,ct.c_int]
VLib._PM0D__FSetFileSaveFile.restype = ct.c_int

# SInt32 PM0D__FLoadRunFile (SInt32 VAcqNo, char *  VRunDir, char * VFileNamePrefix, SInt32 VRunNo );)
VLib._PM0D__FLoadRunFile.argtypes = [ ct.c_int,ct.c_char_p, ct.c_char_p,ct.c_int]
VLib._PM0D__FLoadRunFile.restype = ct.c_int

# SInt32 PM0D__FReadRunBlock (void);)
VLib._PM0D__FLoadRunFile.restype = ct.c_int

# SInt32 PM0D__FCloseRunFile ( );)
VLib._PM0D__FCloseRunFile.restype = ct.c_int

#SInt32 PM0D__FSaveCSVHeaderFile ( char *  VRunDir, char * VFileNamePrefix, SInt32 VRunNo )
VLib._PM0D__FSaveCSVHeaderFile.argtypes = [ ct.c_char_p, ct.c_char_p,ct.c_int]
VLib._PM0D__FSaveCSVHeaderFile.restype = ct.c_int

#SInt32 PM0D__FSaveCSVDataFile ( char *  VRunDir, char * VFileNamePrefix, SInt32 VRunNo, SInt32 OneFileByAcq )
VLib._PM0D__FSaveCSVDataFile.argtypes = [ ct.c_char_p, ct.c_char_p,ct.c_int, ct.c_int]
VLib._PM0D__FSaveCSVDataFile.restype = ct.c_int

# SInt32 PM0D__FGetDataFromFile ( UInt16* PtDataW16,  char *  VRunDir, char * VFileNamePrefix, SInt32 VRunNo, SInt32 *  framesize, SInt32 * TotalFrmNb,  SInt32 Verbose )
VLib._PM0D__FGetDataFromFile.argtypes = [ ct.POINTER (ct.c_ushort),ct.c_char_p, ct.c_char_p,ct.c_int, ct.c_void_p,ct.c_void_p, ct.c_int]
VLib._PM0D__FGetDataFromFile.restype = ct.c_int
