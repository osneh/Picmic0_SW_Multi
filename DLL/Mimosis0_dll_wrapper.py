#!/usr/bin/python
# -*- coding: utf-8 -*-
"""  @file dll_wrapper.py

  Wrapper for the Cfunctions of the mimosis0_DLL
  
"""
# import ctypes for the function calls of the DLL
import ctypes as ct

import os

##  DirPath : absolute path to the working directory
DirPath = os.path.abspath('')
## DllFullName : Full path for the SSCI dll
DllFullName = os.path.join(DirPath, 'DLL\mimosis0_dll.dll')

# load the library
## @brief VLib : Reference to the library
try:
    VLib = ct.cdll.LoadLibrary (DllFullName) 
except :
    print("failed to load library:{}".format(DllFullName))
    

# Define functions paramters list and returned type


# SInt32 MIMOSIS0__FBegin ( SInt8 EnableErrorLog, char* ErrorLogFile, SInt8 EnableMsgLog, char* MsgLogFile );)
VLib._MIMOSIS0__FBegin.argtypes = [ ct.c_byte, ct.c_char_p,ct.c_byte, ct.c_char_p]
VLib._MIMOSIS0__FBegin.restype = ct.c_int

# SInt32 MIMOSIS0__FEnd ();)
VLib._MIMOSIS0__FEnd.restype = ct.c_int

# SInt32 MIMOSIS0__FPrintFrame (  SInt32 FrameNo, SInt32 Verbose );)
VLib._MIMOSIS0__FPrintFrame.argtypes = [ ct.c_int, ct.c_int ]
VLib._MIMOSIS0__FPrintFrame.restype = ct.c_int

# SInt32 MIMOSIS0__FAcq ( UInt16* PtSrcW16, SInt32 EltNb, SInt32 * AcqStatus, SInt8 TrigStatus, SInt32 Verbose );)
VLib._MIMOSIS0__FAcq.argtypes = [ ct.POINTER (ct.c_ushort), ct.c_int,ct.POINTER(ct.c_int), ct.c_byte,ct.c_int]
VLib._MIMOSIS0__FAcq.restype = ct.c_int

# SInt32 MIMOSIS0__FAcqRetData ( UInt16* PtSrcW16, SInt32 EltNb, UInt16 * PtDataW16,SInt32 * AcqStatus, SInt8 TrigStatus, SInt32 Verbose );)
VLib._MIMOSIS0__FAcqRetData.argtypes = [ ct.POINTER (ct.c_ushort), ct.c_int,ct.POINTER (ct.c_ushort), ct.POINTER(ct.c_int), ct.c_byte,ct.c_int]
VLib._MIMOSIS0__FAcqRetData.restype = ct.c_int

#SInt32 MIMOSIS0__FAcqEmulData ( UInt16* PtSrcW16, SInt32 EltNb, SInt32 * AcqStatus, SInt8 TrigStatus, SInt32 EmulationFonction, SInt32 Verbose )
VLib._MIMOSIS0__FAcqEmulData.argtypes = [ ct.POINTER (ct.c_ushort), ct.c_int, ct.POINTER(ct.c_int), ct.c_byte,ct.c_int,ct.c_int]
VLib._MIMOSIS0__FAcqEmulData.restype = ct.c_int

#SInt32 MIMOSIS0__FAcqRetDataNoSaving ( UInt16* PtSrcW16, SInt32 EltNb, UInt16 * PtDataW16,SInt32 * AcqStatus, SInt8 TrigStatus, SInt32 Verbose )
VLib._MIMOSIS0__FAcqRetDataNoSaving.argtypes = [ ct.POINTER (ct.c_ushort), ct.c_int,ct.POINTER (ct.c_ushort), ct.POINTER(ct.c_int), ct.c_byte,ct.c_int]
VLib._MIMOSIS0__FAcqRetDataNoSaving.restype = ct.c_int

# SInt32 MIMOSIS0__FPollAcqRqEv ();)
VLib._MIMOSIS0__FPollAcqRqEv.restype = ct.c_int

# SInt32 MIMOSIS0__FStartRun (SInt32 TotalFrameNumber,SInt32 FrameNbByAcq, UInt16 FrameLength, UInt16 MaxFrameSize, UInt16 Flush,  double ClockFreq  );)
VLib._MIMOSIS0__FStartRun.argtypes = [  ct.c_int,ct.c_int,ct.c_ushort, ct.c_ushort,ct.c_ushort,ct.c_double]
VLib._MIMOSIS0__FStartRun.restype = ct.c_int

# SInt32 MIMOSIS0__FStopRun (  );)
VLib._MIMOSIS0__FStopRun.restype = ct.c_int

# SInt32 MIMOSIS0__FSetErrorLogLevel ( SInt8 Level );)
VLib._MIMOSIS0__FSetErrorLogLevel.argtypes = [ ct.c_byte ]
VLib._MIMOSIS0__FSetErrorLogLevel.restype = ct.c_int

# SInt32 MIMOSIS0__FSetMsgLogLevel ( SInt8 Level );)
VLib._MIMOSIS0__FSetMsgLogLevel.argtypes = [ ct.c_byte ]
VLib._MIMOSIS0__FSetMsgLogLevel.restype = ct.c_int

# SInt32 MIMOSIS0__FGetRealFrameLength ( SInt8 FrameNo );)
VLib._MIMOSIS0__FGetRealFrameLength.argtypes = [ ct.c_byte ]
VLib._MIMOSIS0__FGetRealFrameLength.restype = ct.c_int

# SInt32 MIMOSIS0__FSetFileSaveFile (   char *  VRunDir, char * VFileNamePrefix, SInt32 VRunNo );)
VLib._MIMOSIS0__FSetFileSaveFile.argtypes = [ ct.c_char_p, ct.c_char_p,ct.c_int]
VLib._MIMOSIS0__FSetFileSaveFile.restype = ct.c_int

# SInt32 MIMOSIS0__FLoadRunFile (SInt32 VAcqNo, char *  VRunDir, char * VFileNamePrefix, SInt32 VRunNo );)
VLib._MIMOSIS0__FLoadRunFile.argtypes = [ ct.c_int,ct.c_char_p, ct.c_char_p,ct.c_int]
VLib._MIMOSIS0__FLoadRunFile.restype = ct.c_int

# SInt32 MIMOSIS0__FReadRunBlock (void);)
VLib._MIMOSIS0__FLoadRunFile.restype = ct.c_int

# SInt32 MIMOSIS0__FCloseRunFile ( );)
VLib._MIMOSIS0__FCloseRunFile.restype = ct.c_int

#SInt32 MIMOSIS0__FSaveCSVHeaderFile ( char *  VRunDir, char * VFileNamePrefix, SInt32 VRunNo )
VLib._MIMOSIS0__FSaveCSVHeaderFile.argtypes = [ ct.c_char_p, ct.c_char_p,ct.c_int]
VLib._MIMOSIS0__FSaveCSVHeaderFile.restype = ct.c_int

#SInt32 MIMOSIS0__FSaveCSVDataFile ( char *  VRunDir, char * VFileNamePrefix, SInt32 VRunNo, SInt32 OneFileByAcq )
VLib._MIMOSIS0__FSaveCSVDataFile.argtypes = [ ct.c_char_p, ct.c_char_p,ct.c_int, ct.c_int]
VLib._MIMOSIS0__FSaveCSVDataFile.restype = ct.c_int

#SInt32 MIMOSIS0__FSetChipForAcq ( SInt32 ChipSel )
VLib._MIMOSIS0__FSetChipForAcq.argtypes = [ ct.c_int ]
VLib._MIMOSIS0__FSetChipForAcq.restype = ct.c_int



# SInt32 MIMOSIS0__FGetDataFromFile ( UInt16* PtDataW16,  char *  VRunDir, char * VFileNamePrefix, SInt32 VRunNo, SInt32 *  framesize, SInt32 * TotalFrmNb,  SInt32 Verbose )
VLib._MIMOSIS0__FGetDataFromFile.argtypes = [ ct.POINTER (ct.c_ushort),ct.c_char_p, ct.c_char_p,ct.c_int, ct.c_void_p,ct.c_void_p, ct.c_int]
VLib._MIMOSIS0__FGetDataFromFile.restype = ct.c_int