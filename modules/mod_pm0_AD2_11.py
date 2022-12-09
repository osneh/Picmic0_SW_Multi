#Module permettant de contenir les fonctions de l'AD2
# modifié le 06 09 2022 par MS pour pourvoir l'utiliser avec un GUI 
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
config.read("Modules.conf")


PM0SC_Name = config['ModuleName']['slowControlLowLevel']
#import mod_pm0_emul_func_11 as PM0EMUL # for the comment extracting of the pulsing files
PM0SC = importlib.import_module(PM0SC_Name, package=None)
#import mod_pm0_sc_23 as PM0SC

importlib.reload(PM0SC)


if sys.platform.startswith("win"):
    #Load the dynamic library on windows
    dwf = cdll.dwf
elif (sys.platform == "linux"):
    # Load the dynamic library on linux
    dwf = cdll.LoadLibrary("libdwf.so")
# =============================================================
# Declaration variables
# =============================================================

sts = c_byte()
pvoltsRange = c_double()
cBufMax = c_int()

# =============================================================
# Settings
# =============================================================


global VGRes1
global VGRes2 

global VGNbrePtEch              #nombre d'échantillons
global VGFrEch#fréquence d'échantillonage
global VGRange                   

VGRes1 = 10000
VGRes2 = 1000
VGNbrePtEch = 8192   
VGFrEch = 100000  
VGRange = 1.0 

# =============================================================
# Functions
# =============================================================

def FSetPar(Res1,Res2,NbreEch,FrEch,Range):
    global VGRes1
    global VGRes2
    global VGNbrePtEch     
    global VGFrEch         
    global VGRange  
    
    #print("VRes1 = "+ str(VGRes1)+" , VRes2 = "+ str(VGRes2) + " \n VGNbrePtEch = "+ str(VGNbrePtEch) + ", VGFrEch = "+ str(VGFrEch)+" , Range = " + str(VGRange))
    #Res1
    VGRes1 = Res1
    #VRes1 = input("Change the value of Res1 ? | Current = "+str(VGRes1)+ " Default = 10000 \n")
    #if VRes1 == '' or int(VRes1) == VGRes1 :
    #    None
    #else :
    #    VGRes1 = int(VRes1)
    #Res2  
    VGRes2 = Res2
    #VRes2 = input("Change the value of Res2 ? | Current = "+str(VGRes2)+ " Default = 1000 \n")
    #if VRes2 == '' or int(VRes2) == VGRes2 :
    #    None
    #else :
    #    VGRes2 = int(VRes2)
    #NbrePtEch
    VGNbrePtEch = NbreEch
    #VNbrePtEch = input("Change the value of VNbrePtEch ? | Current = "+str(VGNbrePtEch)+ " Default = 8192 | 8192 max  \n")
    #if VNbrePtEch == '' or int(VNbrePtEch) == VGNbrePtEch :
    #    None
    #else :
    #    VGNbrePtEch = int(VNbrePtEch)
    #FrEch
    VGFrEch = FrEch
    #VFrEch = input("Change the value of VFrEch ? | Current = "+str(VGFrEch)+ " Default = 100000 \n")
    #if VFrEch == '' or int(VFrEch) == VGFrEch :
    #    None
    #else :
    #    VGFrEch = int(VFrEch)
    #Range
    VGRange = Range
    #VRange= input("Change the value of VRange ? | Current = "+str(VGRange)+ " Default = 1 \n")
    #if VRange == '' or int(VRange) == VGRange :
    #    None
    #else :
    #    VGRange = int(VRange)
     
def FResPar():
    global VGRes1
    global VGRes2
    global VGNbrePtEch     
    global VGFrEch         
    global VGRange 
    
    VGRes1 = 10000
    VGRes2 = 1000
    VGNbrePtEch = 8192   
    VGFrEch = 100000  
    VGRange = 1 
    
def FConnect(UsbPortUno):
    
    global VGUno
    
    VGUno = pyfirmata.Arduino(UsbPortUno)
    
    print("Communication Successfully started - Arduino VGUno obj created")
    
    return (0)
    
def FDisconnect():

    global VGUno
    
    VGUno.exit()
    
    del VGUno
 
def FCarac(VGRegOp, VGPrePostOp, VGPrePostParam, VGStrRegOp, VGUnoConnected):
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
    global VGRange  
    logger = logging.getLogger('pm0_AD2')

    VDoubleIn = c_double()
    VIntIn = c_int()



    version = create_string_buffer(16)
    dwf.FDwfGetVersion(version)
    print("\nDWF Version: "+str(version.value))
    
    hdwf = c_int()
    #ChannelA = 1
    #ChannelB = 4
    
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
    
    #R = int(VGRange)
    
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
