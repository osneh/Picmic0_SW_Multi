#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Module containing the functions to allow to use the Analog Discovery 2 as an analog acquisition system
 V1.1 06 09 2022 MS : function modification in order to allow the use of this module with a GUI
 V1.2 24 11 2022 MS : modified the importing procedure in order to have one place to change the modules names in the project
 """



__author__ = "Mathias Grau, Thomas Lauber, Matthieu Specht"
__version__ = '0.1.2'
__maintainer__ = "Matthieu Specht"
__email__ = "matthieu.specht@iphc.cnrs.fr"
__date__ = "2022-11-25"

import importlib
import configparser    # for the ini file configuration retrieving 

import pyfirmata

from ctypes import *
from dwfconstants import *
import math
import time
import matplotlib.pyplot as plt
import sys
import numpy as np

import logging

import os
import datetime
from time import strftime

# retrieve the modules names from the Modules.conf file
config = configparser.ConfigParser(allow_no_value=True)
config.read("modules/Modules.conf")


PM0SC_Name = config['ModuleName']['slowControlLowLevel']
PM0SC = importlib.import_module(PM0SC_Name, package=None)

importlib.reload(PM0SC)


if sys.platform.startswith("win"):
    #Load the dynamic library on windows
    dwf = cdll.dwf
elif (sys.platform == "linux"):
    # Load the dynamic library on linux
    dwf = cdll.LoadLibrary("libdwf.so")

# =============================================================
# Settings
# =============================================================


global VGRes1        # resistor value for the Dacs 0,2,3
global VGRes2        # resistor value for the Dac 1

global VGNbrePtEch   # number of samples used for a single point
global VGFrEch       # Sampling frequency
global VGRange       # range of the analog inputs            

VGRes1 = 4700
VGRes2 = 4700
VGNbrePtEch = 8192   
VGFrEch = 100000  
VGRange = 1.0 

# =============================================================
# Functions
# =============================================================

def FSetPar(Res1,Res2,NbreEch,FrEch,Range):
    ''' 
    ... 
    
    Sets the parameters used for the DAC caracterisation
    
    Param
    - Res1     : Resistor value for the Dac0,2,3
    - Res2     : Resistor value for the Dac1
    - NbreEch  : Numbre of samples for each step
    - FrEch    : Sampling frequenc
    - Range    : Range of the analog inputs  of the Analog Discovery
    
    Returns
    - nothing
    
    09/12/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI    
    
    '''
    global VGRes1
    global VGRes2
    global VGNbrePtEch     
    global VGFrEch         
    global VGRange  
    
    VGRes1 = Res1
    VGRes2 = Res2
    VGNbrePtEch = NbreEch
    VGFrEch = FrEch
    VGRange = Range

def FResPar():
    ''' 
    ... 
    
    Resets the parameters used for the DAC caracterisation to the default value
    
    Param
    - none
    
    Returns
    - nothing
    
    09/12/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI    
    
    '''
    global VGRes1
    global VGRes2
    global VGNbrePtEch     
    global VGFrEch         
    global VGRange 
    
    VGRes1 = 4700
    VGRes2 = 4700
    VGNbrePtEch = 8192   
    VGFrEch = 100000  
    VGRange = 1 

def FConnect(UsbPortUno):
    ''' 
    ... 
    
    Connects to the Arduon Uno board
        ( used for the picmic emulation
    
    Param
    - ReUsbPortUnos1     : port on whoch the arduino uno board is conneted
    
    Returns
    - 0
    
    09/12/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI    
    
    '''    
    global VGUno
    
    VGUno = pyfirmata.Arduino(UsbPortUno)
    
    print("Communication Successfully started - Arduino VGUno obj created")
    
    return (0)

def FDisconnect():
    ''' 
    ... 
    
    Disconnect from the Arduino Uno board
    Param
    - none
    
    Returns
    - nothing
    
    09/12/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI    
    
    '''
    global VGUno
    
    VGUno.exit()
    
    del VGUno

def FCarac(VGRegOp, VGPrePostOp, VGPrePostParam, VGStrRegOp, VGUnoConnected):
    ''' 
    ... 
    
    Starts a dac caracterisation ( with an Arduino uno board to emulate the picmic chip)
    
    Param
    - VRegOp          =  Register operation mode
    - VPrePostOp     = Pre/post operatiion mode
    - VPrePostParam  = Pre/post operation param
    - VGStrRegOp     = user friendly name of the Register operation mode
    - VGUnoConnected = if 1 : the arduino uno board is connected
    
    Returns
    - status of the function
    
    09/12/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI    
    
    '''
    global VGUno
        
    VRegValDac = int(input("Write on the Dac number :  (Value between 0 and 4) "))  
    
    print('Valeur de truc : '+str(VGUnoConnected))
    time.sleep(2) 
    
    if VRegValDac < 4 :
        Channel = 1
    elif VRegValDac == 4 :
        Channel = 2
    elif VRegValDac > 4 :
        print("error please enter a value of Dac between 0 and 4 ")
        time.sleep(0.5)
        
    if VGUnoConnected == True :
        V_pinRelay = VGUno.get_pin('d:'+str(VRegValDac+2)+':o')
        V_pinRelay.write(1)
    
    print( " Please enter the parameters for acquisition / Values min = 0 max = 255 ")
    Start = int(input(" Values to start : "))
    Step = int(input(" Step values of the acquisition : "))
    Stop = int(input(" Values to stop : "))
    
    hdwf, Channel = FInit()
        
    LstRgdSamples = []
    LstValDac = [60,94,62,62,81]
    LstRegValDac = []
        
    for VRegValStr in range(Start, Stop + 1, Step):
        VRegVal = int ( str(VRegValStr+2), 10)
        LstValDac[VRegValDac] = VRegVal
        VErr = PM0SC.FCmdSetWrReg ( PM0SC.TRegId.DAC_VAL.value, VGRegOp, VGPrePostOp, VGPrePostParam, LstValDac )
        VStatus = "Reg op = {:s} - Write error = {:d}".format (VGStrRegOp[VGRegOp], VErr)
        rgdSamples = FAcquisition(hdwf, Channel)
        LstRgdSamples.append(rgdSamples)
        LstRegValDac.append(VRegVal)
        
    FCloseDevice()
    print (" Success ")
    
    PM0SC.FCmdSetWrReg ( PM0SC.TRegId.DAC_VAL.value, VGRegOp, VGPrePostOp, VGPrePostParam, [0, 0, 0, 0, 0] )
    
    Cond = input("Enter Y for save data or 'enter' to do nothing and erase the current acquisition")
    if Cond == 'Y' :
        FSeparation(LstRgdSamples, LstRegValDac, VRegValDac,1) 
    else :
        None
        
    if VGUnoConnected == True :
        V_pinRelay.write(0)
    
    return VStatus   



def FDacCarac(VGRegOp, VGPrePostOp, VGPrePostParam, VGStrRegOp):
    ''' 
    ... 
    
    Starts a dac caracterisation 
    
    Param
    - VRegOp          =  Register operation mode
    - VPrePostOp     = Pre/post operatiion mode
    - VPrePostParam  = Pre/post operation param
    - VGStrRegOp     = user friendly name of the Register operation mode
    - VGUnoConnected = if 1 : the arduino uno board is connected
    
    Returns
    - status of the function
    
    09/12/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI    
    
    '''        
    VRegValDac = int(input("Write on the Dac number :  (Value between 0 and 4) "))  
    
    
    if VRegValDac < 4 :
        Channel = 1
    elif VRegValDac == 4 :
        Channel = 2
    elif VRegValDac > 4 :
        print("error please enter a value of Dac between 0 and 4 ")
        time.sleep(0.5)
        
    
    print( " Please enter the parameters for acquisition / Values min = 0 max = 255 ")
    Start = int(input(" Values to start : "))
    Step = int(input(" Step values of the acquisition : "))
    Stop = int(input(" Values to stop : "))
    
    hdwf, Channel = FInit()
        
    LstRgdSamples = []
    LstValDac = [0,0,0,0,0]
    LstRegValDac = []
        
    for VRegValStr in range(Start, Stop + 1, Step):
        VRegVal = int ( str(VRegValStr+2), 10)
        LstValDac[VRegValDac] = VRegVal
        VErr = PM0SC.FCmdSetWrReg ( PM0SC.TRegId.DAC_VAL.value, VGRegOp, VGPrePostOp, VGPrePostParam, LstValDac )
        VStatus = "Reg op = {:s} - Write error = {:d}".format (VGStrRegOp[VGRegOp], VErr)
        rgdSamples = FAcquisition(hdwf, Channel)
        LstRgdSamples.append(rgdSamples)
        LstRegValDac.append(VRegVal)
        
    FCloseDevice()
    print (" Success ")
    
    PM0SC.FCmdSetWrReg ( PM0SC.TRegId.DAC_VAL.value, VGRegOp, VGPrePostOp, VGPrePostParam, [0, 0, 0, 0, 0] )
    
    Cond = input("Enter Y for save data or 'enter' to do nothing and erase the current acquisition")
    if Cond == 'Y' :
        FSeparation(LstRgdSamples, LstRegValDac, VRegValDac,1) 
    else :
        None
        
    
    return VStatus   



def FInit(ChannelA,ChannelB):
    ''' 
    ... 
    
    Initialise the Analog discovery device
    
    Param
    - ChannelA     =  Index of the Positive input channel
    - ChannelB     =  Index of the negative input channel
    
    Returns
    - hdwf         =  handle for the Analog discovery device
    - ChannelA     =  Index of the Positive input channel
    - ChannelB     =  ndex of the negative input channel
    
    09/12/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI    
    
    '''        


    global VGRange  
    cBufMax = c_int()
    logger = logging.getLogger('pm0_AD2')
    
    VDoubleIn = c_double()
    VIntIn = c_int()
    
    version = create_string_buffer(16)
    dwf.FDwfGetVersion(version)
    print("\nDWF Version: "+str(version.value))
    
    hdwf = c_int()
    
    print("\nOpening first device")
    dwf.FDwfDeviceOpen(c_int(-1), byref(hdwf))
    if hdwf.value == hdwfNone.value:
        szerr = create_string_buffer(512)
        dwf.FDwfGetLastErrorMsg(szerr)
        print(szerr.value)
        print("failed to open device")
        sys.exit()
    
    dwf.FDwfAnalogInBufferSizeInfo(hdwf, 0, byref(cBufMax))
    print("\nDevice buffer size: "+str(cBufMax.value))
    
    dwf.FDwfAnalogInFrequencySet(hdwf, c_double(float(VGFrEch)))
    dwf.FDwfAnalogInFrequencyGet(hdwf, byref(VDoubleIn))
    logger.info("\Analog Frequency : "+str(VDoubleIn.value))
    
    dwf.FDwfAnalogInBufferSizeSet(hdwf, c_int(int(VGNbrePtEch))) 
    dwf.FDwfAnalogInBufferSizeGet(hdwf, byref(VIntIn)) 
    logger.info("\Buffer size : "+str(VIntIn.value))
    
    # initialise the channel 0 or maybe all channels ???
    dwf.FDwfAnalogInChannelEnableSet(hdwf, c_int(-1), c_bool(True))
    #dwf.FDwfAnalogInChannelAttenuationSet(hdwf, c_int(-1),10)
    dwf.FDwfAnalogInChannelRangeSet(hdwf, c_int(-1), c_double(VGRange))
    dwf.FDwfAnalogInChannelRangeGet(hdwf, ChannelA, byref(VDoubleIn))
    logger.info("Channel A Input range : "+str(VDoubleIn.value))
    dwf.FDwfAnalogInChannelRangeGet(hdwf, ChannelB, byref(VDoubleIn))
    logger.info("Channel B Input range : "+str(VDoubleIn.value))
    dwf.FDwfAnalogInChannelFilterSet(hdwf, c_int(-1), filterDecimate)
    time.sleep(2)
    
    return hdwf, ChannelA, ChannelB


def FAcquisition(hdwf, Channel,currStep = 0,totStep=0):
    ''' 
    ... 
    
    Performs one step of acquisition
    
    Param
    - hdwf         =  handle for the Analog discovery device
    - Channel      =  Index of the input channel
    
    Returns
    - rgdSamples   =  list of the samples taken for this step of acquisition
    
    09/12/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI    
    
    '''        

    sts = c_byte()
    rgdSamplesx10 = (c_double*int(VGNbrePtEch))()
    rgdSamples = (c_double*int(VGNbrePtEch))()
    print("\nStarting oscilloscope...")
    dwf.FDwfAnalogInConfigure(hdwf, c_int(1), c_int(1))
    
    while True:
        dwf.FDwfAnalogInStatus(hdwf, c_int(1), byref(sts))
        if sts.value == DwfStateDone.value :
            break
    if totStep != 0:
        print("   Acquisition done step {} / {}".format(currStep,totStep))
    else:
        print("   Acquisition done")
    
    dwf.FDwfAnalogInStatusData(hdwf, int(Channel - 1), rgdSamplesx10, int(VGNbrePtEch))
    
    for Index in range (VGNbrePtEch):
        rgdSamples[Index] = 10 * rgdSamplesx10[Index]
    
    return rgdSamples


def FDualAcquisition(hdwf, ChannelA,ChannelB,currStep = 0,totStep=0):
    ''' 
    ... 
    
    Performs one step of differential acquisition 
    
    Param
    - hdwf         =  handle for the Analog discovery device
    - ChannelA      =  Index of the positive input channel
    - ChannelA      =  Index of the negative input channel
    - currStep      =  index of the current step of acquisition
    - totStep       =  Total number of steps for this acquisition
    
    Returns
    - rgdSamples   =  list of the samples taken for this step of acquisition
    
    09/12/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI    
    
    '''        

    sts = c_byte()
    rgdSamples = (c_double*int(VGNbrePtEch))()
    rgdSamplesA = (c_double*int(VGNbrePtEch))()
    rgdSamplesB = (c_double*int(VGNbrePtEch))()
    print("\nStarting oscilloscope...")
    dwf.FDwfAnalogInConfigure(hdwf, c_int(1), c_int(1))

    while True:
        dwf.FDwfAnalogInStatus(hdwf, c_int(1), byref(sts))
        if sts.value == DwfStateDone.value :
            break
    if totStep != 0:
        print("   Acquisition done step {} / {}".format(currStep,totStep))
    else:
        print("   Acquisition done")
    
    dwf.FDwfAnalogInStatusData(hdwf, int(ChannelA - 1), rgdSamplesA, int(VGNbrePtEch))
    dwf.FDwfAnalogInStatusData(hdwf, int(ChannelB - 1), rgdSamplesB, int(VGNbrePtEch))

    for Index in range (VGNbrePtEch):
        rgdSamples[Index] = 10 * (rgdSamplesA[Index] - rgdSamplesB[Index])
    return rgdSamples




def FCloseDevice():
    ''' 
    ... 
    
    Closes the Analog discovery device
    
    Param
    - none
    
    Returns
    - nothing
    
    09/12/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI    
    
    '''  
    dwf.FDwfDeviceCloseAll()


def FCalcul(rgdSamples):

    # ajouté une multiplication de 10 pour compenser la sonde *10 du scope
    dc = sum(rgdSamples)/len(rgdSamples)
    S_ET = 0
    for value in rgdSamples : #calcul de l'écart-type/rms
        S_ET += (value - dc)**2
        
        rms = np.sqrt((1/len(rgdSamples))*S_ET)
        
    return dc, rms


def FAffichageNormal(rgdSamples, Ind, FileOut, NAdc):
    
    x = np.arange(int(VGNbrePtEch))
    Minrgd = min(rgdSamples)
    Maxrgd = max(rgdSamples)

    if NAdc in [0,1,2,3]:
        # Units are Amps
        #graph1

        plt.plot(x, rgdSamples)
        plt.xlabel("$Samples$")
        plt.ylabel("$Current (mA)$")
        plt.xlim(0, int(VGNbrePtEch))
        plt.ylim(Minrgd, Maxrgd)
        plt.grid()
        
        plt.savefig(FileOut+"Dac"+str(NAdc)+"_"+str(Ind)+"_graph.jpg")
        
        plt.cla()
        
        #graph2
        
        plt.hist(rgdSamples, range = (Minrgd, Maxrgd), bins = 30, rwidth = 0.8)
        plt.xlabel("$Current (mA)$")
        plt.ylabel("$Occurences$")
        
        plt.savefig(FileOut+"Dac"+str(NAdc)+"_"+str(Ind)+"_histo.jpg")
        
        plt.cla()
    elif NAdc == 4:
        # Units are Amps
        #graph1

        plt.plot(x, rgdSamples)
        plt.xlabel("$Samples$")
        plt.ylabel("$Tension (V)$")
        plt.xlim(0, int(VGNbrePtEch))
        plt.ylim(Minrgd, Maxrgd)
        plt.grid()
        
        plt.savefig(FileOut+"Dac"+str(NAdc)+"_"+str(Ind)+"_graph.jpg")
        
        plt.cla()
        
        #graph2
        
        plt.hist(rgdSamples, range = (Minrgd, Maxrgd), bins = 30, rwidth = 0.8)
        plt.xlabel("$Tension (V)$")
        plt.ylabel("$Occurences$")
        
        plt.savefig(FileOut+"Dac"+str(NAdc)+"_"+str(Ind)+"_histo.jpg")
        
        plt.cla()


def FFctTrsf(lstDC, lstRMS, NbreTst, FileOut, LstRegValDac, NAdc):
        
    x = np.array(LstRegValDac)
    

    if NAdc in [0,1,2,3]:
        # Units are Amps

        #graph1
        
        MinDC = min(lstDC)
        MaxDC = max(lstDC)

        plt.plot(x, lstDC)
        plt.xlabel("$Code(DAC)$")
        plt.ylabel("$Current DC (mA)$")
        plt.xlim(0, max(LstRegValDac))
        plt.ylim(MinDC, MaxDC)
        plt.grid()
        
        plt.savefig(FileOut+"Dac"+str(NAdc)+"_graph_fct_DC.jpg")
        
        plt.cla()
        
        #graph2
        
        MinRMS = min(lstRMS)
        MaxRMS = max(lstRMS)

        plt.plot(x, lstRMS)
        plt.xlabel("$Code(DAC)$")
        plt.ylabel("$Current RMS (mA)$")
        plt.xlim(0, max(LstRegValDac))
        plt.ylim(MinRMS, MaxRMS)
        plt.grid()
        
        plt.savefig(FileOut+"Dac"+str(NAdc)+"_graph_fct_RMS.jpg")
        
        plt.cla()
    elif NAdc == 4:
        #Units are volts
        #graph1
        
        MinDC = min(lstDC)
        MaxDC = max(lstDC)

        plt.plot(x, lstDC)
        plt.xlabel("$Code(DAC)$")
        plt.ylabel("$Tension DC (V)$")
        plt.xlim(0, max(LstRegValDac))
        plt.ylim(MinDC, MaxDC)
        plt.grid()
        
        plt.savefig(FileOut+"Dac"+str(NAdc)+"_graph_fct_DC.jpg")
        
        plt.cla()
        
        #graph2
        
        MinRMS = min(lstRMS)
        MaxRMS = max(lstRMS)

        plt.plot(x, lstRMS)
        plt.xlabel("$Code(DAC)$")
        plt.ylabel("$Tension RMS (V)$")
        plt.xlim(0, max(LstRegValDac))
        plt.ylim(MinRMS, MaxRMS)
        plt.grid()
        
        plt.savefig(FileOut+"Dac"+str(NAdc)+"_graph_fct_RMS.jpg")
        
        plt.cla()



def FSeparation(LstRgdSamples, LstRegValDac, VRegValDac,SaveAllFiles):

    FName = 'Dac'+str(VRegValDac)+'_'
    DacName=['VrefP','VRefN','VBN','VBN_adj','VBP']
    LstDC = []
    LstRMS = []
    LstENOB = []
    date = datetime.datetime.now()
    Filedate = '{:%Y-%m-%d %H:%M:%S}'.format(date)
    Filedate = Filedate.replace(':','.')
    if (sys.platform == "linux"):
        FileOutName = str('Carac_Dac/'+DacName[VRegValDac] + Filedate)
        os.mkdir(FileOutName)
        
        FileOut = FileOutName+"/"
        
    else:
        FileOutName = str('Carac_Dac\\'+DacName[VRegValDac] + Filedate)
        os.mkdir(FileOutName)
        
        FileOut = FileOutName+"\\"
    
    txtDCRMS = ''
    
    lstDC = []
    lstRMS = []
    
    for Ind, RgdSamples in enumerate(LstRgdSamples) :
        texte = ''
        for ind, value in enumerate(RgdSamples):
            texte += (str(ind)+'  ' + str(value)+ '\n' )
        texte += "."+str(LstRegValDac[Ind])
        dc, rms= FCalcul(RgdSamples)
        txtDCRMS += (FName+str(LstRegValDac[Ind])+" DC: "+str(dc)+" V "+ "Valeur efficace : "+str(rms)+" V")
        
        #if VRegValDac == 0 or VRegValDac == 2 or VRegValDac == 3 :
        if VRegValDac in [0,2,3]:
            VCDac = dc/VGRes1
            txtDCRMS += ' Current: ' + str(VCDac) + ' A \n'
            
        elif VRegValDac == 1 :
            VCDac = dc/VGRes2
            txtDCRMS += ' Current: ' + str(VCDac) + ' A \n'
        elif VRegValDac == 4 :
            VCDac = dc
            txtDCRMS += ' Voltage: ' + str(VCDac) + ' V \n'
            
        elif VRegValDac == 5 :
            txtDCRMS += '\n'
        
        lstDC.append(VCDac)
        lstRMS.append(rms)
       
        if ( SaveAllFiles != 0 ):
            FAffichageNormal(RgdSamples, Ind, FileOut, VRegValDac)
        
        
        FWrite(texte, FName+'test'+str(Ind), FileOut)
        
        NbreTst = Ind + 1
    FWrite(txtDCRMS, FName+'Result_DC', FileOut)
    FFctTrsf(lstDC, lstRMS, NbreTst, FileOut, LstRegValDac, VRegValDac)   
    
    return lstDC,lstRMS


def NmF(NF, NAdc):

    if (sys.platform == "linux"):
        #path = 'P:\prj\win\picmic0\i2c\Analyse'
        NameFile = "chip_0_adc"+str(NAdc)+"_test"+str(NF)+".txt"
        
    else:
        path = 'P:\prj\win\picmic0\i2c\Analyse'
        NameFile = path + "\chip_0_adc"+str(NAdc)+"_test"+str(NF)+".txt"
    return NameFile


def FCptADC():

    for ind in range(5):
        if os.path.isfile(NmF(0, ind)) == True :
            LstRgdSamples, LstRegValDac = FFile(ind)
            FSeparation(LstRgdSamples, LstRegValDac, ind,1)


def FFile(NAdc):
    NF = 0
    LstRgdSamples = []
    LstRegValDac = []
    VNmF = NmF(NF, NAdc)
    while os.path.isfile(VNmF) == True :
        fichier = open(VNmF, 'r', encoding="utf8")
        RgdSamples = []
        for ligne in fichier :
            if ligne[0] != ".":
                ind = 0
                while ligne[ind] != ' ':
                    ind += 1
                value = float(ligne[(ind+1):-3])
                RgdSamples.append(value)
            else :
                LstRegValDac.append(ligne[1:])
        LstRgdSamples.append(RgdSamples)
        fichier.close()
        del fichier
        NF += 1
        VNmF = NmF(NF, NAdc)
        
    return LstRgdSamples, LstRegValDac


def FWrite(Text, FileName, FileOut):
    fichier = open(FileOut+FileName+".txt", "w", encoding = "utf8")
    fichier.write(str(Text))
    fichier.close



if __name__ == "__main__":
    if sys.platform.startswith("win"):
        dwf = cdll.dwf
