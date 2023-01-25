#!/usr/bin/python
# -*- coding: utf-8 -*-
"""  @file dll_wrapper.py

  Wrapper for the Cfunctions of the Msis0_LV_DLL
  
"""
# import ctypes for the function calls of the DLL
import ctypes as ct

import os

##  DirPath : absolute path to the working directory
DirPath = os.path.abspath('')
## DllFullName : Full path for the SSCI dll
DllFullName = os.path.join(DirPath, 'DLL\Msis0_LV_dll.dll')

# load the library
## @brief VLib : Reference to the library
try:
    VLib = ct.cdll.LoadLibrary (DllFullName) 
except :
    print("failed to load library:{}".format(DllFullName))
    

# Define functions paramters list and returned type

#int32_t __cdecl Close_hdsio(char StatusString[], int8_t *StatusBool, int32_t len)
VLib.Close_hdsio.argtypes = [ ct.POINTER (ct.c_char),ct.POINTER (ct.c_ubyte),ct.c_int]
VLib.Close_hdsio.restype = ct.c_int

#void __cdecl GetPXI6562SlotNoAndName(int32_t *Slot_Number, char BoardName[], int32_t len);
VLib.GetPXI6562SlotNoAndName.argtypes = [ ct.POINTER (ct.c_int),ct.POINTER (ct.c_char),ct.c_int]

#int32_t __cdecl Read_Waveform(uint16_t DataRate,  int8_t *Conf_status, int32_t *SmpNbAcquiredAcq, uint16_t data[], char Result_string[], int32_t len, int32_t len2);
VLib.Read_Waveform.argtypes = [ ct.c_ushort, ct.POINTER (ct.c_ubyte),ct.POINTER (ct.c_int),ct.POINTER (ct.c_ushort),ct.POINTER (ct.c_char),ct.c_int,ct.c_int]
VLib.Read_Waveform.restype = ct.c_int

#int32_t __cdecl Start_acq(double ClockRate, int32_t DataRate, uint16_t SamplingEdge, int32_t FrameLength, int32_t FrameNrByAcq, char ResourceName[], char ConfBoardStatus[],  int32_t *SmpNbAcquiredAcq, LVBoolean *Status, int32_t len);
VLib.Start_acq.argtypes = [ ct.c_double,ct.c_int,ct.c_ushort,ct.c_int,ct.c_int,ct.c_char_p,ct.POINTER (ct.c_char), ct.POINTER (ct.c_int),ct.POINTER (ct.c_ubyte),ct.c_int]
VLib.Start_acq.restype = ct.c_int

#int32_t Read_Waveform_ext( LVBoolean *Conf_status, int32_t *SmpNbAcquiredAcq, uint16_t data[], char Result_string[], int32_t len, int32_t len2)
VLib.Read_Waveform_ext.argtypes = [ ct.POINTER (ct.c_ubyte),ct.POINTER (ct.c_int),ct.POINTER (ct.c_ushort),ct.POINTER (ct.c_char),ct.c_int,ct.c_int]
VLib.Read_Waveform_ext.restype = ct.c_int

#int32_t Start_acq_ext(double ClockRate, int32_t DataRate, uint16_t SamplingEdge, int32_t FrameLength, int32_t FrameNrByAcq, char ConfBoardStatus[], int32_t *SmpNbAcquiredAcq, int8_t *Status, int32_t len)
VLib.Start_acq_ext.argtypes = [ ct.c_double,ct.c_int,ct.c_ushort,ct.c_int,ct.c_int,ct.POINTER (ct.c_char), ct.POINTER (ct.c_int),ct.POINTER (ct.c_ubyte),ct.c_int]
VLib.Start_acq_ext.restype = ct.c_int

#void GetGlobalVar(int8_t *Instrument_initialized, int32_t *Numeric)
VLib.GetGlobalVar.argtypes =[ ct.POINTER (ct.c_byte),ct.POINTER (ct.c_int)]