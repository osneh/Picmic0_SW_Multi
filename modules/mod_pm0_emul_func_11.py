#!/usr/bin/env python3
# Module which contains PICMIC 0 emulation functions
#
#
# 16/02/2022 V10 M.SPECHT CNRS/IN2P3/IPHC/C4PI 
#- First implementation  
#
# 21/02/2022 V10 M.SPECHT CNRS/IN2P3/IPHC/C4PI 
#- moved the FSetBitMapFromFile fonction from the sc_picmic_gc_22.py script
#
# 24/11/2022 V11 M.SPECHT CNRS/IN2P3/IPHC/C4PI 
# - modified the importing procedure in order to have one place to change the modules names in the project
#
# Can be loaded as a module under python interpreter and used in interactive mode
# python
# >>> import module
# >>> m = module
# >>> m.FPrint ()
# >>> m.VInteger
# >>> etc ...
#
# Another way to import module 
#
# >>> import module as m
# >>> m.FPrint ()

__author__ = "M.SPECHT CNRS/IPHC/C4PI"
__author_email__ = "matthieu.specht@iphc.cnrs.fr"
__version__ = '1.1.0'
__vdate__ = "24/11/2022" # Module version &date


# ===========================================================================
# Modules import
# ===========================================================================

import logging
import numpy as np
import sys
import ctypes as ct
import importlib
import configparser    # for the ini file configuration retrieving 

import re

from time import sleep


# retrieve the modules names from the Modules.conf file
config = configparser.ConfigParser(allow_no_value=True)
config.read("modules/Modules.conf")


PM0SC_Name = config['ModuleName']['slowControlLowLevel']
#import mod_pm0_emul_func_11 as PM0EMUL # for the comment extracting of the pulsing files
PM0SC = importlib.import_module(PM0SC_Name, package=None)
#import mod_pm0_sc_23 as PM0SC




# ===========================================================================
# Global variables  
# ===========================================================================


# BitMap for the pixel emulation for picmic
#
# 17/02/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI
#BitMap = []

# For registers operation

RegOp     = PM0SC.TRegOp.CHK.value

VGStrRegOp = ["SW","HW","CHECK"]

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
    - Module version 
    - Module info + date
    - Module author

    28/12/2021 G.CLAUS CNRS/IN2P3/IPHC/C4PI    

    '''

    VModule    = "PICMIC 0 emulation module V{:s} {:s}".format (__version__, __vdate__) 
    VAuthor    = "M.SPECHT CNRS/IPHC/C4PI"

    if ( Print ) :
        print ( "" )
        print ( "============================================" )
        print ( VModule )
        print ( __author__ )
        print ( "============================================" )
        print ( "" )
        
    return ( __version__,  VModule, __author__)




# 19/02/2022
 
def FPrintRegWRError ( Err, TestNo, RegName, RegOp, PrePostOp, PrePostParam, Pattern ) :
    '''
    ...
    
    - Prints a register if there was an error
    
    Param
    - Err : selection of the way to treat the bitmap
        - 0 : set all pixels of the matrix, even the one not selected
        - 1 : set only the selected pixels
    - TestNo :  index of the test being done
    - RegName : name of the register concerned
    - Pattern : pattern sent to the register
    Returns
        - Result: 0 if successfull, negative if failed
        - BitMap: two dimensions list ( 128 x 54 ) containing the  pixel matrix
        - HitNb: number of hits in the emulated matrix
    
    19/02/2022 G.CLAUS CNRS/IN2P3/IPHC/C4PI
    
    '''
    logger = logging.getLogger('pm0_emul')
 
    if ( Err != 0 ) : 
      VErr, VARead = PM0SC.FCmdGetRdReg ( PM0SC.TRegId.PIX_SEQ.value, RegOp, PrePostOp, PrePostParam )        
      VStatus = "Read error = {:d} - Read values dec = {}".format (VErr, VARead)
      print ( "Register {:s} W/R error on Test no = {:d} \n".format (RegName, TestNo) )
      VPatternToPrint = []  
      print ( "Test pattern = {}".format(Pattern) )
      print ( "Read back  pattern = {}".format(VARead) )
      logger.error("Register {:s} W/R error on Test no = {:d} \n".format (RegName, TestNo))
      logger.error("Test Pattern = {}".format (Pattern))
      logger.error ( "Read back  pattern = {}".format(VARead) )



 
def FWrPixSeqLoop ( LoopNb,RegOp, PrePostOp, PrePostParam ) :
    '''
    ...
    
    - Test sequence on the pixel sequencer register bank
    
    Param
    - LoopNb : number of iteration for the test

    Returns
        - Result: 0 if successfull, negative if failed
    
    18-19/02/2022 G.CLAUS CNRS/IN2P3/IPHC/C4PI
    
    '''

    logger = logging.getLogger('pm0_emul')

    VErr = 0

    VParamStr = input ( "WaitTime (ms) : " )     
    VWaitTime    = int ( VParamStr, 10 )

    for Vi in range (LoopNb) :


        if ( Vi % 100 == 0 ) :  
          
            VNow = dt.datetime.now()
            VStrNow = VNow.strftime("%H:%M:%S")

            print ( "Loop No : {:d} - Time = {:s} \n".format (Vi, VStrNow) )
            logger.info("Loop No : {:d} - Time = {:s} \n".format (Vi, VStrNow))

        VTestPat = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

        VErr = PM0SC.FCmdSetWrReg ( PM0SC.TRegId.PIX_SEQ.value, RegOp, PrePostOp, PrePostParam, VTestPat )   
        FPrintRegWRError ( VErr, Vi, "PIX SEQ", RegOp, PrePostOp, PrePostParam, VTestPat )
        if ( VErr != 0 ) : 
            logger.error("Error on first step of loop, VErr = {:d} ".format (VErr))
            return (-1)

        VTestPat = [0xFF,0x00,0xFF,0x00,0xFF,0x00,0xFF,0x00,0xFF,0x00,0xFF,0x00,0xFF,0x00,0xFF,0x00,0xFF,0x00,0xFF,0x00,0xFF,0x00,0xFF,0x00]

        VErr = PM0SC.FCmdSetWrReg ( PM0SC.TRegId.PIX_SEQ.value, RegOp, PrePostOp, PrePostParam, VTestPat )   
        FPrintRegWRError ( VErr, Vi, "PIX SEQ", RegOp, PrePostOp, PrePostParam, VTestPat )
        if ( VErr != 0 ) : 
            logger.error("Error on second step of loop, VErr = {:d} ".format (VErr))
            return (-1)
         
        VTestPat = [0x00,0xFF,0x00,0xFF,0x00,0xFF,0x00,0xFF,0x00,0xFF,0x00,0xFF,0x00,0xFF,0x00,0xFF,0x00,0xFF,0x00,0xFF,0x00,0xFF,0x00,0xFF]

        VErr = PM0SC.FCmdSetWrReg ( PM0SC.TRegId.PIX_SEQ.value, RegOp, PrePostOp, PrePostParam, VTestPat )   
        FPrintRegWRError ( VErr, Vi, "PIX SEQ", RegOp, PrePostOp, PrePostParam, VTestPat )
        if ( VErr != 0 ) : 
            logger.error("Error on third step of loop, VErr = {:d} ".format (VErr))
            return (-1)


        VTestPat = [0x55,0xAA,0x55,0xAA,0x55,0xAA,0x55,0xAA,0x55,0xAA,0x55,0xAA,0x55,0xAA,0x55,0xAA,0x55,0xAA,0x55,0xAA,0x55,0xAA,0x55,0xAA]

        VErr = PM0SC.FCmdSetWrReg ( PM0SC.TRegId.PIX_SEQ.value, RegOp, PrePostOp, PrePostParam, VTestPat )   
        FPrintRegWRError ( VErr, Vi, "PIX SEQ", RegOp, PrePostOp, PrePostParam, VTestPat )
        if ( VErr != 0 ) : 
            logger.error("Error on fourth step of loop, VErr = {:d} ".format (VErr))
            return (-1)


        VTestPat = [0xAA,0x55,0xAA,0x55,0xAA,0x55,0xAA,0x55,0xAA,0x55,0xAA,0x55,0xAA,0x55,0xAA,0x55,0xAA,0x55,0xAA,0x55,0xAA,0x55,0xAA,0x55]

        VErr = PM0SC.FCmdSetWrReg ( PM0SC.TRegId.PIX_SEQ.value, RegOp, PrePostOp, PrePostParam, VTestPat )   
        FPrintRegWRError ( VErr, Vi, "PIX SEQ", RegOp, PrePostOp, PrePostParam, VTestPat )
        if ( VErr != 0 ) : 
            logger.error("Error on fifth step of loop, VErr = {:d} ".format (VErr))
            return (-1)


        VTestPat = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]

        VErr = PM0SC.FCmdSetWrReg ( PM0SC.TRegId.PIX_SEQ.value, RegOp, PrePostOp, PrePostParam, VTestPat )   
        FPrintRegWRError ( VErr, Vi, "PIX SEQ", RegOp, PrePostOp, PrePostParam, VTestPat )
        if ( VErr != 0 ) : 
            logger.error("Error on sixth step of loop, VErr = {:d} ".format (VErr))
            return (-1)
      
    return (0)  





def FSetBitMapFromFile(Param,VFileName,VPulsingReg,VNotPulsingReg,VRegOp, VPrePostOp, VPrePostParam):
    '''
    ...
    
    - Loads a bitmap file ( name asked to the used in function)
    - compare the bitmap file with the list of connected pixels of picmic
    - Set the bitmap to the matrix of picmic
    
    Param
    - Param : selection of the way to treat the bitmap
        - 0 : set all pixels of the matrix, even the one not selected
        - 1 : set only the selected pixels
    
    Returns
        - Result: 0 if successfull, negative if failed
        - BitMap: two dimensions list ( 128 x 54 ) containing the  pixel matrix
        - HitNb: number of hits in the emulated matrix
    
    17/02/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI
    
    '''
    logger = logging.getLogger('pm0_emul')
    VErrorNb = 0
    FuncResult = 0


    # Set Global command to 0x00 (soft stop)
    VErr = PM0SC.FCmdSetWrReg ( PM0SC.TRegId.GLB_CMD.value, VRegOp, VPrePostOp, VPrePostParam, [0] )
    VStatus = "Reg op = {:s} - Wr val = {:X} Hex - Write error = {:d}".format (VGStrRegOp[VRegOp], 0, VErr)
    if VErr >= 0:
        logger.debug(VStatus)
    else:
        logger.error(VStatus)


    ConnectedPixelsBitmap = FExtractConnectedPixels('ROnb_xyp1.txt')
    logger.info("ConnectedPixelsBitmap :{}".format(ConnectedPixelsBitmap))
        
    if Param == 0:  #  all pixels set even the empty ones
        # Load the bitmap
        try :
            Result, BitMap, HitNb = FLoadBitmapFromFile ( VFileName )
        except:
            logger.error("Error while loading bitmap from file")
            Result = -1
        HitIndex = 0
        UnconnectedNb = 0
        if Result < 0 :
            print("Error reading the file !!!! ")
            VStatus = "Error reading the file !!!! "
            logger.error(VStatus)
            FuncResult = -1
        else:
            # reset the matrix
            # write col value : select all columns
            VErr = PM0SC.FCmdSetWrReg ( PM0SC.TRegId.CONF_COL.value, VRegOp, VPrePostOp, VPrePostParam, [64] )
            VStatus = "Reset Matrix Select all col, Reg op = {:s} - Write error = {:d}".format (VGStrRegOp[VRegOp], VErr)
            if VErr >= 0:
                logger.debug(VStatus)
            else:
                logger.error(VStatus)
            # write row value : select all rows
            VErr = PM0SC.FCmdSetWrReg ( PM0SC.TRegId.PIX_CONF_ROW.value, VRegOp, VPrePostOp, VPrePostParam, [128] )
            VStatus = "Reset Matrix select all Row, Reg op = {:s} - Write error = {:d}".format (VGStrRegOp[VRegOp], VErr)
            if VErr >= 0:
                logger.debug(VStatus)
            else:
                logger.error(VStatus)
            # Set data to pixel : MSB at 1
            VErr = PM0SC.FCmdSetWrReg ( PM0SC.TRegId.CONF_DATA.value, VRegOp, VPrePostOp, VPrePostParam, [VNotPulsingReg] )
            VStatus = "Reset Matrix set pixel data to 0, Reg op = {:s} - Write error = {:d}".format (VGStrRegOp[VRegOp], VErr)
            if VErr >= 0:
                logger.debug(VStatus)
            else:
                logger.error(VStatus)
            # write col value : unselect all columns
            VErr = PM0SC.FCmdSetWrReg ( PM0SC.TRegId.CONF_COL.value, VRegOp, VPrePostOp, VPrePostParam, [128] )
            VStatus = "after Reset Matrix unselect all col, Reg op = {:s} - Write error = {:d}".format (VGStrRegOp[VRegOp], VErr)
            if VErr >= 0:
                logger.debug(VStatus)
            else:
                logger.error(VStatus)

            # set the bitmap to the matrix
            for Col in range (54):
                # write col value :
                VErr = PM0SC.FCmdSetWrReg ( PM0SC.TRegId.CONF_COL.value, VRegOp, VPrePostOp, VPrePostParam, [Col] )
                VStatus = "Write col = {:d} , Reg op = {:s} - Write error = {:d}".format (Col,VGStrRegOp[VRegOp], VErr)
                if VErr >= 0:
                    logger.info(VStatus)
                else:
                    logger.error(VStatus)
                    VErrorNb += 1
                for Row in range (128):
                    #logger.info("Pixel[{},{}]".format(Row,Col))
                    print("Pixel[{},{}] (last:[128,54])".format(Row,Col))
                    if BitMap[Row,Col] == 1:
                        if ConnectedPixelsBitmap[Row,Col] == 1:
                            # Pixel connected, can be emulated
                            # write row value :
                            VErr = PM0SC.FCmdSetWrReg ( PM0SC.TRegId.PIX_CONF_ROW.value, VRegOp, VPrePostOp, VPrePostParam, [Row] )
                            VStatus = "Write row = {:d} , Reg op = {:s} - Write error = {:d}".format (Row,VGStrRegOp[VRegOp], VErr)
                            if VErr >= 0:
                                logger.debug(VStatus)
                            else:
                                logger.error(VStatus)
                                VErrorNb += 1
                            # Set data to pixel : bits 7(pulse) and 6(mask)  at 1
                            VErr = PM0SC.FCmdSetWrReg ( PM0SC.TRegId.CONF_DATA.value, VRegOp, VPrePostOp, VPrePostParam, [VPulsingReg] )
                            VStatus = "write pixel reg value = {:d} , Reg op = {:s} - Write error = {:d}".format (128,VGStrRegOp[VRegOp], VErr)
                            if VErr >= 0:
                                logger.debug(VStatus)
                            else:
                                logger.error(VStatus)
                                VErrorNb += 1
                            print("Hit No:{:d} out of {:d}".format(HitIndex,HitNb))
                            HitIndex += 1
                        else:
                            #Pixel not connected, 
                            UnconnectedNb += 1
                            BitMap[Row,Col] = 0
                            logger.error('Pixel Row:{:d}, Col:{:d} is a dummy pixel !!'.format(Row,Col))
                            # write row value :
                            VErr = PM0SC.FCmdSetWrReg ( PM0SC.TRegId.PIX_CONF_ROW.value, VRegOp, VPrePostOp, VPrePostParam, [Row] )
                            VStatus = "Write row = {:d} , Reg op = {:s} - Write error = {:d}".format (Row,VGStrRegOp[VRegOp], VErr)
                            if VErr >= 0:
                                logger.debug(VStatus)
                            else:
                                logger.error(VStatus)
                                VErrorNb += 1
                            # Set data to pixel : MSB at 0

                            VErr = PM0SC.FCmdSetWrReg ( PM0SC.TRegId.CONF_DATA.value, VRegOp, VPrePostOp, VPrePostParam, [VNotPulsingReg] )
                            VStatus = "write pixel reg value = {:d} , Reg op = {:s} - Write error = {:d}".format (0,VGStrRegOp[VRegOp], VErr)
                            if VErr >= 0:
                                logger.debug(VStatus)
                            else:
                                logger.error(VStatus)
                                VErrorNb += 1

                    else:
                        # write row value :
                        VErr = PM0SC.FCmdSetWrReg ( PM0SC.TRegId.PIX_CONF_ROW.value, VRegOp, VPrePostOp, VPrePostParam, [Row] )
                        VStatus = "Write row = {:d} , Reg op = {:s} - Write error = {:d}".format (Row,VGStrRegOp[VRegOp], VErr)
                        if VErr >= 0:
                            logger.debug(VStatus)
                        else:
                            logger.error(VStatus)
                            VErrorNb += 1
                        # Set data to pixel : MSB at 0

                        VErr = PM0SC.FCmdSetWrReg ( PM0SC.TRegId.CONF_DATA.value, VRegOp, VPrePostOp, VPrePostParam, [VNotPulsingReg] )
                        VStatus = "write pixel reg value = {:d} , Reg op = {:s} - Write error = {:d}".format (0,VGStrRegOp[VRegOp], VErr)
                        if VErr >= 0:
                            logger.debug(VStatus)
                        else:
                            logger.error(VStatus)
                            VErrorNb += 1

            # deselect all col : write 0x80 in col_cfg
            VErr = PM0SC.FCmdSetWrReg ( PM0SC.TRegId.CONF_COL.value, VRegOp, VPrePostOp, VPrePostParam, [0x80] )
            VStatus = "Unselect all col, Reg op = {:s} - Write error = {:d}".format (VGStrRegOp[VRegOp], VErr)
            #print the bitmap
            FPrintBitmap(BitMap)
            if VErr >= 0:
                logger.debug(VStatus)
            else:
                logger.error(VStatus)
                VErrorNb += 1

            # set the sequencer registers
            
#  MS 18 05 22  test the increasing of the frame size            
#            VErr = PM0SC.FCmdSetWrReg ( PM0SC.TRegId.PIX_SEQ.value, VRegOp, VPrePostOp, VPrePostParam, [0,0,0,0,0,16,2,3,0,1,12,1,100,12,251,255,0,0,55,67,3,4,36,37] )
            ##VErr = PM0SC.FCmdSetWrReg ( PM0SC.TRegId.PIX_SEQ.value, VRegOp, VPrePostOp, VPrePostParam, [0,0,0,0,0,100,2,3,0,1,0,0,200,12,251,255,0,0,55,67,3,4,200,201] )
            ##VStatus = "Reg op = {:s} - Write error = {:d}".format (VGStrRegOp[VRegOp], VErr)
            ##if VErr >= 0:
            ##    logger.debug(VStatus)
            ##else:
            ##    logger.error(VStatus)
            ##    VErrorNb += 1
            # Set Global command to 0x08 (soft start)
            VErr = PM0SC.FCmdSetWrReg ( PM0SC.TRegId.GLB_CMD.value, VRegOp, VPrePostOp, VPrePostParam, [8] )
            VStatus = "Reg op = {:s} - Wr val = {:X} Hex - Write error = {:d}".format (VGStrRegOp[VRegOp], 8, VErr)
            if VErr >= 0:
                logger.debug(VStatus)
            else:
                logger.error(VStatus)
            if VErrorNb == 0:
                logger.debug("Matrix set without any com error ")
                
            
            else:
                logger.error("Matrix set , total err nb : {:d}".format (VErrorNb))
                FuncResult = -2
            

    elif Param == 1:  #  only active pixels are set
        # Load the bitmap
        Result, BitMap, HitNb = FLoadBitmapFromFile ( VFileName )
        UnconnectedNb = 0
        HitIndex = 0
        if Result < 0 :
            print("Error reading the file !!!! ")
            VStatus = "Error reading the file !!!! "
            logger.error(VStatus)
            FuncResult = -1
        else:
            #input("Type return to continue")
            # reset the matrix
            # write col value : select all columns
            VErr = PM0SC.FCmdSetWrReg ( PM0SC.TRegId.CONF_COL.value, VRegOp, VPrePostOp, VPrePostParam, [64] )
            # write row value : select all rows
            VErr = PM0SC.FCmdSetWrReg ( PM0SC.TRegId.PIX_CONF_ROW.value, VRegOp, VPrePostOp, VPrePostParam, [128] )
            # Set data to pixel : MSB at 1
            VErr = PM0SC.FCmdSetWrReg ( PM0SC.TRegId.CONF_DATA.value, VRegOp, VPrePostOp, VPrePostParam, [VNotPulsingReg] )
            VStatus = "write pixel reg value, Reg op = {:s} - Write error = {:d}".format (VGStrRegOp[VRegOp], VErr)
            if VErr >= 0:
                logger.debug(VStatus)
            else:
                logger.error(VStatus)
                FuncResult = -2
            # write col value : unselect all columns
            VErr = PM0SC.FCmdSetWrReg ( PM0SC.TRegId.CONF_COL.value, VRegOp, VPrePostOp, VPrePostParam, [128] )
            
            # set the bitmap to the matrix
            for Col in range (54):
                # write col value :
                VErr = PM0SC.FCmdSetWrReg ( PM0SC.TRegId.CONF_COL.value, VRegOp, VPrePostOp, VPrePostParam, [Col] )
                VStatus = "Write col, Reg op = {:s} - Write error = {:d}".format (VGStrRegOp[VRegOp], VErr)
                if VErr >= 0:
                    logger.debug(VStatus)
                else:
                    logger.error(VStatus)
                    FuncResult = -2
                for Row in range(128):
                    #logger.info("Pixel[{},{}]".format(Row,Col))
                    if BitMap[Row,Col] == 1:
                        if ConnectedPixelsBitmap[Row,Col] == 1:
                            # write row value :
                            VErr = PM0SC.FCmdSetWrReg ( PM0SC.TRegId.PIX_CONF_ROW.value, VRegOp, VPrePostOp, VPrePostParam, [Row] )
                            VStatus = "Write row, Reg op = {:s} - Write error = {:d}".format (VGStrRegOp[VRegOp], VErr)
                            if VErr >= 0:
                                logger.debug(VStatus)
                            else:
                                logger.error(VStatus)
                                FuncResult = -2
                            # Set data to pixel : MSB at 1 and bit 6 at 1
                            VErr = PM0SC.FCmdSetWrReg ( PM0SC.TRegId.CONF_DATA.value, VRegOp, VPrePostOp, VPrePostParam, [VPulsingReg] )
                            VStatus = "write pixel reg value, Reg op = {:s} - Write error = {:d}".format (VGStrRegOp[VRegOp], VErr)
                            if VErr >= 0:
                                logger.debug(VStatus)
                            else:
                                logger.error(VStatus)
                                FuncResult = -2
                            print("Hit No:{:d} out of {:d}".format(HitIndex,HitNb))
                            HitIndex += 1
                        else:
                            # Pixel selected is dummy !!
                            UnconnectedNb += 1
                            BitMap[Row,Col] = 0
                            logger.error('Pixel Row:{:d}, Col:{:d} is a dummy pixel , total {:d} dummies pixels!!'.format(Row,Col,UnconnectedNb))

            # deselect all col : write 0x80 in col_cfg
            VErr = PM0SC.FCmdSetWrReg ( PM0SC.TRegId.CONF_COL.value, VRegOp, VPrePostOp, VPrePostParam, [0x80] )
            VStatus = "Write col, Reg op = {:s} - Write error = {:d}".format (VGStrRegOp[VRegOp], VErr)
            #print the bitmap
            FPrintBitmap(BitMap)

            if VErr >= 0:
                logger.debug(VStatus)
            else:
                logger.error(VStatus)
                FuncResult = -2

            # set the sequencer registers
#  MS 18 05 22  test the increasing of the frame size            
#            VErr = PM0SC.FCmdSetWrReg ( PM0SC.TRegId.PIX_SEQ.value, VRegOp, VPrePostOp, VPrePostParam, [0,0,0,0,0,16,2,3,0,1,12,1,100,12,251,255,0,0,55,67,3,4,36,37] )
            VErr = PM0SC.FCmdSetWrReg ( PM0SC.TRegId.PIX_SEQ.value, VRegOp, VPrePostOp, VPrePostParam, [0,0,0,0,0,100,2,3,0,1,0,0,200,12,251,255,0,0,55,67,3,4,200,201] )
            VStatus = "Reg op = {:s} - Write error = {:d}".format (VGStrRegOp[VRegOp], VErr)
            if VErr >= 0:
                logger.debug(VStatus)
            else:
                logger.error(VStatus)
                FuncResult = -2
            # Set Global command to 0x08 (soft start)
            VErr = PM0SC.FCmdSetWrReg ( PM0SC.TRegId.GLB_CMD.value, VRegOp, VPrePostOp, VPrePostParam, [8] )
            VStatus = "Reg op = {:s} - Wr val = {:X} Hex - Write error = {:d}".format (VGStrRegOp[VRegOp], 8, VErr)
            if VErr >= 0:
                logger.debug(VStatus)
            else:
                logger.error(VStatus)
                FuncResult = -2

    return FuncResult, BitMap, HitIndex


def FLoadBitmapFromFile(FileName):
    ''' 
    ... 
    
    Loads a file and extract the bitmap fir picmic matrix
    
    Param
    - FileName      = Name of the file from which extract the bitfile
    
    Returns
    - An error code, 0 => OK, < 0 => error
    - BitMap = numpy 128 * 54 array
    - HitNb = numbres of hit in the matrix
    
    14/02/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI    
    
    '''
    #global BitMap
    logger = logging.getLogger('pm0_emul')
    #BitMap = []
    BitMap = np.zeros(shape=(128,54),dtype=int)
    RowIndex = ct.c_int(0)
    ColIndex = ct.c_int(0)
    
    HitNb = 0
    try:
        # Open the file
        with open(FileName,"r") as infile:
            RowIndex.value = 0
            for line in infile:
                #BitMapLine = []
                if line[0] == ':':
                    #comment line : line ignored
                    print("")
                else:
                    ColIndex.value = 0
                    #bitmap line
                    for ColLineIndex in range (len(line)):
                        if line[ColLineIndex] in ["0","1"]:
                            #BitMapLine.append(int(line[ColIndex]))
                            BitMap[RowIndex.value,ColIndex.value] = int(line[ColLineIndex])
                            if line[ColLineIndex] in ["1"]:
                                HitNb += 1
                            ColIndex.value += 1
                    RowIndex.value += 1 
        Result = 0
    except IOError as e:
        print ("I/O error({0}): {1}".format(e.errno, e.strerror))
        logger.error("I/O error({0}): {1}".format(e.errno, e.strerror))
        Result = -1
    except: #handle other exceptions such as attribute errors
        print ("Unexpected error:", sys.exc_info()[0])
        logger.error ("Unexpected error:", sys.exc_info()[0])
        print ("RowIndex:{:d}".format(RowIndex.value))
        print ("ColIndex:{:d}".format(ColIndex.value))
        Result = -2
    logger.info("FLoadBitmapFromFile done,result:{:d}".format(Result))
    return Result, BitMap, HitNb




def FGetCommentsFromFile(FileName):
    ''' 
    ... 
    
    Loads a file and extract the comments of it
    
    Param
    - FileName      = Name of the file from which extract the bitfile
    
    Returns
    - An error code, 0 => OK, < 0 => error
    - Comments = a multline string
    
    14/02/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI    
    
    '''
    logger = logging.getLogger('pm0_emul')
    CommentsFromFile = ""
    try:
        # Open the file
        with open(FileName,"r") as infile:
            for line in infile:
                if line[0] == ':':
                    #comment line : line added to comments
                    CommentsFromFile = CommentsFromFile.__add__(line[1:])
                    #CommentFromFile.append (line[1:])
                    #logger.info("comment:{}".format(CommentFromFile))
        Result = 0
    except IOError as e:
       print ("I/O error({0}): {1}".format(e.errno, e.strerror))
       logger.error("I/O error({0}): {1}".format(e.errno, e.strerror))
       Result = -1
    except: #handle other exceptions such as attribute errors
       print ("Unexpected error:", sys.exc_info()[0])
       logger.error ("Unexpected error:{}".format(sys.exc_info()[0]))
       Result = -2
    logger.info("FGetCommentsFromFile done,result:{:d}".format(Result))
    return Result, CommentsFromFile



def FPrintBitmap(EntBitMap):
    ''' 
    ... 
    
    Loads a file and extract the bitmap fir picmic matrix
    
    Param
    - FileName      = Name of the file from which extract the bitfile
    
    Returns
    - An error code, 0 => OK, < 0 => error
    - BitMap = numpy 128 * 54 array
    - HitNb = numbres of hit in the matrix
    
    14/02/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI    
    
    '''
    logger = logging.getLogger('pm0_emul')
    #global BitMap
    #if EntBitMap == []:
    #    EntBitMap = BitMap
    #    logger.info("Using the global BitMap var")
    #else:
    #    logger.info("Using the BitMap param")
    
    TotalHitNb = 0
    for Col in range (54):
        for Row in range(128):
            if (EntBitMap[Row,Col]) == 1:
                TotalHitNb +=1
                print ("hit nb:{:d}, col :{:d}, row:{:d}, result:{:d}(d) / {:x} (x)".format(TotalHitNb,Col,Row,((Col+0)*128)+Row+0,((Col+0)*128)+Row+0))
                logger.info("hit nb:{:d}, col :{:d}, row:{:d}, result:{:d}(d) / {:x} (x)".format(TotalHitNb,Col,Row,((Col+0)*128)+Row+0,((Col+0)*128)+Row+0))
    return 0


def FTestPicMicI2CTrans(Param,VRegOp,VPrePostOp, VPrePostParam):
    '''
    ...
    
    - sends a bunch of transmissions
    
    Param
    - Param : selection of the way to treat the bitmap
        - 0 : set all pixels of the matrix, even the one not selected
        - 1 : set only the selected pixels
    
    Returns
        - Result: 0 if successfull, negative if failed
        - BitMap: two dimensions list ( 128 x 54 ) containing the  pixel matrix
        - HitNb: number of hits in the emulated matrix
    
    17/02/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI
    
    '''
    logger = logging.getLogger('pm0_emul')
    VErrorNb = 0
    VCompError = 0
 
    # set the bitmap to the matrix
    for Col in range (Param):
        # write col value :
#        VErr = PM0SC.FCmdSetWrReg ( PM0SC.TRegId.CONF_COL.value, VRegOp,0, 0, [Col%250] )
        VErr = PM0SC.FCmdSetWrReg ( PM0SC.TRegId.CONF_COL.value, VRegOp,VPrePostOp, VPrePostParam, [Col%255] )
        VStatus = "Write col:{:d}, Reg op = {:s} - Write error = {:d}".format (Col%255,VGStrRegOp[VRegOp], VErr)
        if VErr >= 0:
            logger.info(VStatus)
        else:
            logger.error(VStatus)
            VErrorNb += 1
            #retry once the writing
#            VErr = PM0SC.FCmdSetWrReg ( PM0SC.TRegId.CONF_COL.value, VRegOp,0, 0, [Col%250] )
            VErr = PM0SC.FCmdSetWrReg ( PM0SC.TRegId.CONF_COL.value, VRegOp,VPrePostOp, VPrePostParam, [Col%255] )
            VStatus = "Second try /Write col:{:d}, Reg op = {:s} - Write error = {:d}".format (Col%255,VGStrRegOp[VRegOp], VErr)
            if VErr >= 0:
                logger.info(VStatus)
            else:
                logger.error(VStatus)
                VErrorNb += 1
            
        #VARead = []
        # send the reset-I2C signal for WaitTime ms
#        WaitTime = 500
#        FSendResetI2CPulse(WaitTime)
            # read back the value
        VErr, VARead = PM0SC.FCmdGetRdReg ( PM0SC.TRegId.CONF_COL.value, VRegOp, VPrePostOp, VPrePostParam )
        if not VARead:
            # list empty
            logger.error("Read value empty")
            VErrorNb += 1
            
        else:
            if ((Col%255)!=VARead[0]):
                logger.error("Step :{:d}/{:d}  written value:{:d} / readback value :{}".format(Col,Param,Col%255,VARead))
                VCompError +=1
            else :
                logger.info("Step :{:d}/{:d}  written value:{:d} / readback value :{}".format(Col,Param,Col%255,VARead))
    # deselect all col : write 0x80 in col_cfg
    VErr = PM0SC.FCmdSetWrReg ( PM0SC.TRegId.CONF_COL.value, VRegOp,VPrePostOp, VPrePostParam, [0x80] )
    VStatus = "Write col, Reg op = {:s} - Write error = {:d}".format (VGStrRegOp[VRegOp], VErr)
    if VErr >= 0:
        logger.info(VStatus)
    else:
        logger.error(VStatus)
        VErrorNb += 1
    if (VErrorNb == 0) and (VCompError == 0):
        VStatus = "Test without errors  for {:d} transmissions".format (Param)
        logger.info("Test without errors  for {:d} transmissions".format (Param))
    
    else:
        VStatus = "Test with errors , total err nb : {:d} , comp errors : {:d} for {:d} transmissions".format (VErrorNb,VCompError,Param)
        logger.error("Test with errors , total err nb : {:d} , comp errors : {:d} for {:d} transmissions".format (VErrorNb,VCompError,Param))
    return VStatus


def FSendResetI2CPulse(Param):
    '''
    ...
    
    - send a pulse on the Reset_I2C pin
    
    Param
    - Param : Time to wait in ms between the rise and the fall of the reset-I2C signal
    
    Returns
        - Result: 0 if successfull, negative if failed
    
    22/02/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI
    
    '''
    logger = logging.getLogger('pm0_emul')
    VErr = 0
    if Param > 0 :
        # set the reset I2C signal
             
        # FCmdCtrlHwSig ( Cmd, RstSt, RstI2CSt, StartSt, TestmodeSt, PulseWidthUs )
         
        VErr = PM0SC.FCmdCtrlHwSig ( PM0SC.TCmdHwSig.SET_ST_RST_I2C.value, 0, 1, 0, 0, 0 )         
        VStatus = "Set RST_I2C = 1 - Error = {:d}".format (VErr)
        if VErr < 0:
            logger.error(VStatus) 
        # wait for Param ms
        sleep(Param/1000000.0)
        # Reset the reset I2C signal
             
        # FCmdCtrlHwSig ( Cmd, RstSt, RstI2CSt, StartSt, TestmodeSt, PulseWidthUs )
         
        VErr = PM0SC.FCmdCtrlHwSig ( PM0SC.TCmdHwSig.SET_ST_RST_I2C.value, 0, 0, 0, 0, 0 )         
        VStatus = "Set RST_I2C = 0 - Error = {:d}".format (VErr)
        if VErr < 0:
            logger.error(VStatus) 
        # wait for Param ms
        sleep(Param/1000.0)
    else:
        logger.debug("No reset I2C sent (WaitTime = 0)") 
 

def FExtractConnectedPixels(Filename):
    '''
    ...
    
    - extract the list of connected pixels from a file
    
    Param
    - Filename : Name of the file containing the connected pixels from picmic
    
    Returns
        - Result: matrix containing the connected pixels
    
    29/07/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI
    
    '''
    logger = logging.getLogger('pm0_emul')
    BitMap = np.zeros(shape=(128,54),dtype=int)

    try:
        logger.info("Bitmap: {}".format(BitMap))    
    except :
        logger.error("bitmap not existing")
            
            
    if (Filename.find('.csv')!= -1):
        logger.info("File is csv type")
        # Read the file
        with open (Filename,'r') as f:
            lines = f.readlines
        logger.info("File {:s} opened ".format(Filename))
        #file is csv file
        for line in lines:
            if line.find('D<')!= - 1:
                #Dummy pixel
                logger.debug("Dummy pixel !!") 
            else :
                #Connected pixel
                extrLine = re.findall(r'\d+',line)
                Col= int(extrLine[0],10)
                Row=int(extrLine[1],10)
                BitMap[Row,Col]=1
                
    elif (Filename.find('.txt') != -1):
        logger.info("File is txt type")
        # file is text file 
        # Extract the pixels coords from lines
        # Read the file
        with open (Filename,'r') as InFile:
            #                lines = f.readlines
            #logger.info("File {:s} opened ".format(Filename))
            for line in InFile:
                extrLine = re.findall(r'\d+',line)
                if extrLine != []:
                    Col= int(extrLine[0],10)
                    Row=int(extrLine[1],10)
                    BitMap[Row,Col]=1
                    #logger.info("extracted: col:{:d},Row{:d}".format(Col,Row))
                #else:
                    #logger.error("extracted data empty")
                    
    logger.info("BitMap: {}".format(BitMap))    
    return BitMap

        
if __name__ == "__main__" :

    FVersion (1)
