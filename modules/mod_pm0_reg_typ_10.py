# Module which contains PICMIC 0 slow control registers definition and tools to handle them
#


# ===========================================================================
# Modules import
# ===========================================================================




import sys

from enum import Enum, unique

from pyfirmata import Arduino
import time

import pyfirmata 

import ctypes as ct

import mod_pm0_sc_22 as PM0SC

import mod_pm0_reg_typ_10 as PM0RT


# ===========================================================================
# Constants
# ===========================================================================


VERSION_DATE = "V1.0 16/02/2022" # Module version &date


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
  
  
  
  
  
  
  
  
#===========================================   REG SHORTCUTS ====================================================  

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
    
    
    
    
    
    











# ===========================================================================
# Bit/bit register classes
# ===========================================================================



 #===========================================   REG GLOBAL COMMAND ==================================================== 

class TRegGlbCmdBits ( ct.Structure ):
        _fields_ = [("EnExtPulse", ct.c_ubyte, 1),  # Enable external pulse
                    ("ExtPulse", ct.c_ubyte, 1),    # External pulse
                    ("RstFrCnt", ct.c_ubyte, 1),    # Reset frame counter
                    ("StartSeq", ct.c_ubyte, 1),    # Start sequencer
                    ("nu", ct.c_ubyte, 4)]          # Not used
                




class TRegGlbCmd ( ct.Union ):
        _fields_ = [("aw8", ct.c_ubyte * 1),("b", TRegGlbCmdBits)]
        

# creating a variable that correspond to Global Command Register.

VRegGlbCmd = TRegGlbCmd () # on instancie la classe 









#===========================================   REG TEST STRUCTURE CONTROL ==================================================== 

class TRegTestSCtrlBits ( ct.Structure ):
        _fields_ = [("SW0", ct.c_ubyte, 1),  
                    ("SW1", ct.c_ubyte, 1),  
                    ("EN_CM", ct.c_ubyte, 1),   
                    ("EN_CC", ct.c_ubyte, 1),    
                    ("ENA_CM1", ct.c_ubyte, 1),    
                    ("ENA_D2P", ct.c_ubyte, 1),
                    ("ENA_D1P", ct.c_ubyte, 1),
                    ("UnUsed", ct.c_ubyte, 1)]
                                      
                



class TRegTestSCtrl ( ct.Union ):
        _fields_ = [("aw8", ct.c_ubyte * 1),("b", TRegTestSCtrlBits)]
        
        

VRegTestSCtrl = TRegTestSCtrl () # on instancie la classe 


















#===========================================   REG CONFIG_ROW ==================================================== 

class TRegCfgRowBits ( ct.Structure ):
        _fields_ = [("SelRow", ct.c_ubyte, 7),  
                    ("SelAllRow", ct.c_ubyte, 1)]
                                      
                



class TRegCfgRow ( ct.Union ):
        _fields_ = [("aw8", ct.c_ubyte * 1),("b", TRegCfgRowBits)]
        
        

VRegCfgRow = TRegCfgRow () # on instancie la classe 

















 #===========================================   REG CONFIG COL ==================================================== 

class TRegCfgColF( ct.Structure ):
        _fields_ = [("SelCol", ct.c_ubyte, 6),  
                    ("SelDeselAllCol", ct.c_ubyte, 2)]
                                      
                



class TRegCfgCol ( ct.Union ):
        _fields_ = [("aw8", ct.c_ubyte * 1),("b", TRegCfgColF)]
        
        

VRegCfgCol = TRegCfgCol () # on instancie la classe 






















#===========================================   REG CONFIG_DATA ==================================================== 

class TRegCfgDataBits ( ct.Structure ):
        _fields_ = [("I_Adj", ct.c_ubyte, 3),    
                    ("ENA_CM", ct.c_ubyte, 1),    
                    ("SW0", ct.c_ubyte, 1),    
                    ("SW1", ct.c_ubyte, 1),
                    ("ENA_CC", ct.c_ubyte, 1),
                    ("ActivateVpulse", ct.c_ubyte, 1)]
                                      
                



class TRegCfgData ( ct.Union ):
        _fields_ = [("aw8", ct.c_ubyte * 1),("b", TRegCfgDataBits)]
        
        

VRegCfgData = TRegCfgData () # on instancie la classe 


















#===========================================   REG PIX_SEQUENCER ==================================================== 




PixSeqNameList = ["FlushMod", "UnUsed", "MarkerMod", "UnUsed", "PulseMod", "LoadWidth", "Load_pLSB",
            "Load_pMSB", "Flush_pLSB", "Flush_pMSB", "Apulse_pLSB", "Apulse_pMSB", "Dpulse_pLSB", "Dpulse_pMSB", "RdpixMaskLSB",
            "RdpixMaskMSB", "MaxFrameLSB", "MaxFrameMSB", "PolarityLSB", "PolarityMSB", "Marker1LSB", "Marker1MSB", "Marker2LSB", "Marker2MSB"]



class TRegPixSeqU8 ( ct.Structure ):
        _fields_ = [("FlushMod", ct.c_ubyte, 8),    
                    ("UnUsed", ct.c_ubyte, 8),    
                    ("MarkerMod", ct.c_ubyte, 8),    
                    ("UnUsed", ct.c_ubyte, 8),
                    ("PulseMod", ct.c_ubyte, 8),
                    ("LoadWidth", ct.c_ubyte, 8),
                    ("Load_pLSB", ct.c_ubyte, 8),
                    ("Load_pMSB", ct.c_ubyte, 8),
                    ("Flush_pLSB", ct.c_ubyte, 8),
                    ("Flush_pMSB", ct.c_ubyte, 8),
                    ("Apulse_pLSB", ct.c_ubyte, 8),
                    ("Apulse_pMSB", ct.c_ubyte, 8),
                    ("Dpulse_pLSB", ct.c_ubyte, 8),
                    ("Dpulse_pMSB", ct.c_ubyte, 8),
                    ("RdpixMaskLSB", ct.c_ubyte, 8),
                    ("RdpixMaskMSB", ct.c_ubyte, 8),
                    ("MaxFrameLSB", ct.c_ubyte, 8),
                    ("MaxFrameMSB", ct.c_ubyte, 8),
                    ("PolarityLSB", ct.c_ubyte, 8),
                    ("PolarityMSB", ct.c_ubyte, 8),
                    ("Marker1LSB", ct.c_ubyte, 8),
                    ("Marker1MSB", ct.c_ubyte, 8),
                    ("Marker2LSB", ct.c_ubyte, 8),
                    ("Marker2MSB", ct.c_ubyte, 8)]
                                      
                



class TRegPixSeq ( ct.Union ):
        _fields_ = [("aw8", ct.c_ubyte * 24),("f", TRegPixSeqU8)]
        
        

VRegPixSeq = TRegPixSeq () # on instancie la classe 