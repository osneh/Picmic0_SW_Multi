#!/usr/bin/python
# -*- coding: utf-8 -*-
""" 
Module which contains PICMIC 0 slow control registers definition and tools to handle them

It is mainly code conversion from C PICMIC 0 slow control library => X:\lib\com\maps\picmic0\sc

28/12/2021 V00 G.CLAUS CNRS/IN2P3/IPHC/C4PI 
- First implementation  

06/01/2022 V10 G.CLAUS CNRS/IN2P3/IPHC/C4PI
- Add USB deconnect it was not implemeented before (close app to disconnect ;-)

17/01/2022 V11 G.CLAUS CNRS/IN2P3/IPHC/C4PI
- Better errors handling to fix a bugs in application V1.0 => application V1.1

10/02/2022 V20 MS
- Add commands to control signals RST, RST_I2C, START, TESTMODE

03/08/2022 V22 MS
- Add the FResetPixelMatrix function

22/11/2022 V24 MS
- Set the VPrint of the handleIncommingSysEx function to 0 ( disabling the print at each transaction to save time )
- added an optional param to the FConnect function in order to possibly disable the automatic reset of arduino board at connection
- changed the way to import modules to enable one place modification in case of module name change 

16/05/2023 V25 MS
- added the possibility to save the sent registers in a file

Can be loaded as a module under python interpreter and used in interactive mode
python
>>> import module
>>> m = module
>>> m.FPrint ()
>>> m.VInteger
>>> etc ...

Another way to import module 

>>> import module as m
>>> m.FPrint ()
"""



__author__ = "Gilles Claus"
__version__ = '0.2.4'
__maintainer__ = "Matthieu Specht"
__email__ = "matthieu.specht@iphc.cnrs.fr"
__date__ = "2022-11-22"



import sys

from enum import Enum, unique

from pyfirmata import Arduino
import time

#import ctypes as ct
import pyfirmata 

import logging

# ===========================================================================
# Constants
# ===========================================================================


VERSION_DATE = "V{} {}".format(__version__,__date__) # Module version &date


# ===========================================================================
# Enum
# ===========================================================================

#----------------------------------------------
# Registers list
#
# 28/12/2021 G.CLAUS CNRS/IN2P3/IPHC/C4PI
#----------------------------------------------

  # Registers list on 01/12/2021 based on datsheet PICMIC Datasheet.docx from 29/11/2021
  #
  # Index = 0, Name = Global command          , Addr = 0x01, Size =  1 W8, Access W/R
  # Index = 1, Name = Pixel sequence control  , Addr = 0x02, Size = 18 W8, Access W/R
  # Index = 2, Name = Vpulse switch           , Addr = 0x1E, Size =  7 W8, Access W/R
  # Index = 3, Name = Test structure control  , Addr = 0x25, Size =  1 W8, Access W/R
  # Index = 4, Name = DAC values              , Addr = 0x26, Size =  5 W8, Access W/R
  # Index = 7, Name = DAC switches            , Addr = 0x2B, Size =  3 W8, Access W/R
  # Index = 6, Name = DATA emulation          , Addr = 0x3C, Size =  1 W8, Access W/R
  # Index = 7, Name = Pixel config row        , Addr = 0x3D, Size =  1 W8, Access W/R
  # Index = 8, Name = Pixel config col        , Addr = 0x3E, Size =  1 W8, Access W/R
  # Index = 9, Name = Pixel config data       , Addr = 0x3F, Size =  1 W8, Access W/R

@unique
class TRegId (Enum) :

    GLB_CMD         =  0 #  Global command        
    PIX_SEQ         =  1 # Pixel sequence control 
    VPULSE_SW       =  2 # Vpulse switch          
    TEST_S_CTRL     =  3 # Test structure control 
    DAC_VAL         =  4 # DAC values             
    DAC_SW          =  5 # DAC switches           
    DATA_EMUL       =  6 # DATA emulation         
    PIX_CONF_ROW    =  7 # Pixel config row       
    CONF_COL        =  8 # Pixel config col       
    CONF_DATA       =  9 # Pixel config data      

    REG_NB          = 10 # Registers number       


#----------------------------------------------
# Registers access mode
#
# 28/12/2021 G.CLAUS CNRS/IN2P3/IPHC/C4PI
#----------------------------------------------

@unique
class TRegAcc (Enum) :

  NA = 0 # Not available = not implemenetd
  WO = 1 # Write Only
  RO = 2 # read Only
  WR = 3 # Write & read
  NB = 4 # Number of register access mode
  
#----------------------------------------------
# Commands to I2C controller (Arduino DUE)
#
# 27/12/2021 G.CLAUS CNRS/IN2P3/IPHC/C4PI
#----------------------------------------------


@unique
class TCmd (Enum) :

    SET_LOG     = 0 # Sets log level on UC side   
    GET_STATUS  = 1 # Gets status of UC side    
    SET_WR_REG  = 2 # Sets/writes register Mode = SW sets register value in UC register image, Mode = HW sets in image + write to PICMIC, Mode = CHK write, readback, compare 
    GET_RD_REG  = 3 # Gets/reads register  Mode = SW reads register value from UC register image, Mode = HW reads register from PICMIC, update image, Mode = CHK => Idem HW 
    SET_WR_DEF  = 4 # Sets/writes ALL registers default values Mode = SW sets registers value in UC register image, Mode = HW sets in image + write to PICMIC, Mode = CHK write, readback, compare 
    WR_ALL_REG  = 5 # Writes to a PICMIC all registers, if param Mode = CHK write, readback, compare */    
    RD_ALL_REG  = 6 # Reads from PICMIC all registers, if param Mode = CHK => Compare to WR register image (Mode = SW, HW are ignored) 
    CTRL_HW_SIG = 7 # 10/02/22 Control of HW signals RTS, RST_I2C, 
    TEST_I2C_REGS = 8 # 25/07/22 Test a bank of I2C registers
    ACTIVATE_OUTPUTS = 9 # 29/09/22 MS Activate all outputs' I2C and steering)
    DEACTIVATE_OUTPUTS = 10 # 29/09/22 MS Deactivate all outputs' I2C and steering)
    WR_REG_LOW_LEVEL  = 11 # 17/05/2023 MS Writes one register value with its address Low level function
    RD_REG_LOW_LEVEL  = 12 # 17/05/2023 MS Reads one register value with its address Low level function */

    CMD_NB      = 13 # Cmd number



#----------------------------------------------
# Registers access mode
#
# 10/02/2022 G.CLAUS CNRS/IN2P3/IPHC/C4PI
#----------------------------------------------

@unique
class TCmdHwSig (Enum) :

  SET_ST_ALL      = 0 # Sets state of all signals, satates are function paramters RstSt, RstI2CSt, StratSt, TestmodeSt  
  SET_ST_RST      = 1 # Sets state of RST
  SET_ST_RST_I2C  = 2 # Sets state of RST I2C
  SET_ST_START    = 3 # Sets state of START
  SET_ST_TESTMODE = 4 # Sets state of TESTMODE
  PULSE_RST       = 5 # Generates a pulse on RST
  PULSE_RST_I2C   = 6 # Generates a pulse on 
  PULSE_START     = 7 # Generates a pulse on 
  GET_PRINT_ST    = 8 # Gets en prints (on Arduino console) signals state
  NB = 9             # Number of commands - More commands can be added of course
 


#----------------------------------------------
# Register operation mode for I2C controller (Arduino DUE) commands
#
# 28/12/2021 G.CLAUS CNRS/IN2P3/IPHC/C4PI
#----------------------------------------------


@unique
class TRegOp (Enum) :

    SW  = 0   # SET/WR cmd => Writes register to RAM image / GET/RD cmd => Reads register from RAM image => NO I2C access  
    HW  = 1   # SET/WR cmd => Writes register to PICMIC    / GET/RD cmd => Reads register from PICMIC and update RAM image => I2C access 
    CHK = 2   # SET/WR cmd => Write register to PICMIC, reads back ans compare /  GET/RD cmd => Reads register from PICMIC and update RAM image => I2C access 

    NB  = 3   # Operations number   

#----------------------------------------------
# PrePost operation mode for I2C controller (Arduino DUE) commands
#
# 23/02/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI
#----------------------------------------------


@unique
class TPrePostOp (Enum) :

    NONE  = 0   # SET/WR cmd => Writes register to RAM image / GET/RD cmd => Reads register from RAM image => NO I2C access  
    PRERST  = 1   # SET/WR cmd => Writes register to PICMIC    / GET/RD cmd => Reads register from PICMIC and update RAM image => I2C access 
    POSTRETRY = 2   # SET/WR cmd => Write register to PICMIC, reads back ans compare /  GET/RD cmd => Reads register from PICMIC and update RAM image => I2C access 

    NB  = 3   # Operations number   


#----------------------------------------------
# Register default value mode for I2C controller (Arduino DUE) command PM0SC__CMD_SET_WR_DEF
#
# 04/01/2022 G.CLAUS CNRS/IN2P3/IPHC/C4PI
#----------------------------------------------


@unique
class TDefOp (Enum) :

    DEF  = 0   # SET/WR default values from doc, values are hardcoded in Arduino DUE function FPicmicProPcCmd  (...)
    VAL  = 1   # SET/WR a value in ALL registers, this value is passed as param to PM0SC__CMD_SET_WR_DEF command
    
    NB  = 3   # Operations number   


#----------------------------------------------
# USB errors list
#
# 17/01/2022 G.CLAUS CNRS/IN2P3/IPHC/C4PI
#----------------------------------------------


@unique
class TErrUsb (Enum) :

    OK         =  0 # No error
    CONNECT    = -1 # USB connect has failed
    DISCONNECT = -2 # USB disconnect has failed
    
    NB  = 3         # Errors number   







# ===========================================================================
# Global variables used as constants 
# ===========================================================================


MAX_FIRMATA_CMD_BUFF_SZ = 60

MAX_CMD_BUFF_SZ = MAX_FIRMATA_CMD_BUFF_SZ # Firmata max cmd buff sz





# Registers lookup tables

# uint8_t VGARegAddr[PM0SC__MAX_REG_NB] = {0x01,  0x02, 0x1E, 0x25, 0x26, 0x2B, 0x3C, 0x3D, 0x3E, 0x3F}; //!< Address of each register, to get address from register index

VGARegAddr = [0x01,  0x02, 0x1E, 0x25, 0x26, 0x2B, 0x3C, 0x3D, 0x3E, 0x3F]

# uint8_t VGARegW8ESZ[PM0SC__MAX_REG_NB] = {1, 18, 7, 1, 5, 3, 1, 1, 1, 1};                              //!< Size of each register in W8, to get size from register index, 0 => Register handling not implemented

VGARegW8ESz = [1, 24, 7, 1, 5, 3, 1, 1, 1, 1]

# uint8_t VGARegAccess[PM0SC__MAX_REG_NB] = {REG_ACC_WR, REG_ACC_WR, REG_ACC_WR, REG_ACC_WR, REG_ACC_WR, REG_ACC_WR, REG_ACC_WR, REG_ACC_WR, REG_ACC_WR, REG_ACC_WR}; //!< Access mode of each register, to get mode from register index,REG_ACC_NA = Not available = register not implemenetd

VGARegAccess = [TRegAcc.WR.value, TRegAcc.WR.value, TRegAcc.WR.value, TRegAcc.WR.value, TRegAcc.WR.value, TRegAcc.WR.value, TRegAcc.WR.value, TRegAcc.WR.value, TRegAcc.WR.value, TRegAcc.WR.value]

# char*   VGARegName[PM0SC__MAX_REG_NB] = { "Global command", "Pixel sequence", "Vpulse switch", "Test structure control", "DAC values", "DAC switches", "Data emulation", "Pixel config row", "Pixel config col", "Pixel config data" }; //!< Name of each register, to get name from register index

VGARegName = [ "Global command", "Pixel sequence", "Vpulse switch", "Test structure control", "DAC values", "DAC switches", "Data emulation", "Pixel config row", "Pixel config col", "Pixel config data" ]

VGStrRegOp = ["SW","HW","CHECK"]

# Registers list init to 0
#
# 28/12/2021 G.CLAUS CNRS/IN2P3/IPHC/C4PI

VGRegZero = [
    [0],                                                # Global command
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  # Pixel sequence
    [0,0,0,0,0,0,0],                                    # Vpulse switch
    [0],                                                # Test structure control
    [0,0,0,0,0],                                        # DAC values
    [0,0,0],                                            # DAC switches
    [0],                                                # Data emulation
    [0],                                                # Pixel config row
    [0],                                                # Pixel config col 
    [0]                                                 # Pixel config data
    ]

# Registers list which contains PICMIC default values, now 0
#
# 28/12/2021 G.CLAUS CNRS/IN2P3/IPHC/C4PI

VGRegDef = [
    [0],                                                # Global command
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  # Pixel sequence
    [0,0,0,0,0,0,0],                                    # Vpulse switch
    [0],                                                # Test structure control
    [0,0,0,0,0],                                        # DAC values
    [0,0,0],                                            # DAC switches
    [0],                                                # Data emulation
    [0],                                                # Pixel config row
    [0],                                                # Pixel config col 
    [0]                                                 # Pixel config data
    ]



# ===========================================================================
# Global variables  
# ===========================================================================


# Arduino DUE answer data to a request
#
# 27/12/2021 G.CLAUS CNRS/IN2P3/IPHC/C4PI

VGAArdAns = []


# Flag to indicates if Arduino DUE answer data to a request is ready or not
#
# 27/12/2021 G.CLAUS CNRS/IN2P3/IPHC/C4PI


VGArdAnsReady = 0

# Time of beginning of a request to I2C controller 
#
# XX/12/2021 G.CLAUS CNRS/IN2P3/IPHC/C4PI

VGTimeBeg = 0


# Memory image of registers to be written to PICMIC, initialized to 0
#
# 28/12/2021 G.CLAUS CNRS/IN2P3/IPHC/C4PI

VGRegWr = VGRegZero.copy () 


# Memory image of registers to read from PICMIC, initialized to 0
#
# 28/12/2021 G.CLAUS CNRS/IN2P3/IPHC/C4PI


VGRegRd = VGRegZero.copy () 
 

VGRegOp     = TRegOp.CHK.value
VGPrePostOp = TPrePostOp.NONE.value
VGPrePostParam = TPrePostOp.NONE.value

VGRegSaveToFile = 1
VGFileToSaveRegs = "I2C_Regs_Picmic.txt"


# ===========================================================================
# Functions  
# ===========================================================================


def FVersion ( Print = 0) :

    '''
    ...
    
    Prints module name, version and date
    
    
    Param
    - Print 0/1 1 => Prints modules info
    
    Returns
    - Module version majour
    - Module version minor
    - Module info + date
    - Module author

    28/12/2021 G.CLAUS CNRS/IN2P3/IPHC/C4PI    

    '''

    VVersMajor = 1
    VVersMinor = 0
    VDate      = "28/12/2021"
    VModule    = "PICMIC 0 slow control module V{:d}.{:d} {:s}".format (VVersMajor, VVersMinor, VDate) 
    VAuthor    = "G.CLAUS CNRS/IPHC/C4PI"

    if ( Print ) :
        print ( "" )
        print ( "============================================" )
        print ( VModule )
        print ( VAuthor )
        print ( "============================================" )
        print ( "" )
        
    return ( VVersMajor, VVersMinor, VModule, VAuthor)



def FPrintErrMsg ( Msg ) :
    print ( "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!" )
    print ( Msg )
    print ( "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!" )


def FConVectMidi7bTo8bV1 ( Src, Print ):

    '''
    ...
    
    Convert a Firmata/midi 7 bits list in 8 bits list
    
    Version V1 uses variables to store intermediate results
    
    Param
    - Src   =  Source list to convert
    - Print = 0 => No print / 1 => Prints conversion time
    
    Returns
    - Loist of 8 bits words

    XX/12/2021 G.CLAUS CNRS/IN2P3/IPHC/C4PI    

    '''


    VAW8 = list ()
    VW8Nb = len ( Src ) // 2
    Vi = 0
    
    if ( Print ):    
        v_time_beg = time.perf_counter ()    
    
    while ( Vi < VW8Nb ):
        ViX2 = Vi * 2
        ViX2P1 = ViX2 + 1
        VAW8.append ( Src[ViX2] + (128 * Src[ViX2P1] ) )
        Vi = Vi + 1
       

    if ( Print ):
        v_time_end = time.perf_counter ()
        v_time_s   = v_time_end - v_time_beg
        print ( "" )
        print ( "exec time = {:.6f} s".format (v_time_s) )
        print ( "" )
       
    return VAW8
    

    
def FConVectMidi7bTo8bV2 ( Src, Print ):

    '''
    ...
    
    Convert a Firmata/midi 7 bits list in 8 bits list
    
    Version V2 doesn't use variables to store intermediate results
    
    Param
    - Src   =  Source list to convert
    - Print = 0 => No print / 1 => Prints conversion time
    
    Returns
    - Loist of 8 bits words

    XX/12/2021 G.CLAUS CNRS/IN2P3/IPHC/C4PI    

    '''

    VAW8 = list ()
    VW8Nb = len ( Src ) // 2
    Vi = 0
    
    if ( Print ):        
        v_time_beg = time.perf_counter ()    
    
    while ( Vi < VW8Nb ):
        VAW8.append ( Src[2 * Vi] + (128 * Src[(2 * Vi) + 1] ) )
        Vi = Vi + 1
       

    if ( Print ):
        v_time_end = time.perf_counter ()
        v_time_s   = v_time_end - v_time_beg
        print ( "" )
        print ( "exec time = {:.6f} s".format (v_time_s) )
        print ( "" )
       
    return VAW8
    
def FConVect8bToMidi7b ( Src, Print ):

    '''
    ...
    
    Convert a Firmata/midi 7 bits list in 8 bits list
    
    Version V2 doesn't use variables to store intermediate results
    
    Param
    - Src   =  Source list to convert
    - Print = 0 => No print / 1 => Prints conversion time
    
    Returns
    - List of 8 bits words

    24/02/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI    

    '''
    logger = logging.getLogger('pm0_sc')

    VAW8 = list ()
    VW8SrcSz = len ( Src )
    Vi = 0
    
    if ( Print ):        
        v_time_beg = time.perf_counter ()    

    for Item in Src:
         VAW8.append ( ((Item&0x7F)) )   
         VAW8.append ( (Item&0x80)>>7 )   
    
    VVAW8Sz = len ( VAW8 )  
    logger.debug ( "src size ={:d} / result size :{:d}".format (VW8SrcSz,VVAW8Sz) )
    logger.debug ( "data to send ={}".format (VAW8) )

    if ( Print ):
        v_time_end = time.perf_counter ()
        v_time_s   = v_time_end - v_time_beg
        print ( "" )
        print ( "exec time = {:.6f} s".format (v_time_s) )
        print ( "" )
       
    return VAW8
   
  
             
def FConvU8ToS8 ( SrcU8 ) :

    '''
    ...
    
    Convert an unsigend byte to a signed byte
    
    Param
    - SrcU8          =  Source unsigned byte
    
    Returns
    - Signed byte corresponding to SrcU8

    XX/12/2021 G.CLAUS CNRS/IN2P3/IPHC/C4PI    

    '''

    if ( SrcU8 > 127 ):
        return (255 - SrcU8 + 1) * -1
        
    return ( SrcU8 )    
    




def FResetPixelMatrix(ResetValue, VRegOp, VPrePostOp, VPrePostParam):

    '''
    ...
    
    Reset all the pixel memories
    
    Param
    - ResetValue     =  Value to be set to all the pixel registers
    - VRegOp         =  Register operation mode
    - VPrePostOp     = Pre/post operatiion mode
    - VPrePostParam  = Pre/post operation param
    
    Returns
    - An error code, 0 => OK, < 0 => error

    03/08/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI    

    '''
    logger = logging.getLogger('pm0_sc')
    # reset the matrix
    # write col value : select all columns
    VErr = FCmdSetWrReg ( TRegId.CONF_COL.value, VRegOp, VPrePostOp, VPrePostParam, [64] )
    VStatus = "Reset Matrix Select all col, Reg op = {:s} - Write error = {:d}".format (VGStrRegOp[VRegOp], VErr)
    if VErr >= 0:
        logger.debug(VStatus)
    else:
        logger.error(VStatus)
    # write row value : select all rows
    VErr = FCmdSetWrReg ( TRegId.PIX_CONF_ROW.value, VRegOp, VPrePostOp, VPrePostParam, [128] )
    VStatus = "Reset Matrix select all Row, Reg op = {:s} - Write error = {:d}".format (VGStrRegOp[VRegOp], VErr)
    if VErr >= 0:
        logger.debug(VStatus)
    else:
        logger.error(VStatus)
    # Set data to pixel : MSB at 1
    VErr = FCmdSetWrReg ( TRegId.CONF_DATA.value, VRegOp, VPrePostOp, VPrePostParam, [ResetValue] )
    VStatus = "Reset Matrix set pixel data to 0, Reg op = {:s} - Write error = {:d}".format (VGStrRegOp[VRegOp], VErr)
    if VErr >= 0:
        logger.debug(VStatus)
    else:
        logger.error(VStatus)
    # write col value : unselect all columns
    VErr = FCmdSetWrReg ( TRegId.CONF_COL.value, VRegOp, VPrePostOp, VPrePostParam, [128] )
    VStatus = "after Reset Matrix unselect all col, Reg op = {:s} - Write error = {:d}".format (VGStrRegOp[VRegOp], VErr)
    if VErr >= 0:
        logger.debug(VStatus)
    else:
        logger.error(VStatus)

    return VErr




  
def FSendCmd ( CmdId, CmdADataW8, CmdRetADataW8Sz ) :

    '''
    ...
    
    Sents a command to Arduino
    
    Param
    - CmdId           =  No of the command
    - CmdADataW8      =  The command data as an array of W8
    - CmdRetADataW8Sz =  Number of W8 returned by function in case it returns an array
    
    Returns
    - An error code, 0 if ok
    - An optionnal array of results
    
    26/12/2021 G.CLAUS CNRS/IN2P3/IPHC/C4PI  
    
    '''
    
    VRet = 0
    logger = logging.getLogger('pm0_sc')
    
    global  VGBoard
    global  VGBuffW8Sz
    global  VGTimeBeg
    global  VGArdAnsReady
    global  VGAArdAns
    
    # Save i2c orders to to file
    if (VGRegSaveToFile != 0):
        try :
            # Saving to file
            with open(VGFileToSaveRegs, 'a') as Regsfile:
                # Reg Id = first data [RegId, RegOp,PrePostOp,PrePostParam, VRegSz]
                VRegAddress = VGARegAddr[CmdADataW8[0]]
                VRegNb = len ( CmdADataW8 ) - 5
                for VIndex in range (VRegNb):
                    # write all registers values
                    VStringToAppend = "{:d},{:d}\n".format(VRegAddress + VIndex,CmdADataW8[5+VIndex])
                    Regsfile.write(VStringToAppend)
        except IOError as e:
            print ("I/O error({0}): {1}".format(e.errno, e.strerror))
            logger.error("I/O error({0}): {1}".format(e.errno, e.strerror))
        except: #handle other exceptions such as attribute errors
            #print ("Unexpected error:", sys.exc_info()[0])
            logger.error ("Unexpected error")
            pass
    
    
    VGTimeBeg = time.perf_counter ()
    
    
    VCmdToArduinoSz = len ( CmdADataW8 ) + 2 # + 2 for W[0],W[1] = CmdRetADataW8Sz, now 27/12/2021, only W[0] is used
    
    
       
    # Check size of buffer the Arduino must send back
    
    if ( CmdRetADataW8Sz > MAX_CMD_BUFF_SZ ):
        print ( "Abort : Arduino returned buff sz {:d} > Max = {:d}".format (CmdRetADataW8Sz, MAX_CMD_BUFF_SZ)  )
        return (-1)

    
    # Check size of buffer to send to Arduino
 
    if ( VCmdToArduinoSz > MAX_CMD_BUFF_SZ ):
        print ( "Abort : Arduino received buff sz {:d} > Max = {:d}".format (VCmdToArduinoSz, MAX_CMD_BUFF_SZ)  )
        return (-1)
 
 
    # Calculates total size of buffers : sent + received

    VGBuffW8Sz = VCmdToArduinoSz + CmdRetADataW8Sz + 1 # + 1 because RetAData contains also status code
 
    # Build buffer to Arduino
   
    # Format of W8 buffer sent to Arduino
    # W[0],W[1] = CmdRetADataW8Sz, size of array the Arduino must return, it can be 0, now 27/12/2021, only W[0] is used
    # W[2], W[3], ... = CmdADataW8

   
    VCmdADataW8 = []
    
    VCmdADataW8.append (CmdRetADataW8Sz) # W[0] = low 16 bits Expected returned / answser size
    VCmdADataW8.append (0)               # W[1] = in FUTURE high 16 bits Expected returned / answser size, now 27/12/2021 => 0        
    
    # Since 10/02/2022 W16 are also handled, but not W32
    
    
    for VW8 in CmdADataW8:
    
        # W8 handling
    
#        if (type(VW8)==ct.c_ubyte):
#            VCmdADataW8.append (VW8)
            
#        elif ( VW8 < 256 ) : 
        if ( VW8 < 256 ) :   
            VCmdADataW8.append (VW8)
        
        # W16 handling
            
        else : 
            VCmdADataW8.append (VW8 & 0xFF) # First byte  = B7B0
            VCmdADataW8.append (VW8 >> 8  ) # Second byte = B15B8

    VCmdADataW7 = FConVect8bToMidi7b ( VCmdADataW8, 0 )
        
    VCmdADataBA = bytearray (VCmdADataW7)   
    #VCmdADataBA = bytearray (VCmdADataW8)   
    VGArdAnsReady = 0
    
    VGBoard.send_sysex (CmdId,VCmdADataBA) # 
  
    VGBoard.iterate()        

    if ( VGArdAnsReady == 1 ):
        VGArdAnsReady = 0

        # print ( "Arduino cmd status = {:d}".format ( FConvU8ToS8 (VGAArdAns[0]) ) )
        
        VRet = FConvU8ToS8 ( VGAArdAns[0] ) # Get status / returned code from UC
        
        del VGAArdAns[0]  # Delete status / returned code to get list of useful UC returend data only      
        
        if ( CmdRetADataW8Sz == 0 ):
            return ( VRet )
            
        else:
            return (VRet, VGAArdAns) 

    else:
        print ( "Error : No cmd answer from Arduino" )
        # return (-2) # 18/02/2022 - GC : Bug fix : Code returned before 18/02/2022
        return (-3)   # 18/02/2022 - GC : Bug fix : new code returned in order to distinguish DUE not responding error from I2C errors



    
    
def FCmdSetLog ( LogRaw, LogCmd ) :

    ''' 
    ... 
    
    Sents a command set log (PM0SC__CMD_SET_LOG) to Arduino
    
    Param
    - LogRaw      =  0 => No log, 1 => Log commands raw data request and answer buffer
    - LogCmd      =  0 => No log, 1 => Log cmd name, 2= Log cmd name + data, results
    
    Returns
    - An error code, 0 => OK, < 0 => error
    - An optionnal array of results
    
    27/12/2021 G.CLAUS CNRS/IN2P3/IPHC/C4PI    
    
    '''
    
    VRet = 0
    
    VCmdRq = [LogRaw,LogCmd ]
     
    # FSendCmd ( CmdId, CmdADataW8, CmdRetADataW8Sz )
     
    VRet = FSendCmd ( TCmd.SET_LOG.value, VCmdRq, 0 )
    
    if ( VRet < 0 ):
        print ( "Cmd set log failed !" )
    
    return (VRet)

 

    
def FCmdGetStatus ( Reserved ) :

    '''
    ...
    
    Sents a command get status (PM0SC__CMD_GET_STATUS) to Arduino
    
    Param
    - Reserved    =  A W8 param reserved for future use
    
    Returns
    - An error code, 0 => OK, < 0 => error
    - An array of [SW status, HW status]
    
    27/12/2021 G.CLAUS CNRS/IN2P3/IPHC/C4PI
    
    '''
    

    
    VRet = 0
    
    
    VCmdRq = [Reserved]
     
    # FSendCmd ( CmdId, CmdADataW8, CmdRetADataW8Sz )
     
    VRet,VAStatus = FSendCmd ( TCmd.GET_STATUS.value, VCmdRq, 2 )
    
    VAStatus[0] = FConvU8ToS8 ( VAStatus[0] )
    VAStatus[1] = FConvU8ToS8 ( VAStatus[1] )
    
    
    if ( VRet < 0 ):
        VAStatus[0] = -128
        VAStatus[1]= -128
        print ( "Cmd get status failed !" )
    
    return (VRet,VAStatus)

 
 
 
    
def FCmdSetWrReg ( RegId, RegOp,PrePostOp,PrePostParam, RegAW8 ) :

    '''
    ...
    
    Set / write a register to PICMIC
    
    Param
    - RegId  = Register identifier, see TRegId => GLB_CMD, etc ...
    - RegOp  = Operation, see TRegOp => SW (sets ram image), HW (sets RAM image + write to PICMIC), CHK => HW + read back and compare
    - RegAW8 = Array of data to be written in register
    
    Returns
    - An error code, 0 => OK, -1 sw error, -2 readback value <> write one 
    
    28/12/2021 G.CLAUS CNRS/IN2P3/IPHC/C4PI
    
    '''
    logger = logging.getLogger('pm0_sc')
    

    
    VRet = 0
    
    
    # Check register size
    
    VDataSz = len ( RegAW8 )
    VRegSz  = VGARegW8ESz[RegId]
    
    if ( VDataSz != VRegSz ):
        FPrintErrMsg ( "Abort : Data sz = {:d} != Register sz = {:d}".format (VDataSz, VRegSz) )
        return (-1)
    
    # Build request buffer
    
    VCmdRq = [RegId, RegOp,PrePostOp,PrePostParam, VRegSz]
    
    for _ in RegAW8:
        VCmdRq.append ( _ )
        #VCmdRq.append ( ((_&0xF0)>>4)+0x10 )   
        #VCmdRq.append ( (_&0x0F)+0x20 )   
            
    logger.debug ( "Data sent : {}".format(VCmdRq) )
    #VTestData = []
    #for Index in range (0,VRegSz):
    #    VTestData.append(((VCmdRq[5+(2*Index)]&0x0F)<<4)+(VCmdRq[6+(2*Index)]&0x0F))
    #logger.info ( "VTestData : {}".format(VTestData) )
    
     
    # FSendCmd ( CmdId, CmdADataW8, CmdRetADataW8Sz )
     
    VRet = FSendCmd ( TCmd.SET_WR_REG.value, VCmdRq, 0 )
    
    while (1) :
    
        if ( VRet == 0 ) :
            break
    
        if ( VRet > 0 ) :
            FPrintErrMsg ( "Abort => {:d} register R/W errors".format (VRet) )
            break
    
        if ( VRet == -1 ):
            FPrintErrMsg ( "Abort => SW error" )
            break;
   
   
        # 18/02/2022 - GC : Bug fix : Buggy code removed, bug due to bad indentation !!! 
        #
        # if ( VRet == -2 ):
            # FPrintErrMsg ( "Abort => DUE not responding OR I2C error" )
   
        # # If this step is reached => Error but no info on source
            # FPrintErrMsg ( "Abort => Error code = {:d}".format (VRet) )
            # break
 

        # 18/02/2022 - GC : Bug fix :  new source code to 
        # - fix the above "indentation bug" 
        # - uses a new error code -3 to distinguish DUE not responding error from I2C errors

        if ( VRet == -2 ):
            FPrintErrMsg ( "Abort => I2C error" )
            break

        if ( VRet == -3 ):
            FPrintErrMsg ( "Abort => DUE not responding" )
            break
   
        # If this step is reached => Error but no info on source
        
        FPrintErrMsg ( "Abort => Error code = {:d}, unknown error source ...".format (VRet) )
        break

 
   
    return (VRet)

 
def FCmdWrOneReg ( RegAddr, RegOp,PrePostOp,PrePostParam, RegAW8 ) :

    '''
    ...
    
    Set / write a register to PICMIC
    
    Param
    - RegId  = Register address
    - RegOp  = Operation, see TRegOp => SW (sets ram image), HW (sets RAM image + write to PICMIC), CHK => HW + read back and compare
    - RegAW8 = Array of data to be written in register
    
    Returns
    - An error code, 0 => OK, -1 sw error, -2 readback value <> write one 
    
    17/05/2023 M.SPECHT CNRS/IN2P3/IPHC/C4PI
    
    '''
    logger = logging.getLogger('pm0_sc')
    

    
    VRet = 0
    
    
    # Check register size
    
    VDataSz = len ( RegAW8 )
    
    
    # Build request buffer
    
    VCmdRq = [RegAddr, RegOp,PrePostOp,PrePostParam, VDataSz]
    
    for _ in RegAW8:
        VCmdRq.append ( _ )
        #VCmdRq.append ( ((_&0xF0)>>4)+0x10 )   
        #VCmdRq.append ( (_&0x0F)+0x20 )   
            
    logger.debug ( "Data sent : {}".format(VCmdRq) )
    #VTestData = []
    #for Index in range (0,VRegSz):
    #    VTestData.append(((VCmdRq[5+(2*Index)]&0x0F)<<4)+(VCmdRq[6+(2*Index)]&0x0F))
    #logger.info ( "VTestData : {}".format(VTestData) )
    
     
    # FSendCmd ( CmdId, CmdADataW8, CmdRetADataW8Sz )
     
    VRet = FSendCmd ( TCmd.WR_REG_LOW_LEVEL.value, VCmdRq, 0 )
    
    while (1) :
    
        if ( VRet == 0 ) :
            break
    
        if ( VRet > 0 ) :
            FPrintErrMsg ( "Abort => {:d} register R/W errors".format (VRet) )
            break
    
        if ( VRet == -1 ):
            FPrintErrMsg ( "Abort => SW error" )
            break;
   
   
        # 18/02/2022 - GC : Bug fix : Buggy code removed, bug due to bad indentation !!! 
        #
        # if ( VRet == -2 ):
            # FPrintErrMsg ( "Abort => DUE not responding OR I2C error" )
   
        # # If this step is reached => Error but no info on source
            # FPrintErrMsg ( "Abort => Error code = {:d}".format (VRet) )
            # break
 

        # 18/02/2022 - GC : Bug fix :  new source code to 
        # - fix the above "indentation bug" 
        # - uses a new error code -3 to distinguish DUE not responding error from I2C errors

        if ( VRet == -2 ):
            FPrintErrMsg ( "Abort => I2C error" )
            break

        if ( VRet == -3 ):
            FPrintErrMsg ( "Abort => DUE not responding" )
            break
   
        # If this step is reached => Error but no info on source
        
        FPrintErrMsg ( "Abort => Error code = {:d}, unknown error source ...".format (VRet) )
        break

 
   
    return (VRet)
 
 
 
     
def FCmdGetRdReg ( RegId, RegOp,PrePostOp,PrePostParam ) :

    '''
    ...
    
    Get / read a register to PICMIC
    
    Param
    - RegId = register identifier, see TRegId => GLB_CMD, etc ...
    - RegOp = operation, see TRegOp => SW (gets registerfrom ram image), HW (reads from PICMIC and update ram image), CHK => HW + compare to write ram image
    
    Returns
    - An error code, 0 => OK, -1 sw error, -2 readback value <> write one
    - An array of data read from register
        
    28/12/2021 G.CLAUS CNRS/IN2P3/IPHC/C4PI
    
    '''
    logger = logging.getLogger('pm0_sc')
    

    
    VRet = 0
    VRegSzFromUc = 0; # register size returned by Arduino I2C master
    
    
    # Get register size
    
    VRegSz  = VGARegW8ESz[RegId]
    
    
    # Build request buffer
    
    VCmdRq = [RegId, RegOp,PrePostOp,PrePostParam, VRegSz]
                
     
    # FSendCmd ( CmdId, CmdADataW8, CmdRetADataW8Sz )
     
    VRet,VARead = FSendCmd ( TCmd.GET_RD_REG.value, VCmdRq, VRegSz )
    
    VRegSzFromUc = len ( VARead )
    logger.info ( "Data read : {}".format(VARead) )
    
    if ( VRegSzFromUc != VRegSz ):
        VRet = -1
        FPrintErrMsg ( "Abort => Register sz from uC = {:d} <> expected register sz = {:d}".format (VRegSzFromUc, VRegSz) )
    
    
    if ( VRet == -1 ):
        FPrintErrMsg ( "Abort => SW error" )
   
    if ( VRet == -2 ):
        FPrintErrMsg ( "Abort => I2C error : Readback register <> write one" )
   
    return (VRet,VARead)

 
     
def FCmdSetWrDef ( RegOp, DefOp, DefVal ) :

    '''
    ...
    
    Set / write a default registers values to PICMIC
    
    Param
    - RegOp  = Operation, see TRegOp => SW (sets ram image), HW (sets RAM image + write to PICMIC), CHK => HW + read back and compare
    - DefOp  = TDefOp.DEF.value = 0 SET/WR default values from doc, TDefOp.VAL.value = 1 SET/WR the value DefVal in ALL registers
    - Defval = The value written in ALL registers if DefOp = VAL = 1
   
    
    Returns
    - An error code, 0 => OK, -1 sw error, -2 readback value <> write one 
    
    28/12/2021 & 04/01/2022 G.CLAUS CNRS/IN2P3/IPHC/C4PI
    
    '''
      
    VRet = 0
    
        
   
    # Build request buffer
    
    VCmdRq = [RegOp,DefOp,DefVal]
    
     
    # FSendCmd ( CmdId, CmdADataW8, CmdRetADataW8Sz )
     
    VRet = FSendCmd ( TCmd.SET_WR_DEF.value, VCmdRq, 0 )
    
    
    
    if ( VRet == -1 ):
        FPrintErrMsg ( "Abort => SW error" )
   
    if ( VRet == -2 ):
        FPrintErrMsg ( "Abort => I2C error : Readback register <> write one" )
   
    return (VRet)


 
     
def FCmdWrAllReg ( RegOp ) :

    '''
    ...
    
    Write current values of registers RAM image to PICMIC
    
    Param
    - RegOp  = Operation, see TRegOp => SW or HW => Writes register to PICMIC, CHK => Write registers + read back and compare
    
    Returns
    - An error code, 0 => OK, -1 sw error, -2 readback value <> write one 
    
    28/12/2021 G.CLAUS CNRS/IN2P3/IPHC/C4PI
    
    '''
      
    VRet = 0
    
        
   
    # Build request buffer
    
    VCmdRq = [RegOp]
    
     
    # FSendCmd ( CmdId, CmdADataW8, CmdRetADataW8Sz )
     
    VRet = FSendCmd ( TCmd.WR_ALL_REG.value, VCmdRq, 0 )
    
    
    
    if ( VRet == -1 ):
        FPrintErrMsg ( "Abort => SW error" )
   
    if ( VRet == -2 ):
        FPrintErrMsg ( "Abort => I2C error : Readback register <> write one" )
   
    return (VRet)

 
 
     
def FCmdRdAllReg ( RegOp ) :

    '''
    ...
    
    Reads all register from PICMIC and copy their values in RAM image, if RegOp = CHK
    the read values are compared to current write values from RAM image in case of
    difference error code -2 is returned
    
    Param
    - RegOp  = SW or HW => Reads registers from PICMIC and copy them in RAM image, 
    CHK => Compare read values to RAM image write values, return -2 if difference
    
    Returns
    - An error code, 0 => OK, -1 sw error, -2 readback value <> write one 
    
    28/12/2021 G.CLAUS CNRS/IN2P3/IPHC/C4PI
    
    '''
      
    VRet = 0
    
        
   
    # Build request buffer
    
    VCmdRq = [RegOp]
    
     
    # FSendCmd ( CmdId, CmdADataW8, CmdRetADataW8Sz )
     
    VRet = FSendCmd ( TCmd.RD_ALL_REG.value, VCmdRq, 0 )
    
    
    
    if ( VRet == -1 ):
        FPrintErrMsg ( "Abort => SW error" )
   
    if ( VRet == -2 ):
        FPrintErrMsg ( "Abort => I2C error : Readback register <> write one" )
   
    return (VRet)

  
 
def FCmdTestI2CRegs ( RegId, ItNb ) :

    '''
    ...
    
    Test a bank of registers
    
    Param
    - RegId  = Id of the bank of registers to be tested
    - ItNb   = Number of iterations of the test to be done
    
    Returns
    - An error code, 0 => OK, -1 sw error, -2 readback value <> write one 
    
    25/07/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI
    
    '''
      
    VRet = 0
    
        
   
    # Build request buffer
    ItNb_Low = ItNb & 0xFF
    ItNb_High = (ItNb & 0xFF00) >> 8
    
    VCmdRq = [RegId, ItNb_Low,ItNb_High]
    
     
    # FSendCmd ( CmdId, CmdADataW8, CmdRetADataW8Sz )
     
    VRet = FSendCmd ( TCmd.TEST_I2C_REGS.value, VCmdRq, 0 )
    
    
    
    if ( VRet == -1 ):
        FPrintErrMsg ( "Abort => SW error" )
   
    if ( VRet == -2 ):
        FPrintErrMsg ( "Abort => I2C error : Readback register <> write one" )
   
    return (VRet)

 
     
def FCmdCtrlHwSig ( Cmd, RstSt, RstI2CSt, StartSt, TestmodeSt, PulseWidthUs ) :

    ''' 
    ... 
    
    Sents a command set HW signals ( PM0SC__CMD_CTRL_HW_SIG) to Arduino
    
    Param
    - Cmd           = Command => TCmdHwSig
    - RstSt         = RST state
    - RstI2CSt      = RST I2C state
    - StartSt       = START state
    - TestmodeSt    = TESTMODE state
    - PulseWidthUs  = Width in us oif the pulse generated on obne signal which is defined by Cmd  param
    
    Returns
    - An error code, 0 => OK, < 0 => error
    
    10/02/2022 G.CLAUS CNRS/IN2P3/IPHC/C4PI    
    
    '''       
    
    VRet = 0
    
    if ( PulseWidthUs < 255 ) :
        VCmdRq = [Cmd, RstSt, RstI2CSt, StartSt, TestmodeSt, PulseWidthUs, 0]
    
    else :
        VCmdRq = [Cmd, RstSt, RstI2CSt, StartSt, TestmodeSt, PulseWidthUs]
    
       
     
    VRet = FSendCmd ( TCmd.CTRL_HW_SIG.value, VCmdRq, 0 )
    
    
    if ( VRet < 0 ):
        print ( "Cmd set ctrl HW signals failed !" )
    
    
    return (VRet)



def FCmdActivateOutputs (RegOp  ) :

    ''' 
    ... 
    
    Sents a command activate outputs ( PM0SC__CMD_ACTIVATE_OUTPUTS) to Arduino
    
    Param
    - RegOp  = Operation, see TRegOp => SW or HW => Writes register to PICMIC, CHK => Write registers + read back and compare
    
    Returns
    - An error code, 0 => OK, < 0 => error
    
    29/09/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI    
    
    '''       
    
    VRet = 0
    
    # Build request buffer
    
    VCmdRq = [RegOp]
    
     
    # FSendCmd ( CmdId, CmdADataW8, CmdRetADataW8Sz )
     
       
     
    VRet = FSendCmd ( TCmd.ACTIVATE_OUTPUTS.value, VCmdRq, 0 )
    
    
    if ( VRet < 0 ):
        print ( "Cmd set ctrl HW signals failed !" )
    
    
    return (VRet)

 
def FCmdDeactivateOutputs (RegOp  ) :

    ''' 
    ... 
    
    Sents a command activate outputs ( PM0SC__CMD_ACTIVATE_OUTPUTS) to Arduino
    
    Param
    - RegOp  = Operation, see TRegOp => SW or HW => Writes register to PICMIC, CHK => Write registers + read back and compare
    
    Returns
    - An error code, 0 => OK, < 0 => error
    
    29/09/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI    
    
    '''       
    
    VRet = 0
    
    # Build request buffer
    
    VCmdRq = [RegOp]
    
     
    # FSendCmd ( CmdId, CmdADataW8, CmdRetADataW8Sz )
     
       
     
    VRet = FSendCmd ( TCmd.DEACTIVATE_OUTPUTS.value, VCmdRq, 0 )
    
    
    if ( VRet < 0 ):
        print ( "Cmd set ctrl HW signals failed !" )
    
    
    return (VRet)
 
 
def FPrintArdAns () :

    global  VGAArdAns
    
    print ( "" )
    print ( "VGAArdAns = {}".format (VGAArdAns) )
    print ( "" )


def FSetRegsSavingFileName(FileName,Comment):
    '''
    ...
    
    Sets the file name 
    
    
    It stores data in global variable VGAArdAns
    It sets the flag VGArdAnsReady after data reception
    It VPrint is set to 1, it prints
    - the request "loop back time" = time elapsed since request sending to UC until getting data back
    - the data, up to 255 W8
    
    Param
    - FileName          =  Name of the file to store the I2C registers values to be sent to picmic 
    
    Returns
    - Nothing
    
    16/05/2023 M.SPECHT CNRS/IN2P3/IPHC/C4PI    
    
    '''
    global VGRegSaveToFile
    global VGFileToSaveRegs



    VGFileToSaveRegs = FileName
    try:
        # Saving enabled : open the file and save the comment in the file
        with open(VGFileToSaveRegs, 'w') as Regsfile:
            Regsfile.write(":"+Comment+"\n")
    except :
        print('Could not write the saving file')
        


def FEnableRegsSavingInFile(Enable):
    '''
    ...
    
    Sets the file name 
    
    
    It stores data in global variable VGAArdAns
    It sets the flag VGArdAnsReady after data reception
    It VPrint is set to 1, it prints
    - the request "loop back time" = time elapsed since request sending to UC until getting data back
    - the data, up to 255 W8
    
    Param
    - FileName          =  Name of the file to store the I2C registers values to be sent to picmic 
    
    Returns
    - Nothing
    
    16/05/2023 M.SPECHT CNRS/IN2P3/IPHC/C4PI    
    
    '''
    global VGRegSaveToFile
    VGRegSaveToFile = Enable


def handleIncomingSysEx(*byteArray):

    '''
    ...
    
    Handles Firmata SysEx commands from UC
    
    
    It stores data in global variable VGAArdAns
    It sets the flag VGArdAnsReady after data reception
    It VPrint is set to 1, it prints
    - the request "loop back time" = time elapsed since request sending to UC until getting data back
    - the data, up to 255 W8
    
    Param
    - byteArray          =  Command data 
    
    Returns
    - Nothing

    XX/12/2021 G.CLAUS CNRS/IN2P3/IPHC/C4PI    

    '''
    

    global VGTimeBeg
    global VGBuffW8Sz
    global VGAArdAns
    global VGArdAnsReady
    
    VPrint     = 0   # 0 = No print, 1 = Prints execution time, 2 = Prints execution time + data
    VPrintW8Nb = 255 # Maximum number of W8 to print



    VGAArdAns = FConVectMidi7bTo8bV1 ( byteArray, 0 )
    
    # print ( "handleIncomingSysEx - {:d} W8 received - W[0] = {:d}".format ( len (VGAArdAns), VGAArdAns[0] ) )
    # input ( "Type enter to continue" )    
    

    v_time_end = time.perf_counter ()
    v_time_s   = v_time_end - VGTimeBeg
      
    
    VDataRate = VGBuffW8Sz / v_time_s
    
    if ( VPrint >= 1 ) :
        print ( "" )
        print ( "Request loop back time = {:.6f} s = {:.1f} ms".format (v_time_s, v_time_s * 1000) )
        print ( "Data rate = {:.1f} W8/S = {:.1f} bauds".format (VDataRate, VDataRate * 10) )  

    
    if ( VPrint >= 2 ) :    
        print ( "Data from Arduino : {:d} W8".format ( len (VGAArdAns) )  )
        print ( "Prints the first {:d} W8".format (VPrintW8Nb) )

        Vi = 0;    

        for x in VGAArdAns:
            print ( x )
            Vi = Vi + 1
            if (Vi >= VPrintW8Nb ):
                break # Prints only 10 first data
            
            
    VGArdAnsReady = 1        



def FConnect ( UsbPort,dsrdtr = False ) :

    '''
    ...
    
    Connects from Arduino DUE I2C controller
    
    Param
    - UsbPort    =  The USB port string
    - dsrdtr     =  True : Automatic reset of  the arduino board at connection disabled
                    False : Automatic reset of  the arduino board at connection enabled
    
    Returns
    - An error code, 0 => OK, < 0 => error
    
    27/12/2021 G.CLAUS CNRS/IN2P3/IPHC/C4PI
    
    '''
    
    global VGBoard
    logger = logging.getLogger('pm0_sc')
    
    logger.info('Port:{} / Auto reset disabled:{}'.format(UsbPort,dsrdtr))
    
    
    try:
        if (dsrdtr == True):
            VGBoard = Arduino ( UsbPort ,dsrdtr=dsrdtr ) 
        else:
            VGBoard = Arduino ( UsbPort ) 
        

        print("Communication Successfully started - Arduino board obj created")
        
        
        VGBoard.add_cmd_handler(pyfirmata.START_SYSEX, handleIncomingSysEx )
            
        
        VGBoard.callback_holder = dict()
      
       
      
        # Print infos
        
        print ( "============================================" )
        print ( "firmware         = {0}".format (VGBoard.firmware) )
        print ( "firmware_version = {0}".format (VGBoard.firmware_version) )
        print ( "firmata_version  = {0}".format (VGBoard.firmata_version) )
        print ( "============================================" )

        logger.info ( "============================================" )
        logger.info ( "firmware         = {0}".format (VGBoard.firmware) )
        logger.info ( "firmware_version = {0}".format (VGBoard.firmware_version) )
        logger.info ( "firmata_version  = {0}".format (VGBoard.firmata_version) )
        logger.info ( "============================================" )


        
        return (0)


    except : 
        logger.error("Could not connect to the Arduno board:{}".format(sys.exc_info()[1]))
        print(sys.exc_info()[1])
        return (-1)
    
    
    
    
    
def FDisconnect ( ) :

    '''
    ...
    
    Disconnects from Arduino DUE I2C controller
    
    Param
    - None
    
    Returns
    - An error code, 0 => OK, < 0 => error
    
    05/01/2022 G.CLAUS CNRS/IN2P3/IPHC/C4PI
    
    '''
    
    global VGBoard
    
    VGBoard.exit()
    
    del ( VGBoard )
    
    return (0)
    
    
    




if __name__ == "__main__" :

    FVersion (1)



