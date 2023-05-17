#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module containing the class for the high level functions for the picmic slow control software
  


 Version V1.5

 Versions list

 V1.0 09/09/2022 - MS
 V1.3 17/11/2022 - MS : added the return of result of the FConnectToDueBoard function
 V1.4 23/11/2022 - MS : added a param to the FConnectToDueBoard function
 V1.5 25/11/2022 - MS : modified the importing system : using a Modules.conf file to store the modules names to avoid the multiple name 

 
"""

# ===========================================================================
# Modules import
# ===========================================================================


import logging
import logging.config

import importlib
import configparser    # for the ini file configuration retrieving 

# retrieve the modules names from the Modules.conf file
config = configparser.ConfigParser(allow_no_value=True)
config.read("modules/Modules.conf")


PM0EMUL_Name = config['ModuleName']['emulFuncts']
PM0EMUL = importlib.import_module(PM0EMUL_Name, package=None)
#import mod_pm0_emul_func_11 as PM0EMUL


PM0SC_Name = config['ModuleName']['slowControlLowLevel']
PM0SC = importlib.import_module(PM0SC_Name, package=None)
#import mod_pm0_sc_24 as PM0SC

importlib.reload(PM0SC)
importlib.reload(PM0EMUL)



class Picmic_HighLevelFuncts():

    def __init__(self):
        """
            Constructor of the class
        """

        # For log level in Arduino DUE console
        self.VGLogRaw    = 0 # If 1 => it logs commands RAW data buffers in Arduino DUE console window
        self.VGLogCmd    = 0 # If 1 => it logs commands names and param in Arduino DUE console window
                # If 2 => it logs commands names, param and registers data in Arduino DUE console window
                
        # For error messages in PC Python console  
        self.VGLogErrMode = 2 # 0 = log and clear, 1 = print message and wait 5 seconds, 2 = print message and wait CR, 3 = let all message in console = dones't clear screen before menu printing
  
        # For registers operation
        self.VGRegOp     = PM0SC.TRegOp.CHK.value
        self.VGPrePostOp = PM0SC.TPrePostOp.NONE.value
        self.VGPrePostParam = PM0SC.TPrePostOp.NONE.value
        self.VGStrRegOp = ["SW","HW","CHECK"]


        # For PC/Arduino connection / deconnection
        self.VGUsbConnectErr = PM0SC.TErrUsb.CONNECT # Error USB connect , 0 => No error, -1 => Error
        self.VGDueConnected = False   # Flag to reject commands to DUE if PC is not connected to DUE

        # for picmic emulation 
        self.VGEmulFileName = "cfg_mat128x54_00.txt"

         #Init_Logging("sc_picmic_gc_21")
        #logging.config.fileConfig('logging/logging.conf')
        self.logger = logging.getLogger('pm0_hlf')
        self.logger.error('Logging Started')




    def CheckIfDueConnected(self) :
    # Check that DUE is connected

        if ( (self.VGDueConnected == False) and (Choice != 20) and (Choice != 100) ):
            VStatus = "Command rejected => Arduino DUE is not connected => Execute menu cmd 20"
            self.logger.error(VStatus)
            return ( False, False, VStatus ) # return ( VQuit, VBadCmd, VStatus )



    def FWrOneI2CRegs (self,RegAddr, RegAW8):
        """
            Write one I2C register
            
            param:
                - RegAddr : register address 
                - RegAW8 :  list of the registers values to set 

        17/05/2023 M.SPECHT CNRS/IN2P3/IPHC/C4PI
                
        """

        
        VErr = PM0SC.FCmdWrOneReg ( RegAddr, self.VGRegOp, self.VGPrePostOp, self.VGPrePostParam, RegAW8 )
        VStatus = "Reg op = {:s} - Write error = {:d}".format (self.VGStrRegOp[self.VGRegOp], VErr)
        if VErr >= 0:
            self.logger.info(VStatus)
        else:
            self.logger.error(VStatus)

        return VErr

          

    # Set GLB_CMD


    def FSetGlobalCommandReg (self,RegValueToSet) : 
        """
            Set Global command register
            
            param:
                - RegValueToSet : byte to send

        09/09/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI
                
        """
             

        VErr = PM0SC.FCmdSetWrReg ( PM0SC.TRegId.GLB_CMD.value, self.VGRegOp, self.VGPrePostOp, self.VGPrePostParam, [RegValueToSet] )
        VStatus = "Reg op = {:s} - Wr val = {:X} Hex - Write error = {:d}".format (self.VGStrRegOp[self.VGRegOp], RegValueToSet, VErr)
        if VErr >= 0:
            self.logger.info(VStatus)
        else:
            self.logger.error(VStatus)

      
        print ( "Status : {:s}".format (VStatus) )


        return VErr

    # Set PIX_SEQ 

    def FSetPixelSequencerRegs (self,ListValBytes):
        """
            Set Pixel sequencer registers
            
            param:
                - ListValBytes : list of the registers values to set (24 bytes)

        09/09/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI
                
        """


        self.logger.info("send bytes :{}".format(ListValBytes))

        VErr = PM0SC.FCmdSetWrReg ( PM0SC.TRegId.PIX_SEQ.value, self.VGRegOp, self.VGPrePostOp, self.VGPrePostParam, ListValBytes )
        VStatus = "Reg op = {:s} - Write error = {:d}".format (self.VGStrRegOp[self.VGRegOp], VErr)
        if VErr >= 0:
            self.logger.info(VStatus)
        else:
            self.logger.error(VStatus)
        return VErr


    # Set VPULSE_SW

    def FSetPulseSwitchRegs (self,ListVal):
        """
            Set Pulse switch registers
            
            param:
                - ListVal : list of the registers values to set (7 bytes)

        09/09/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI
                
        """


      
        
        VErr = PM0SC.FCmdSetWrReg ( PM0SC.TRegId.VPULSE_SW.value, self.VGRegOp, self.VGPrePostOp, self.VGPrePostParam, ListVal)
        VStatus = "Reg op = {:s} - Write error = {:d}".format (self.VGStrRegOp[self.VGRegOp], VErr)
        if VErr >= 0:
            self.logger.info(VStatus)
        else:
            self.logger.error(VStatus)
        return VErr


    # Set TEST_S_CTRL

    def FSetTestGlobBiasReg (self,VRegVal):
        """
            Set Test structure control / Global bias  register
            
            param:
                - VRegVal : byte to send

        09/09/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI
                
        """
     

        VErr = PM0SC.FCmdSetWrReg ( PM0SC.TRegId.TEST_S_CTRL.value, self.VGRegOp, self.VGPrePostOp, self.VGPrePostParam, [VRegVal] )
        VStatus = "Reg op = {:s} - Write error = {:d}".format (self.VGStrRegOp[self.VGRegOp], VErr)
        if VErr >= 0:
            self.logger.info(VStatus)
        else:
            self.logger.error(VStatus)
        return VErr




    # Set DAC_VAL

    def FSetDacRegs (self,ListDacRegs):
        """
            Set DAC  registers
            
            param:
                - ListDacRegs :  list of the registers values to set (5 bytes)

        09/09/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI
                
        """


        VErr = PM0SC.FCmdSetWrReg ( PM0SC.TRegId.DAC_VAL.value, self.VGRegOp, self.VGPrePostOp, self.VGPrePostParam, ListDacRegs )
        VStatus = "Reg op = {:s} - Write error = {:d}".format (self.VGStrRegOp[self.VGRegOp], VErr)
        if VErr >= 0:
            self.logger.info(VStatus)
        else:
            self.logger.error(VStatus)

        return VErr



    # Set DAC_SW

    def FSetDacSWRegs (self,ListDacSWRegs):
        """
            Set DAC SWitch  registers
            
            param:
                - ListDacSWRegs :  list of the registers values to set (3 bytes)

        09/09/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI
                
        """
     


        VErr = PM0SC.FCmdSetWrReg ( PM0SC.TRegId.DAC_SW.value, self.VGRegOp, self.VGPrePostOp, self.VGPrePostParam, ListDacSWRegs )
        VStatus = "Reg op = {:s} - Write error = {:d}".format (self.VGStrRegOp[self.VGRegOp], VErr)
        if VErr >= 0:
            self.logger.info(VStatus)
        else:
            self.logger.error(VStatus)
        return VErr


    # Set DATA_EMUL

    def FSetDataEmulReg (self,VRegVal):
        """
            Set Data emul  register
            
            param:
                - VRegVal :  registers value to set (1 byte)

        09/09/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI
                
        """

        VErr = PM0SC.FCmdSetWrReg ( PM0SC.TRegId.DATA_EMUL.value, self.VGRegOp, self.VGPrePostOp, self.VGPrePostParam, [VRegVal] )
        VStatus = "Reg op = {:s} - Write error = {:d}".format (self.VGStrRegOp[self.VGRegOp], VErr)
        if VErr >= 0:
            self.logger.info(VStatus)
        else:
            self.logger.error(VStatus)
        return VErr


    # Set PIX_CONF_ROW

    def FSetPixConfRowReg (self,VRegVal):
        """
            Set Pixel conf Row  register
            
            param:
                - VRegVal :  registers value to set (1 byte)

        09/09/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI
                
        """
     
        
        VErr = PM0SC.FCmdSetWrReg ( PM0SC.TRegId.PIX_CONF_ROW.value, self.VGRegOp, self.VGPrePostOp, self.VGPrePostParam, [VRegVal] )
        VStatus = "Reg op = {:s} - Write error = {:d}".format (self.VGStrRegOp[self.VGRegOp], VErr)
        if VErr >= 0:
            self.logger.info(VStatus)
        else:
            self.logger.error(VStatus)
        return VErr


    # Set CONF_COL

    def FSetPixConfColReg(self,VRegVal):
        """
            Set Pixel conf Col  register
            
            param:
                - VRegVal :  registers value to set (1 byte)

        09/09/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI
                
        """
     

        VErr = PM0SC.FCmdSetWrReg ( PM0SC.TRegId.CONF_COL.value, self.VGRegOp, self.VGPrePostOp, self.VGPrePostParam, [VRegVal] )
        VStatus = "Reg op = {:s} - Write error = {:d}".format (self.VGStrRegOp[self.VGRegOp], VErr)
        if VErr >= 0:
            self.logger.info(VStatus)
        else:
            self.logger.error(VStatus)
        return VErr


    # Set CONF_DATA

    def FSetPixConfDataReg(self,VRegVal):
        """
            Set Pixel conf Data  register
            
            param:
                - VRegVal :  registers value to set (1 byte)

        09/09/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI
                
        """

        
        VErr = PM0SC.FCmdSetWrReg ( PM0SC.TRegId.CONF_DATA.value, self.VGRegOp, self.VGPrePostOp, self.VGPrePostParam, [VRegVal] )
        VStatus = "Reg op = {:s} - Write error = {:d}".format (self.VGStrRegOp[self.VGRegOp], VErr)
        if VErr >= 0:
            self.logger.info(VStatus)
        else:
            self.logger.error(VStatus)
        return VErr





    # Get GLB_CMD

    def FGetGlobalCommandReg (self):
        """
            Get Global Command  register
            
            param:
                - none

            Returns
                VErr:   Error code for he execution of  the function :  - 0 : successfull
                                                                        - negative : failed
                VARead: read register value

        09/09/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI
               
        """


        VErr, VARead = PM0SC.FCmdGetRdReg ( PM0SC.TRegId.GLB_CMD.value, self.VGRegOp, self.VGPrePostOp, self.VGPrePostParam )
        if VErr >= 0:
            VStatus = "Read error = {:d} - Read value hex = {:x}".format (VErr, VARead[0] )
            self.logger.info(VStatus)
        else:
            VStatus = "Read error = {:d} ".format (VErr )
            self.logger.error(VStatus)
            
        return VErr, VARead



    # Get PIX_SEQ 

    def FGetPixelSequencerRegs (self):
        """
            Get Global Command  register
            
            param:
                - none
            Returns
                VErr:   Error code for he execution of  the function :  - 0 : successfull
                                                                        - negative : failed
                VARead: list of the read values ( 24 bytes)

        09/09/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI
                
        """


        VErr, VARead = PM0SC.FCmdGetRdReg ( PM0SC.TRegId.PIX_SEQ.value, self.VGRegOp, self.VGPrePostOp, self.VGPrePostParam )        
        VStatus = "Read error = {:d} - Read values dec = {}".format (VErr, VARead)
        self.logger.info("read bytes :{}".format(VARead))
        if VErr >= 0:
            self.logger.info(VStatus)
            VStatus = "Read error = {:d} - Read values dec = {}".format (VErr, VARead)
            self.logger.info("read bytes :{}".format(VARead))
        else:
            VStatus = "Read error = {:d} ".format (VErr)
            self.logger.error(VStatus)
            
        return VErr, VARead


    # Get VPULSE_SW

    def FGetPulseSwitcheRegs (self):
        """
            Get Pulse switches  register
            
            param:
                - none
            Returns
                VErr:   Error code for he execution of  the function :  - 0 : successfull
                                                                        - negative : failed
                VARead: list of the read values ( 3 bytes)

        09/09/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI
                
        """


        VErr, VARead = PM0SC.FCmdGetRdReg ( PM0SC.TRegId.VPULSE_SW.value, self.VGRegOp, self.VGPrePostOp, self.VGPrePostParam )
        VStatus = "Read error = {:d} - Read values dec = {}".format (VErr, VARead)
        if VErr >= 0:
            self.logger.info(VStatus)
        else:
            self.logger.error(VStatus)
            
        return VErr, VARead

    # Get TEST_S_CTRL

    def FGetTestGlobBiasReg (self):
        """
            Get Test structure and global bias  register
            
            param:
                - none
            Returns
                VErr:   Error code for he execution of  the function :  - 0 : successfull
                                                                        - negative : failed
                VARead:  read value ( 1 bytes)

        09/09/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI
                
        """


        VErr, VARead = PM0SC.FCmdGetRdReg ( PM0SC.TRegId.TEST_S_CTRL.value, self.VGRegOp, self.VGPrePostOp, self.VGPrePostParam )
        VStatus = "Read error = {:d} - Read values dec = {}".format (VErr, VARead)
        if VErr >= 0:
            self.logger.info(VStatus)
        else:
            self.logger.error(VStatus)
            
        return VErr, VARead


    # Get DAC_VAL

    def FGetDacRegs (self):
        """
            Get Dac  register
            
            param:
                - none
            Returns
                VErr:   Error code for he execution of  the function :  - 0 : successfull
                                                                        - negative : failed
                VARead: list of the read values ( 5 bytes)

        09/09/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI
                
        """


        VErr, VARead = PM0SC.FCmdGetRdReg ( PM0SC.TRegId.DAC_VAL.value, self.VGRegOp, self.VGPrePostOp, self.VGPrePostParam )
        VStatus = "Read error = {:d} - Read values dec = {}".format (VErr, VARead)
        if VErr >= 0:
            self.logger.info(VStatus)
        else:
            self.logger.error(VStatus)
            
        return VErr, VARead


    # Get DAC_SW

    def FGetDacSWRegs (self):
        """
            Get Dac switch register
            
            param:
                - none
            Returns
                VErr:   Error code for he execution of  the function :  - 0 : successfull
                                                                        - negative : failed
                VARead: list of the read values ( 3 bytes)

        09/09/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI
                
        """


        VErr, VARead = PM0SC.FCmdGetRdReg ( PM0SC.TRegId.DAC_SW.value, self.VGRegOp, self.VGPrePostOp, self.VGPrePostParam )
        VStatus = "Read error = {:d} - Read values dec = {}".format (VErr, VARead)
        if VErr >= 0:
            self.logger.info(VStatus)
        else:
            self.logger.error(VStatus)
            
        return VErr, VARead


    # Get DATA_EMUL

    def FGetDataEmulReg (self):
        """
            Get Data emul  register
            
            param:
                - none
            Returns
                VErr:   Error code for he execution of  the function :  - 0 : successfull
                                                                        - negative : failed
                VARead:  read value ( 1 bytes)

        09/09/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI
                
        """


        VErr, VARead = PM0SC.FCmdGetRdReg ( PM0SC.TRegId.DATA_EMUL.value, self.VGRegOp, self.VGPrePostOp, self.VGPrePostParam )
        VStatus = "Read error = {:d} - Read values dec = {}".format (VErr, VARead)
        if VErr >= 0:
            self.logger.info(VStatus)
        else:
            self.logger.error(VStatus)
        return VErr, VARead


    # Get PIX_CONF_ROW 

    def FGetPixConfRowReg (self):
        """
            Get Pixel conf row  register
            
            param:
                - none
            Returns
                VErr:   Error code for he execution of  the function :  - 0 : successfull
                                                                        - negative : failed
                VARead:  read value ( 1 bytes)

        09/09/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI
                
        """



        VErr, VARead = PM0SC.FCmdGetRdReg ( PM0SC.TRegId.PIX_CONF_ROW.value, self.VGRegOp, self.VGPrePostOp, self.VGPrePostParam )
        VStatus = "Read error = {:d} - Read values dec = {}".format (VErr, VARead)
        if VErr >= 0:
            self.logger.info(VStatus)
        else:
            self.logger.error(VStatus)
            
        return VErr, VARead


    # Get CONF_COL

    def FGetPixConfColReg (self):
        """
            Get Pixel conf Col  register
            
            param:
                - none
            Returns
                VErr:   Error code for he execution of  the function :  - 0 : successfull
                                                                        - negative : failed
                VARead:  read value ( 1 bytes)

        09/09/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI
                
        """



        VErr, VARead = PM0SC.FCmdGetRdReg ( PM0SC.TRegId.CONF_COL.value, self.VGRegOp, self.VGPrePostOp, self.VGPrePostParam )
        VStatus = "Read error = {:d} - Read values dec = {}".format (VErr, VARead)
        if VErr >= 0:
            self.logger.info(VStatus)
        else:
            self.logger.error(VStatus)
            
        return VErr, VARead


    # Get CONF_DATA

    def FGetPixConfDataReg (self):
        """
            Get Pixel conf data  register
            
            param:
                - none
            Returns
                VErr:   Error code for he execution of  the function :  - 0 : successfull
                                                                        - negative : failed
                VARead:  read value ( 1 bytes)
                
        09/09/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI
                
        """

        VErr, VARead = PM0SC.FCmdGetRdReg ( PM0SC.TRegId.CONF_DATA.value, self.VGRegOp, self.VGPrePostOp, self.VGPrePostParam )
        VStatus = "Read error = {:d} - Read values dec = {}".format (VErr, VARead)
        if VErr >= 0:
            self.logger.info(VStatus)
        else:
            self.logger.error(VStatus)
            
        return VErr, VARead


    def ShowComPorts(self):
        print ( "" )
        import serial.tools.list_ports
        ports = list(serial.tools.list_ports.comports())
        for p in ports:
            print (p)



    # Connect  
    def FConnectToDueBoard (self,ComPortParam, dsrdtr = False):
        """
            Connect to the Due Board
            
            param:
                - ComPortParam : Com port to connect to
            Returns
                - VErr :  if 0 : connection successfull
                            -1 : connection already established, nothing done
                            -2 : Connection could not be established
                            any positive number : connection established, but communication errors with arduino board
                            
        09/09/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI
                
        """


        if (self.VGDueConnected == True): 
            # Already connected : abort connection
            VStatus = "Command rejected => Arduino DUE is ALREADY connected "
            self.logger.error(VStatus)
            #return ( False, False, VStatus ) # return ( VQuit, VBadCmd, VStatus )
            VErr = -1

        else:
            VUsbPort = ComPortParam
            self.VGUsbConnectErr = PM0SC.TErrUsb.CONNECT.value  # Sets error source, in case of function crash ;-), set to 0 by function if OK
            
            self.VGUsbConnectErr = PM0SC.FConnect ( VUsbPort , dsrdtr = dsrdtr )
            
            if ( self.VGUsbConnectErr == PM0SC.TErrUsb.OK.value ) :
                PM0SC.FCmdSetLog ( 0, 2 ) # FCmdSetLog ( LogRaw, LogCmd )
                PM0SC.FCmdActivateOutputs ( 0 ) # FCmdActivateOutputs ( LogRaw, LogCmd )
                self.VGDueConnected = True
                VStatus = "I2C master Arduino DUE is connected to port " + VUsbPort
                self.logger.info(VStatus)
                
                # resetting the reset signals
                VErr = 0
                 
                # FCmdCtrlHwSig ( Cmd, RstSt, RstI2CSt, StartSt, TestmodeSt, PulseWidthUs )
                 
                VErr = PM0SC.FCmdCtrlHwSig ( PM0SC.TCmdHwSig.SET_ST_ALL.value, 0, 0, 0, 0, 0 )         
                VStatus = "RST cleared - Error = {:d}".format (VErr)
                if VErr >= 0:
                    self.logger.info(VStatus)
                else:
                    self.logger.error(VStatus)
                
            else:
                self.logger.error('Could not connect to the Arduino due !!')
                VErr = -1
            
        return VErr



    def FDisconnectFromDueBoard (self):
        """
            Disconnect from the Due Board
            
            param:
                none
            Returns
                none
            
        09/09/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI
                
        """

        PM0SC.FCmdDeactivateOutputs ( 0 ) # FCmdDeactivateOutputs ( LogRaw, LogCmd )

        self.VGUsbConnectErr = PM0SC.TErrUsb.DISCONNECT.value  # Sets error source, in case of function crash ;-), set to 0 by function if OK
        self.VGUsbConnectErr = PM0SC.FDisconnect ()
        
        if ( self.VGUsbConnectErr == PM0SC.TErrUsb.OK.value ) :
            self.VGDueConnected = False
            VStatus = "I2C master Arduino DUE is disconnected"
            self.logger.info(VStatus)


    def FSetRegisterOpMode (self,RegOpParam):
        """
            Set the Register operation mode
            
            param:
                - RegOpParam : 0 : Software, all operation are made on the image of the registers in the memory
                               1 : Hardware, all the operation are made on the chip
                               2 : Check, all operation are made on the chip and each register written is read back and checked
            Returns
                nothing
            
        09/09/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI
                
        """
        
        self.VGRegOp = int (RegOpParam)

        VStatus = "Register operation mode sets to {:s}".format ( self.VGStrRegOp[self.VGRegOp] )
        self.logger.info(VStatus)


    def FSetDueConsoleLogLevel (self,LogRaw,LogCmd):
        ''' 
        Sends a command set log (PM0SC__CMD_SET_LOG) to Arduino
        
        Param
        - LogRaw      =  0 => No log, 1 => Log commands raw data request and answer buffer
        - LogCmd      =  0 => No log, 1 => Log cmd name, 2= Log cmd name + data, results
        
        Returns
        - An error code, 0 => OK, < 0 => error

        09/09/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI
        
        '''

        self.VGLogRaw    = LogRaw
        self.VGLogCmd    = LogCmd

        VErr = PM0SC.FCmdSetLog ( self.VGLogRaw, self.VGLogCmd ) # FCmdSetLog ( LogRaw, LogCmd )

        if ( VErr == 0 ) : 
            VStatus = "Log levels : Log raw = {:d} - Log cmd = {:d}".format ( self.VGLogRaw , self.VGLogCmd )
            self.logger.info(VStatus)
        
        else :
            VStatus = "Error : Set log level has failed !"
            self.logger.error(VStatus)
        return VErr


    def FSetPCLogErrMode (self,VLogErrMode): 
        ''' 
        Sets the log level on the PC side
        
        Param
        - LogRaw      =  0 => No log, 1 => Log commands raw data request and answer buffer
        - LogCmd      =  0 => No log, 1 => Log cmd name, 2= Log cmd name + data, results
        
        Returns
        nothing

        09/09/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI
        
        '''

     
        self.VGLogErrMode = VLogErrMode

        VStatus = "Error messages mode sets to {:d}".format (VLogErrMode)
        self.logger.info(VStatus)
         

    def FSetLoggingLevelSetting (self,VLogLevel):
        """
            Setting of the logging level

        Param

        - VLogLever      = Level to be used for the logging
                            0 : debug
                            1 : info
                            2 : warning
                            3 : error
                            4 : critical
        Return
        
            nothing
        09/09/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI
            
        """

        if VLogLevel == 0:
            logging.getself.logger('picmic0').setLevel(logging.DEBUG)
            logging.getself.logger('pm0_emul').setLevel(logging.DEBUG)
            logging.getself.logger('pm0_sc').setLevel(logging.DEBUG)
        elif VLogLevel == 1:
            logging.getself.logger('picmic0').setLevel(logging.INFO)
            logging.getself.logger('pm0_emul').setLevel(logging.INFO)
            logging.getself.logger('pm0_sc').setLevel(logging.INFO)
        elif VLogLevel == 2:
            logging.getself.logger('picmic0').setLevel(logging.WARNING)
            logging.getself.logger('pm0_emul').setLevel(logging.WARNING)
            logging.getself.logger('pm0_sc').setLevel(logging.WARNING)
        elif VLogLevel == 3:
            logging.getself.logger('picmic0').setLevel(logging.ERROR)
            logging.getself.logger('pm0_emul').setLevel(logging.ERROR)
            logging.getself.logger('pm0_sc').setLevel(logging.ERROR)
        elif VLogLevel == 4:
            logging.getself.logger('picmic0').setLevel(logging.CRITICAL)
            logging.getself.logger('pm0_emul').setLevel(logging.CRITICAL)
            logging.getself.logger('pm0_sc').setLevel(logging.CRITICAL)


    # 34 - reload the modules
    def FReloadImportedModules (self):
        """
            Reload the imported modules
        """

        importlib.reload(PM0SC)
        importlib.reload(PM0EMUL)
        #importlib.reload (PM0FC)
        self.logger.error("Modules reloaded")

    # Register operation mode

    def FSetPrePostOperationMode (self,PrePostOp, PrePostParam):
        """
            Setting of the pre/post operations behaviour

        Param

        - PrePostOp      = Pre/post operation
                            0 : no pre or post operation
                            1 : pre operation : Reset I2C
                            2 : post operation : repeat operation until successfull
        - PrePostParam  = param for the pre/post operation
                if pre operation : duration of the reset  in ms 
                if post operation: max retry
        09/09/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI
            
        """


        self.VGPrePostOp = PrePostOp
        self.VGPrePostParam = PrePostParam
        VStatus = "PrePost params set: op {:d} / parma:{:d}".format (self.VGPrePostOp ,self.VGPrePostParam ) 
        self.logger.info(VStatus)

    # 40 - Write doc defaults in ALL registers 

    def FWriteDocDefaultsAllRegs (self):
        ''' 
        Writes the doc default values in all registers
        
        Param
            none
        
        Returns
            nothing
        09/09/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI
        
        '''



        VErr = PM0SC.FCmdSetWrDef ( self.VGRegOp, self.VGPrePostOp, self.VGPrePostParam, PM0SC.TDefOp.DEF.value, 0 ) # FCmdSetWrDef ( RegOp, DefOp, DefVal )

        if ( VErr == 0 ) : 
            VStatus = "Write defaults done :-)"
            self.logger.info(VStatus)
        else :
            VStatus = "Write defaultsl has failed !"
            self.logger.error(VStatus)
        return VErr
        

    # 41 - Write one 8 bits value in ALL registers

    def FWriteOneByteInAllRegs (self,W8ValueToWrite):
        ''' 
        Writes one byte in all registers
        
        Param
            none
        
        Returns
            VErr:   Error code for he execution of  the function :  - 0 : successfull
                                                                        - negative : failed
        09/09/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI
        
        '''


        VErr = PM0SC.FCmdSetWrDef ( self.VGRegOp, self.VGPrePostOp, self.VGPrePostParam, PM0SC.TDefOp.VAL.value, W8ValueToWrite ) # FCmdSetWrDef ( RegOp, DefOp, DefVal )

        if ( VErr == 0 ) : 
            VStatus = "Write value {:x} hex in ALL registers done :-)".format ( W8ValueToWrite ) 
            self.logger.info(VStatus)
        
        else :
            VStatus = "Write value {:x} hex in ALL registers has failed !".format ( W8ValueToWrite ) 
            self.logger.error(VStatus)
        return VErr



    # 50 - Write current RAM image in ALL registers

    def FSendRAMImageinAllRegisters (self):
        ''' 
        Send the current RAM image to all registers
        
        Param
            none
        
        Returns
            VErr:   Error code for he execution of  the function :  - 0 : successfull
                                                                        - negative : failed
        09/09/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI
        
        '''


        VErr = PM0SC.FCmdWrAllReg ( self.VGRegOp, self.VGPrePostOp, self.VGPrePostParam )

        if ( VErr == 0 ) : 
            VStatus = "Write RAM image values to ALL registers done :-)" 
            self.logger.info(VStatus)
        
        else :
            VStatus = "Write RAM image values to ALL registers has failed !"
            self.logger.error(VStatus)
        return VErr



    # 51 - Read ALL registers to RAM image 

    def FReadAllRegisterToRAM (self):
        ''' 
        Read all registers values to RAM image
        
        Param
            none
        
        Returns
            VErr:   Error code for he execution of  the function :  - 0 : successfull
                                                                        - negative : failed
        09/09/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI
        
        '''



        VErr = PM0SC.FCmdRdAllReg ( self.VGRegOp, self.VGPrePostOp, self.VGPrePostParam )

        if ( VErr == 0 ) : 
            VStatus = "Read ALL registers to RAM image done :-)"
            self.logger.info(VStatus)
        
        else :
            VStatus = "Read ALL registers to RAM image has failed !"
            self.logger.error(VStatus)
        return VErr


    def FWriteByteInPixelMemory (self,VRowVal,VColVal,VDefVal):
        """
            Setting of the logging level

        Param

            - VRowVal      = Row index of the targeted pixel register
            - VColVal      = Col index of the targeted pixel register
            - VDefVal      = Value to write to the targeted pixel
        Return
        
            - VErr:   Error code for he execution of  the function :  - 0 : successfull
                                                                        - negative : failed
        09/09/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI
            
        """


        # write row value :1
        VErr = PM0SC.FCmdSetWrReg ( PM0SC.TRegId.PIX_CONF_ROW.value, self.VGRegOp, self.VGPrePostOp, self.VGPrePostParam, [VRowVal] )
        VStatus = "Write row, Reg op = {:s} - Write error = {:d}".format (self.VGStrRegOp[self.VGRegOp], VErr)
        if VErr >= 0:
            self.logger.info(VStatus)
        else:
            self.logger.error(VStatus)
        # write col value :1
        VErr = PM0SC.FCmdSetWrReg ( PM0SC.TRegId.CONF_COL.value, self.VGRegOp, self.VGPrePostOp, self.VGPrePostParam, [VColVal] )
        VStatus = "Write col, Reg op = {:s} - Write error = {:d}".format (self.VGStrRegOp[self.VGRegOp], VErr)
        if VErr >= 0:
            self.logger.info(VStatus)
        else:
            self.logger.error(VStatus)

        # Set data to pixel

        VErr = PM0SC.FCmdSetWrReg ( PM0SC.TRegId.CONF_DATA.value, self.VGRegOp, self.VGPrePostOp, self.VGPrePostParam, [VDefVal] )
        VStatus = "write pixel reg value, Reg op = {:s} - Write error = {:d}".format (self.VGStrRegOp[self.VGRegOp], VErr)
        if VErr >= 0:
            self.logger.info(VStatus)
        else:
            self.logger.error(VStatus)
        
        # deselect all col : write 0x80 in col_cfg
        VErr = PM0SC.FCmdSetWrReg ( PM0SC.TRegId.CONF_COL.value, self.VGRegOp, self.VGPrePostOp, self.VGPrePostParam, [0x80] )
        VStatus = "Write col, Reg op = {:s} - Write error = {:d}".format (self.VGStrRegOp[self.VGRegOp], VErr)
        if VErr >= 0:
            self.logger.info(VStatus)
        else:
            self.logger.error(VStatus)
      



    def FSetBitmapInPixMemFromFile (self,VParam,VEmulFileName,VPulsingReg,VNotPulsingReg):
        """
            Set a bitmap in the pixel memory, using data from a file

        Param

            - VParam             = 0 : send all pixels even the ones not set ( longer)
                                   1 : send only the pixels to be set (faster)
            - VEmulFileName      = Filename of the file to be used
        Return
            - FuncResult  result code for the execution of  the function :  - 0 : successfull
                                                                            - negative : failed
            - BitMap               : matrix containing the bitmap applied to the pixel matrix
            - CommentsFromFile     : string containing the comments explaining the bitmap property
            - HitNb                : Number of hits in the bitmap
            - VErr:   Error code for he execution of  the function :  - 0 : successfull
                                                                        - negative : failed
        09/09/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI
            
        """


        FuncResult, BitMap, HitNb = PM0EMUL.FSetBitMapFromFile(VParam,VEmulFileName,VPulsingReg,VNotPulsingReg,self.VGRegOp, self.VGPrePostOp, self.VGPrePostParam)
        Result, CommentsFromFile = PM0EMUL.FGetCommentsFromFile(VEmulFileName)
        
        return FuncResult, BitMap,CommentsFromFile, HitNb
     



    def FPrintBitmapLoadedFromFile (self):
        """
            Print the bitmap loaded from a file

        Param

            none
        Return
            nothing

        09/09/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI
            
        """
     
        PM0EMUL.FPrintBitmap([])



    def FTransmissionTests (self,VParam):
        '''
        
        - sends a bunch of transmissions through the I2C link
            register targeted : Pixel Conf Col
        
        Param
        - Param : Number of iterations
        
        Returns
            - VStatus: string containing the result of the test
        
        09/09/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI
        
        '''

        
        VStatus = PM0EMUL.FTestPicMicI2CTrans(VParam,self.VGRegOp,self.VGPrePostOp, self.VGPrePostParam)
        
        return VStatus



    def FGetOneRegFromPixelMemory (self,VRowVal,VColVal):
        '''
        
        - Read a single register from the pixel memory
        
        Param
        - VRowVal : Row of the pixel register wanted
        - VColVal : Col of the pixel register wanted
        
        Returns
            - VErr   :  Result of the function : 0 if successfull
                                                 1 if failed
            - VARead : Value read from the targeted register
        
        09/09/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI
        
        '''

        # write row value :VRowVal
        VErr = PM0SC.FCmdSetWrReg ( PM0SC.TRegId.PIX_CONF_ROW.value, self.VGRegOp, self.VGPrePostOp, self.VGPrePostParam, [VRowVal] )
        VStatus = "Write row, Reg op = {:s} - Write error = {:d}".format (self.VGStrRegOp[self.VGRegOp], VErr)
        if VErr >= 0:
            self.logger.info(VStatus)
        else:
            self.logger.error(VStatus)
        # write col value :VColVal
        VErr = PM0SC.FCmdSetWrReg ( PM0SC.TRegId.CONF_COL.value, self.VGRegOp, self.VGPrePostOp, self.VGPrePostParam, [VColVal] )
        VStatus = "Write col, Reg op = {:s} - Write error = {:d}".format (self.VGStrRegOp[self.VGRegOp], VErr)
        if VErr >= 0:
            self.logger.info(VStatus)
        else:
            self.logger.error(VStatus)

        # read pixel register
        VErr, VARead = PM0SC.FCmdGetRdReg ( PM0SC.TRegId.CONF_DATA.value, self.VGRegOp, self.VGPrePostOp, self.VGPrePostParam )
        VStatus = "Read error = {:d} - Read values hex = {}".format (VErr, VARead)
        if VErr >= 0:
            self.logger.info(VStatus)
        else:
            self.logger.error(VStatus)

        
        # deselect all col : write 0x80 in col_cfg
        VErr = PM0SC.FCmdSetWrReg ( PM0SC.TRegId.CONF_COL.value, self.VGRegOp, self.VGPrePostOp, self.VGPrePostParam, [0x80] )
        VStatus = "Write col, Reg op = {:s} - Write error = {:d}".format (self.VGStrRegOp[self.VGRegOp], VErr)
        if VErr >= 0:
            self.logger.info(VStatus)
        else:
            self.logger.error(VStatus)
     
        return VErr, VARead
        

    def FSetResetSignal (self,ResetLevel):
        '''
        
        Set the Reset steering signal
        
        Param
        - ResetLevel : level to be applied to the Reset signal
        
        Returns
            - VErr   :  Result of the function : 0 if successfull
                                                 1 if failed
        
        09/09/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI
        
        '''
        
        VErr = 0
         
        # FCmdCtrlHwSig ( Cmd, RstSt, RstI2CSt, StartSt, TestmodeSt, PulseWidthUs )
         
        VErr = PM0SC.FCmdCtrlHwSig ( PM0SC.TCmdHwSig.SET_ST_RST.value, ResetLevel, 0, 0, 0, 0 )         
        VStatus = "Set RST = {:d} - Error = {:d}".format (ResetLevel,VErr)
        if VErr >= 0:
            self.logger.info(VStatus)
        else:
            self.logger.error(VStatus)
        return VErr

    def FSetResetI2CSignal (self,Reset_I2C):
        '''
        
        Set the Reset_I2C steering signal
        
        Param
        - Reset_I2C : level to be applied to the Reset_I2C signal
        
        Returns
            - VErr   :  Result of the function : 0 if successfull
                                                 1 if failed
        
        09/09/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI
        
        '''

        
        VErr = 0
         
        # FCmdCtrlHwSig ( Cmd, RstSt, RstI2CSt, StartSt, TestmodeSt, PulseWidthUs )
         
        VErr = PM0SC.FCmdCtrlHwSig ( PM0SC.TCmdHwSig.SET_ST_RST_I2C.value, 0, Reset_I2C, 0, 0, 0 )         
        VStatus = "Set RST_I2C = {:d} - Error = {:d}".format (Reset_I2C,VErr)
        if VErr >= 0:
            self.logger.info(VStatus)
        else:
            self.logger.error(VStatus)
        return VErr


    def FSetStartSignal (self,Start):
        '''
        
        Set the Start steering signal
        
        Param
        - Start : level to be applied to the Start signal
        
        Returns
            - VErr   :  Result of the function : 0 if successfull
                                                 1 if failed
        
        09/09/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI
        
        '''

        
        VErr = 0
         
        # FCmdCtrlHwSig ( Cmd, RstSt, RstI2CSt, StartSt, TestmodeSt, PulseWidthUs )
         
        VErr = PM0SC.FCmdCtrlHwSig ( PM0SC.TCmdHwSig.SET_ST_START.value, 0, 0, Start, 0, 0 )         
        VStatus = "Set START = {:d} - Error = {:d}".format (Start,VErr)
        if VErr >= 0:
            self.logger.info(VStatus)
        else:
            self.logger.error(VStatus)
        return VErr


    def FSetTestModSignal (self,TestMod):
        '''
        
        Set the Testmod steering signal
        
        Param
        - TestMod : level to be applied to the Testmod signal
        
        Returns
            - VErr   :  Result of the function : 0 if successfull
                                                 1 if failed
        
        09/09/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI
        
        '''
        
        VErr = 0
         
        # FCmdCtrlHwSig ( Cmd, RstSt, RstI2CSt, StartSt, TestmodeSt, PulseWidthUs )
         
        VErr = PM0SC.FCmdCtrlHwSig ( PM0SC.TCmdHwSig.SET_ST_TESTMODE.value, 0, 0, 0, TestMod, 0 )         
        VStatus = "Set TESTMOD = {:d} - Error = {:d}".format (TestMod,VErr)
        if VErr >= 0:
            self.logger.info(VStatus)
        else:
            self.logger.error(VStatus)
        return VErr


    def FPulseResetSignal (self,PulseWidthUs):
        '''
        
        Pulse the Reset steering signal
        
        Param
        - PulseWidthUs : Width of the pulse un µs
        
        Returns
            - VErr   :  Result of the function : 0 if successfull
                                                 1 if failed
        
        09/09/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI
        
        '''

        print ( "" )              
        
        VErr = 0
         
        # FCmdCtrlHwSig ( Cmd, RstSt, RstI2CSt, StartSt, TestmodeSt, PulseWidthUs )
         
        VErr = PM0SC.FCmdCtrlHwSig ( PM0SC.TCmdHwSig.PULSE_RST.value, 0, 0, 0, 0, PulseWidthUs )         
        VStatus = "Pulse RST - Error = {:d}".format (VErr)
        if VErr >= 0:
            self.logger.info(VStatus)
        else:
            self.logger.error(VStatus)
        return VErr


    def FPulseReset_I2CSignal (self,PulseWidthUs):
        '''
        
        Pulse the Reset_I2C steering signal
        
        Param
        - PulseWidthUs : Width of the pulse un µs
        
        Returns
            - VErr   :  Result of the function : 0 if successfull
                                                 1 if failed
        
        09/09/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI
        
        '''
        
        VErr = 0
         
        # FCmdCtrlHwSig ( Cmd, RstSt, RstI2CSt, StartSt, TestmodeSt, PulseWidthUs )
         
        VErr = PM0SC.FCmdCtrlHwSig ( PM0SC.TCmdHwSig.PULSE_RST_I2C.value, 0, 0, 0, 0, 500 )         
        VStatus = "Pulse RST_I2C - Error = {:d}".format (VErr)
        if VErr >= 0:
            self.logger.info(VStatus)
        else:
            self.logger.error(VStatus)
        return VErr


    def FPulseStartSignal (self,PulseWidthUs):
        '''
        
        Pulse the Start steering signal
        
        Param
        - PulseWidthUs : Width of the pulse un µs
        
        Returns
            - VErr   :  Result of the function : 0 if successfull
                                                 1 if failed
        
        09/09/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI
        
        '''
        
        VErr = 0
         
        # FCmdCtrlHwSig ( Cmd, RstSt, RstI2CSt, StartSt, TestmodeSt, PulseWidthUs )
         
        VErr = PM0SC.FCmdCtrlHwSig ( PM0SC.TCmdHwSig.PULSE_START.value, 0, 0, 0, 0, 1500 )         
        VStatus = "Pulse START - Error = {:d}".format (VErr)
        if VErr >= 0:
            self.logger.info(VStatus)
        else:
            self.logger.error(VStatus)
        return VErr




    def FReadPrintSteeringSignals (self):
        '''
        
        Pulse the Start steering signal
        
        Param
        - PulseWidthUs : Width of the pulse un µs
        
        Returns
            - VErr   :  Result of the function : 0 if successfull
                                                 1 if failed
        
        09/09/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI
        
        '''
        
        VErr = 0
         
        # FCmdCtrlHwSig ( Cmd, RstSt, RstI2CSt, StartSt, TestmodeSt, PulseWidthUs )
         
        VErr = PM0SC.FCmdCtrlHwSig ( PM0SC.TCmdHwSig.GET_PRINT_ST.value, 0, 0, 0, 0, 0 )         
        VStatus = "Get RST = b0 = {:d}, RST_I2C = b1 = {:d}, Start = b2 = {:d}, TestMod = b3 = {:d} - Error < 0 / Sig states >= 0 = {:d}".format ((VErr & 0x01), (VErr & 0x02) >> 1, (VErr & 0x04) >> 2, (VErr & 0x08) >> 3, VErr)
        if VErr >= 0:
            self.logger.info(VStatus)
        else:
            self.logger.error(VStatus)
        return VErr, VStatus


    def FResetPixelMemoryMatrix(self,ResetValue):
        '''
        
        Reset the pixel memory matrix
        
        Param
            none
        
        Returns
            - VErr   :  Result of the function : 0 if successfull
                                                 1 if failed
        
        09/09/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI
        
        '''


        VErr = PM0SC.FResetPixelMatrix(ResetValue,self.VGRegOp, self.VGPrePostOp, self.VGPrePostParam)
        VStatus = "Reset pixel memory - Error = {:d}".format (VErr)
        if VErr >= 0:
            self.logger.info(VStatus)
        else:
            self.logger.error(VStatus)
            
        return VErr





