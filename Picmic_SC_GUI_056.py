#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Slow control software for the chip = Picmic0
low level function written by Gilles Claus <gilles.claus@iphc.cnrs.fr>
GUI written by Hugo Schott and Matthieu Specht
Maintained by Matthieu Specht
"""

__author__ = "Hugo Schott,Matthieu Specht"
__version__ = '0.5.7'
__maintainer__ = "Matthieu Specht"
__email__ = "matthieu.specht@iphc.cnrs.fr"
__date__ = "2022-12-08"


# in order to use the Dac caracterisation feature, set the ANALOG_DISCOVERY_DISABLED to False
# But only if the Digilent software were installed on the system
ANALOG_DISCOVERY_DISABLED = False

#in order to use the DAQ function in the slow control software, set the DAQ_FUNC_ENABLED to True
DAQ_FUNC_ENABLED = True

import platform # for the detection of the OS version

import matplotlib
import matplotlib.pyplot as plt  
from matplotlib.figure import Figure

if platform.release() != 'XP':
    # os is not win XP : PyQt5 is used for the GUI
    from PyQt5 import QtGui, QtWidgets, QtCore
    from PyQt5.QtCore import pyqtSignal as Signal, pyqtSlot as Slot
    from PyQt5.QtWidgets import QApplication,QMainWindow,QFileDialog,QMessageBox,QPushButton, QVBoxLayout,QDialog
    from PyQt5.QtGui import QIcon
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
    print("PyQt version is PyQt5")
else:
    # os is win XP : PySide is used for the GUI
    matplotlib.use('Qt4Agg')
    matplotlib.rcParams['backend.qt4']='PySide'
    from PySide import QtGui,  QtCore
    from PySide.QtCore import Signal, Slot
    from PySide.QtGui import QFileDialog,QMessageBox,QPushButton, QVBoxLayout, QMainWindow, QApplication, QIcon,QDialog
    from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
    print("PyQt5 not available, using PySide")

import importlib
import os
import logging     # for the logging system 
import logging.config
import sys
import time
import math
import numpy as np
import ctypes as ct
import configparser    # for the ini file configuration retrieving 


LoggingFileName =  os.path.abspath(os.path.join(os.getcwd(),'logging','logging_SC.conf'))
try:
    logging.config.fileConfig(LoggingFileName)
except:
    print('Logging configuration failed')

try :
    from Picmic_SC_UI_COMPIL import Ui_MainWindow   # GUI made with QTDesigner, and compiled with pyuiside for win XP, pyuic5 otherwise
except : 
    print('error:{}, need to recompile the UI file'.format(sys.exc_info()[0]))
    import subprocess
    if (platform.release() == 'XP'):
        subprocess.call(["pyside-uic","./IHM/Picmic_SC_UI.ui","-o","Picmic_SC_UI_COMPIL.py"])
    else:
        subprocess.call(["pyuic5","./IHM/Picmic_SC_UI.ui","-o","Picmic_SC_UI_COMPIL.py"])
    print('Picmic_SC_UI_COMPIL script recompiled, retry the import of the script')
    from Picmic_SC_UI_COMPIL import Ui_MainWindow   # GUI made with QTDesigner, and compiled with pyuiside for win XP, pyuic5 otherwise
    

# retrieve the modules names from the Modules.conf file
config = configparser.ConfigParser(allow_no_value=True)
config.read("modules/Modules.conf")

# High level functions for the slow control for picmic
sc_p0_hlfName = config['ModuleName']['highLevelFuncts']
sc_p0_hlf= importlib.import_module(sc_p0_hlfName, package=None)
PicmicHLF = sc_p0_hlf.Picmic_HighLevelFuncts()

if platform.system() == "Windows":
    if (DAQ_FUNC_ENABLED == True ):
        # Acquisitions functions  for picmic
        PM0_DAQ_Func_Name = config['ModuleName']['daqFuncts']
        PM0_DAQ_Func= importlib.import_module(PM0_DAQ_Func_Name, package=None)
        PM0_DF = PM0_DAQ_Func.Picmic_DAQ_Functs()
    else:
        print("DAQ func not enabled")
else:
    print("Linux system : DAQ functions not enabled")
    
# for the comment extracting of the pulsing files
PM0EMUL_Name = config['ModuleName']['emulFuncts']
PM0EMUL= importlib.import_module(PM0EMUL_Name, package=None)
importlib.reload(PM0EMUL)

if ((platform.release() != 'XP')and(ANALOG_DISCOVERY_DISABLED == False)):
    # for the DAC caracterisation
    AD2_Name = config['ModuleName']['analogDiscovery']
    AD2 = importlib.import_module(AD2_Name, package=None)
    importlib.reload(AD2)


class Picmic_SC_GUI_Class (QMainWindow ): 
    """
        Class Picmic_SC_GUI_Class 

        Class dealing with the GUI
        
        for the slow control of 
        
        the picmic chip
    """
    
    def __init__(self):
        """
            Constructor of the class
        """

        super(Picmic_SC_GUI_Class , self).__init__()
        ## ui : pointer on the GUI mainwindow
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        _translate = QtCore.QCoreApplication.translate  

        self.logger = logging.getLogger('pm0_GUI')
        
        #####  Variables of the class   #####
        self.config = configparser.ConfigParser(allow_no_value=True)
        #Binary words for DAC Page
        self.binary_input_DAC_Byte1 = 73
        self.binary_input_DAC_Byte2 = 180 
        self.binary_input_DAC_Byte3 = 1 
        #Binary Words for Pulse Switch page
        self.binary_input_VpulseSwitch1 = 0
        self.binary_input_VpulseSwitch2 = 0
        self.binary_input_VpulseSwitch3 = 0
        self.binary_input_VpulseSwitch4 = 0
        self.binary_input_VpulseSwitch5 = 0
        self.binary_input_VpulseSwitch6 = 0
        self.binary_input_VpulseSwitch7 = 0
        #Binary word for Global command
        self.binary_input_GlobalCommand = 0
        #Binary word for Test Struct
        self.binary_input_TestStruct = 0
        #Binary word for PixConf
        self.binary_input_PixConfData = 0
        self.byte_input_PixConfRow = 0
        self.byte_input_PixConfCol = 0
        #Intern variable. 0 if Target disconnected, 1 if connected
        self.TargetConnected = 0

        #Flags to knows when a value has been set

        self.Flag_Set_GlobalCmd = 0
        self.Flag_Set_PixelSequence = 0
        self.Flag_Set_TestStruct = 0
        self.Flag_Set_PixSeqCol = 0
        self.Flag_Set_PixSeqRow = 0
        self.Flag_Set_PixSeqData = 0
        self.Flag_Set_DAC = 0
        self.Flag_Set_DACSW = 0
        self.Flag_Set_VpulseSw = 0

        self.lstDC = []
        self.lstRMS = []
        self.LstRegValDac = []
        
        self.NextStep = ct.c_int(0)

        self.ui.actionOpen_Config_File.triggered.connect(self.MenuLoadPicmicConfFile)
        self.ui.actionAbout.triggered.connect(self.ShowAboutDialogBox)

        ########################################################################################################################
        ############################################ GUI initialisation  #############################################################
        ########################################################################################################################

        # Initialize the main window title
        self.setWindowTitle(_translate("MainWindow", "Picmic Slow Control software   ver: {:s} ".format(__version__)))
        # set the icon for the running
        self.setWindowIcon(QIcon('.\\icons\\C4PI.ico')) 
        self.ui.statusbar.setStyleSheet("QStatusBar{background:MidLight;color:black;font-weight:normal;}")      
        
        self.ui.statusbar.showMessage('GUI started',0) # le 0 est un temps en seconde 

        ########################################################################################################################
        ############################################ Main tab ####################################################
        ########################################################################################################################

        self.ui.push_disconnect.setEnabled(False) #Disable disconnect button while not connected 
        # Assign the function to the callback of the GUI elements
        self.ui.CoBMainAccessMode.activated.connect(self.AccessModeSelection)
        
        self.ui.CoBPrePostParam.activated.connect(self.PrePostParamSelection)

        self.ui.LblMainPostParam.hide()
        self.ui.LblMainPreParam.hide()
        
        self.ui.BtMainPrePostParamSend.clicked.connect(self.SendPrePostParams)
        
        self.ui.update.clicked.connect(self.UpdateClicked) 
        
        self.ui.push_connect.clicked.connect(self.ConnectButtonClicked) 
        self.ui.push_disconnect.clicked.connect(self.DisconnectButtonClicked) 
        
        self.ui.BtEndSoftware.clicked.connect(self.StopProgClicked)
        
        self.ui.Tab_Pages.currentChanged.connect(self.TabPageChanged)

        ########################################################################################################################
        ############################################ Configuration Tab  ################################################
        ########################################################################################################################

        self.ui.BtConfLoadFileSelection.clicked.connect(self.ConfigurationLoadFileSelection)
        self.ui.BtConfLoadLoadFile.clicked.connect(self.LoadSelectedConfigurationFile)
        self.ui.BtConfSaveConf.clicked.connect(self.SaveConfigurationFile)

        self.ui.BtConfSendConfToChip.clicked.connect(self.SendConfigurationToChip)
        
        ########################################################################################################################
        ############################################ Steering Tab  #####################################################
        ########################################################################################################################

        self.ui.coBSteerRstState.activated.connect(self.SteeringCoBResetActivated)
        self.ui.BtSteerRstToggle.clicked.connect(self.SteeringBtResetToggleClicked)
        self.ui.coBSteerRst_I2CState.activated.connect(self.SteeringCoBReset_I2CActivated)
        self.ui.BtSteerRst_I2CToggle.clicked.connect(self.SteeringBtReset_I2CToggleClicked)
        self.ui.coBSteerStartState.activated.connect(self.SteeringCoBStartActivated)
        self.ui.BtSteerStartToggle.clicked.connect(self.SteeringBtStartToggleClicked)
        self.ui.coBSteerTestmodState.activated.connect(self.SteeringCoBTestmodActivated)
        self.ui.BtSteerTestmodToggle.clicked.connect(self.SteeringBtTestmodToggleClicked)
   
        ########################################################################################################################
        ############################################ Registers Tab #####################################################
        ########################################################################################################################
   
        #   Global Command input Checkbox buttons definiton
        self.ui.Set_EnExtPulse_Global_Cmd.clicked.connect(self.EnExtPulse_Global_Cmd_Clicked)  
        self.ui.Set_ExtPulse_Global_Cmd.clicked.connect(self.Set_ExtPulse_Global_Cmd_Clicked) 
        self.ui.SetRstFrCnt_Global_Cmd.clicked.connect(self.SetRstFrCnt_Global_Cmd_Clicked) 
        self.ui.Set_StartSeq_Global_Cmd.clicked.connect(self.Set_StartSeq_Global_Cmd_Clicked) 
   
        self.ui.Text_Set_GlobalCmd.textChanged.connect(self.GlobalCmdTextChanged)
        #    Global Command Set/Get Buttons definition
        
        self.ui.Set_Button_Global_Cmd.clicked.connect(self.Set_Button_Global_Cmd_Clicked) 
        self.ui.Get_Global_Cmd.clicked.connect(self.Get_Global_Cmd_Clicked) 
   
        #   Pixel Sequence Checkbox/radio buttons definiton

        #Set Button
        self.ui.get_PixSeq.clicked.connect(self.get_PixSeq_Clicked)
        
        #Get Button
        self.ui.setPixSeq.clicked.connect(self.setPixSeq_Clicked)
        
        #   Test Structure buttons definiton
        #Set Button
        self.ui.Set_Button_Test_Struct.clicked.connect(self.Set_Button_Test_Struct_Clicked)
   
        #Get Button
        self.ui.Get_Test_Struct.clicked.connect(self.Get_Test_Struct_Clicked)
        
        #text
        self.ui.Text_Set_Test_Struct.textChanged.connect(self.TestStructTextChanged)
        
        #All Checkboxes
        self.ui.Set_SW0.clicked.connect(self.Set_SW0_Clicked)
        self.ui.Set_SW1.clicked.connect(self.Set_SW1_Clicked)
        self.ui.Set_EN_CM.clicked.connect(self.Set_EN_CM_Clicked)
        self.ui.Set_EN_CC.clicked.connect(self.Set_EN_CC_Clicked)
        self.ui.Set_ENA_CM1.clicked.connect(self.Set_ENA_CM1_Clicked)
        self.ui.Set_ENA_D2P.clicked.connect(self.Set_ENA_D2P_Clicked)
        self.ui.Set_ENA_D1P.clicked.connect(self.Set_ENA_D1P_Clicked)

        #   Pixel Conf Column buttons definiton
        
        #Set Button
        self.ui.Set_Button_Col_PixConf.clicked.connect(self.Set_Button_Col_PixConf_Clicked)
   
        #Get Button
        self.ui.Get_Col_PixConf.clicked.connect(self.Get_Col_PixConf_Clicked)
        
        # Reset matrix button
        self.ui.BtPixConfResetPixelMatrix.clicked.connect(self.ResetPixelMatrixMemories)
        #All Checkboxes
        self.ui.Radio_SelCol_PixConf.clicked.connect(self.Radio_SelCol_PixConf_Clicked)
        self.ui.Radio_SelAllCol_PixConf.clicked.connect(self.Radio_SelAllCol_PixConf_Clicked)
        self.ui.Radio_DeselAllCol_PixConf.clicked.connect(self.Radio_DeselAllCol_PixConf_Clicked)

        #   Pixel Conf ROW buttons definiton
         
        #Set Button
        self.ui.Set_Button_Row_PixConf.clicked.connect(self.Set_Button_Row_PixConf_Clicked)
   
        #Get Button
        self.ui.Get_Row_PixConf.clicked.connect(self.Get_Row_PixConf_Clicked)
        
        #All Checkboxes
        self.ui.Radio_SelRow_Row_PixConf.clicked.connect(self.Radio_SelRow_Row_PixConf_Clicked)
        self.ui.Radio_SelAllRow_Row_PixConf.clicked.connect(self.Radio_SelAllRow_Row_PixConf_Clicked)      
        
        #   Pixel Conf DATA buttons definiton
        
        #Set Button
        self.ui.Set_Button_Data_PixConf.clicked.connect(self.Set_Button_Data_PixConf_Clicked)
   
        #Get Button
        self.ui.Get_Data_PixConf.clicked.connect(self.Get_Data_PixConf_Clicked)
        
        self.ui.Text_Set_Data_PixConf.textChanged.connect(self.Text_Set_Data_PixConf_textChanged)
        #All Checkboxes
        self.ui.Set_IADJ_Data_PixConf.valueChanged.connect(self.Set_IADJ_Data_PixConf_Clicked) #/!\ 3 Bits 
        self.ui.Set_ENA_CM_Data_PixConf.clicked.connect(self.Set_ENA_CM_Data_PixConf_Clicked)   
        self.ui.Set_SW0_Data_PixConf.clicked.connect(self.Set_SW0_Data_PixConf_Clicked)   
        self.ui.Set_SW1_Data_PixConf.clicked.connect(self.Set_SW1_Data_PixConf_Clicked)   
        self.ui.Set_ENA_CC_Data_PixConf.clicked.connect(self.Set_ENA_CC_Data_PixConf_Clicked)   
        self.ui.Set_ActivateVpulse_Data_PixConf.clicked.connect(self.Set_ActivateVpulse_Data_PixConf_Clicked)   
            
        #    DAC 0 - 4 buttons definiton

        # Set Button 
        self.ui.Set_Button_All_DAC.clicked.connect(self.Set_Button_All_DAC_Clicked)
        #Get Button
        self.ui.Get_Button_All_DAC.clicked.connect(self.Get_Button_All_DAC_Clicked)
        
        #    DAC Switch buttons definiton
        
        self.ui.Set_All_Bytes_DacSwitch.clicked.connect(self.Set_All_Bytes_DacSwitch_Clicked)
        self.ui.Get_All_Bytes_DacSwitch.clicked.connect(self.Get_All_Bytes_DacSwitch_Clicked)
        
        #All checkboxes
        
        #Byte 1 
        self.ui.Set_en_bg_Byte1.clicked.connect(self.Set_en_bg_Byte1_Clicked)
        self.ui.Set_IREF_b0_Byte1.clicked.connect(self.Set_IREF_b0_Byte1_Clicked)
        self.ui.Set_IREF_b1_Byte1.clicked.connect(self.Set_IREF_b1_Byte1_Clicked)
        self.ui.Set_IREF_b2_Byte1.clicked.connect(self.Set_IREF_b2_Byte1_Clicked)
        self.ui.Set_ENA_IREF_ext_Byte1.clicked.connect(self.Set_ENA_IREF_ext_Byte1_Clicked)
        self.ui.Set_ENA_IP_Byte1.clicked.connect(self.Set_ENA_IP_Byte1_Clicked)
        self.ui.Set_ENA_IN_Byte1.clicked.connect(self.Set_ENA_IN_Byte1_Clicked)
        self.ui.Set_ENA_IP_ext_Byte1.clicked.connect(self.Set_ENA_IP_ext_Byte1_Clicked)
        self.ui.RegDacText_Set_Byte1.textChanged.connect(self.RegDacByte1TextChanged)
        #Byte 2
        self.ui.Set_ENA_IN_ext_Byte2.clicked.connect(self.Set_ENA_IN_ext_Byte2_Clicked)
        self.ui.Set_ENA_CM_ext_Byte2.clicked.connect(self.Set_ENA_CM_ext_Byte2_Clicked)
        self.ui.Set_ENA_Iadj_ext_Byte2.clicked.connect(self.Set_ENA_Iadj_ext_Byte2_Clicked)
        self.ui.Set_ENA_VBP_ext_Byte2.clicked.connect(self.Set_ENA_VBP_ext_Byte2_Clicked)
        self.ui.Set_ENA_IP_mes_Byte2.clicked.connect(self.Set_ENA_IP_mes_Byte2_Clicked)
        self.ui.Set_ENA_IN_mes_Byte2.clicked.connect(self.Set_ENA_IN_mes_Byte2_Clicked)
        self.ui.Set_ENA_CM_mes_Byte2.clicked.connect(self.Set_ENA_CM_mes_Byte2_Clicked)
        self.ui.Set_ENA_Iadj_mes_Byte2.clicked.connect(self.Set_ENA_Iadj_mes_Byte2_Clicked)
        self.ui.RegDacText_Set_Byte2.textChanged.connect(self.RegDacByte2TextChanged)
        #Byte 3
        self.ui.Set_ENA_VBP_PAD_Byte3.clicked.connect(self.Set_ENA_VBP_PAD_Byte3_Clicked)
        self.ui.RegDacText_Set_Byte3.textChanged.connect(self.RegDacByte3TextChanged)
        
        #   VPulse Switch buttons definiton
        
        self.ui.Set_Vpulse.clicked.connect(self.Set_Vpulse_Clicked) #Set Button
        self.ui.Reset_Vpulse.clicked.connect(self.Reset_Vpulse_Clicked)  #Reset button
        self.ui.ResetAll_Vpulse.clicked.connect(self.ResetAll_Vpulse_Clicked)    #ResetAll Button
        self.ui.Send_ByteState_Vpulse.clicked.connect(self.Send_ByteState_Vpulse_Clicked)
        self.ui.Get_ByteState_Vpulse.clicked.connect(self.Get_ByteState_Vpulse_Clicked)
   
        ########################################################################################################################
        ############################################ Pulsing Tab   #####################################################
        ########################################################################################################################

        self.ui.BtPulsingSendPulsingToChip.clicked.connect(self.SendPulsingToChip)
        self.ui.BtPulsingFileSelection.clicked.connect(self.PulsingFileSelection)
        
        self.ui.LEPulsingPPRegValue.textChanged.connect(self.LEPulsingPPRegValue_Changed)
        self.ui.SBPulsingPulsed_IADJ_Data_PixConf.valueChanged.connect(self.SBPulsingPulsed_IADJ_Data_PixConfValueChanged)
        self.ui.ChBPulsingPP_ENA_CM_Data_PixConf.clicked.connect(self.ChBPulsingPP_ENA_CM_Data_PixConf_Clicked)
        self.ui.ChBPulsingPP_SW0_Data_PixConf.clicked.connect(self.ChBPulsingPP_SW0_Data_PixConf_Clicked)
        self.ui.ChBPulsingPP_SW1_Data_PixConf.clicked.connect(self.ChBPulsingPP_SW1_Data_PixConf_Clicked)
        self.ui.ChBPulsingPP_ENA_CC_Data_PixConf.clicked.connect(self.ChBPulsingPP_ENA_CC_Data_PixConf_Clicked)
        self.ui.ChBPulsingPP_Act_Pulse_Data_PixConf.clicked.connect(self.ChBPulsingPP_Act_Pulse_Data_PixConf_Clicked)

        self.ui.LEPulsingNOTPRegValue.textChanged.connect(self.LEPulsingNOTPRegValue_Changed)
        self.ui.SBPulsingNOTPulsed_IADJ_Data_PixConf.valueChanged.connect(self.SBPulsingNOTPulsed_IADJ_Data_PixConfValueChanged)
        self.ui.ChBPulsingNOTP_ENA_CM_Data_PixConf.clicked.connect(self.ChBPulsingNOTP_ENA_CM_Data_PixConf_Clicked)
        self.ui.ChBPulsingNOTP_SW0_Data_PixConf.clicked.connect(self.ChBPulsingNOTP_SW0_Data_PixConf_Clicked)
        self.ui.ChBPulsingNOTP_SW1_Data_PixConf.clicked.connect(self.ChBPulsingNOTP_SW1_Data_PixConf_Clicked)
        self.ui.ChBPulsingNOTP_ENA_CC_Data_PixConf.clicked.connect(self.ChBPulsingNOTP_ENA_CC_Data_PixConf_Clicked)
        self.ui.ChBPulsingNOTP_Act_Pulse_Data_PixConf.clicked.connect(self.ChBPulsingNOTP_Act_Pulse_Data_PixConf_Clicked)
        
        if platform.release() != 'XP':
        # a figure instance to plot on
            self.figurePulsing = plt.figure()#constrained_layout=True)
            # add one plot to the figure
            self.plotPulsing = self.figurePulsing.add_subplot(111)# row = rows number = 1 , col = colunms number = 1, index = 1
            # this is the Canvas Widget that displays the `figure`
            # it takes the `figure` instance as a parameter to __init__
            self.canvasPulsing = FigureCanvas(self.figurePulsing)
            # this is the Navigation widget
            # it takes the Canvas widget and a parent
            self.toolbar = NavigationToolbar(self.canvasPulsing, self)
            # set the layout
            layoutPulsing = QVBoxLayout()
            layoutPulsing.addWidget(self.toolbar)
            layoutPulsing.addWidget(self.canvasPulsing,1)
            self.ui.GBPulsingPlottingWindow.setLayout(layoutPulsing)
        
        ########################################################################################################################
        ############################################ Dac caracterisation Tab   #########################################
        ########################################################################################################################
        
        
        self.ui.BtCarDacADPSetParams.clicked.connect(self.ADPSetParams)
        self.ui.BtCarDacRunCarac.clicked.connect(self.RunCaracterisation)
        self.ui.CoBCarDacPlotTypeSel.activated.connect(self.CarDacChangePottingType)
        
        self.ui.ChBCarDacStepByStep.clicked.connect(self.CarDacActivateStepByStep)

        if platform.release() != 'XP':

            # a figure instance to plot on
            self.figureCarDac = plt.figure()#constrained_layout=True)
            # add one plot to the figure
            self.plotCarDac = self.figureCarDac.add_subplot(111)# row = rows number = 1 , col = colunms number = 1, index = 1
            # this is the Canvas Widget that displays the `figure`
            # it takes the `figure` instance as a parameter to __init__
            self.canvasCarDac = FigureCanvas(self.figureCarDac)
            # this is the Navigation widget
            # it takes the Canvas widget and a parent
            self.toolbarCarDac = NavigationToolbar(self.canvasCarDac, self)
            # set the layout
            layoutCarDac = QVBoxLayout()
            layoutCarDac.addWidget(self.toolbarCarDac)
            layoutCarDac.addWidget(self.canvasCarDac)
            self.ui.GBCarDacPlottingWindow.setLayout(layoutCarDac)


        ########################################################################################################################
        ############################################ Discri caracterisation Tab   ##############################################
        ########################################################################################################################

        self.ui.BtCarDisRunCarac.clicked.connect(self.BtCarDisRunCaracClicked)
        self.ui.BtCarDisInitAcquisition.clicked.connect(self.CarDisInitAcq)
        self.ui.BtCarDisPathSel.clicked.connect(self.CarDisPathSelect)
        if (DAQ_FUNC_ENABLED == True ):
            pass
        else:
            self.ui.Tab_Pages.removeTab(self.ui.Tab_Pages.indexOf(self.ui.Carac_discri_tab))
            


    def MenuLoadPicmicConfFile(self):
        """
            Load configuration file called by menu
            NOT IMPLEMENTED YET
        """
        
        self.logger.info("menu open clicked")
        
        LoadResult = -1
        VFileName = ""

        VOldFilePath = os.path.join(os.getcwd(),  'Conf_files')

        VFDialog = QFileDialog(self)
        VFDialog.setWindowTitle('Open Conf file')
        VFDialog.setNameFilter('configuration Files (*.conf)')
        VFDialog.setDirectory(VOldFilePath)
        VFDialog.setFileMode(QFileDialog.ExistingFile)
        
        if VFDialog.exec_() == QtWidgets.QDialog.Accepted:
            VFileName = str(VFDialog.selectedFiles()[0])
            if os.path.isfile(VFileName):
                self.logger.info(VFileName)
                self.logger.info('directory:%s',str(VFDialog.directory().path()))

                config = configparser.ConfigParser(allow_no_value=True)
                config.read(VFileName)
                AuthorName= config['Comments']['author']
                self.logger.info('Author:{}'.format(AuthorName))
                # set the pixel sequencer regs
                self.ui.Set_FlushModule_PixSeq.setText('{:s}'.format( config['Pixel_Sequencer']['Flush_mod'] ))

                # if LoadResult == 0:
                    # self.logger.info ('File Reading successfull ')
                    # self.ui.LEMis1LoadSaveResult.setText('0000:File Reading successfull ')
                    # self.ui.LEMis1LoadSaveResult.setStyleSheet("QLineEdit { background-color: Midlight;color: black }")
                # else:
                    # self.logger.error ('File Reading FAILED ')
                    # self.ui.LEMis1LoadSaveResult.setText('-001:File Reading FAILED ')
                    # self.ui.LEMis1LoadSaveResult.setStyleSheet("QLineEdit { background-color: red;color: white }")
            else:
                self.logger.error('File does not exist :%s',VFileName)
        else:
            self.logger.error ('File Reading CANCELLED ')
            LoadResult = -5


    def showdialog(self,MessSelect):
        '''
        ...
        
        Shows a dialog to display a warning 
        
        Param
        - MessSelect : if 0 : Target is not connected
                       if 1 : Win XP => Dac caratcterisation is not possible
                       if 2 : AD2 board not enabled => Dac caratcterisation is not possible
        
        Returns
        - none
        
        08/12/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI
        
        '''

        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        if (MessSelect == 0):
            msg.setText("Your target is not connected")
            msg.setInformativeText("You must connect the target in order to access registers")
            msg.setWindowTitle("PICMIC Slow Control Warning")
            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            retval = msg.exec_()
        elif (MessSelect == 1):
            msg.setText("The OS is Win XP")
            msg.setInformativeText("The Dac caracterisation is not operationnal under win XP")
            msg.setWindowTitle("PICMIC Slow Control Warning")
            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            retval = msg.exec_()
        elif (MessSelect == 2):
            msg.setText("The analog discovery board is not enabled")
            msg.setInformativeText("The Dac caracterisation is not operationnal")
            msg.setWindowTitle("PICMIC Slow Control Warning")
            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            retval = msg.exec_()


    def ShowAboutDialogBox(self):
        """
            Called by the menu Misc - About
            pops a message window containing the informations about software author, version...
        """
        AboutDialogBox = QMessageBox(self)
        AboutDialogBox.setWindowTitle("About")
        AboutDialogBox.setText("Picmic Slow control software\nAuthors:{}\nVersion:{} @ {}\nMaintainer:{}\nEmail:{}".format(__author__,__version__,__date__,__maintainer__,__email__))
        pButtonOk = AboutDialogBox.addButton("Ok", QMessageBox.AcceptRole)
        AboutDialogBox.setDefaultButton(pButtonOk)
        #AboutDialogBox.setIconPixmap(QtGui.QPixmap(":/icons/C4PI.png"))
        AboutDialogBox.setIcon(QMessageBox.Information)
        AboutDialogBox.exec_()


    def TabPageChanged(self):
        """
            callback for the tab changed event
        """
        if self.TargetConnected == False:
            if self.ui.Tab_Pages.currentIndex() != 0: #If we're trying to access Registers pages without being connected
               self.showdialog(0)
               self.ui.statusbar.setStyleSheet("color : red")
               self.ui.statusbar.showMessage('You\'re not connected, cannot access registers',0) # le 0 est un temps en seconde 
               self.ui.Tab_Pages.setCurrentIndex(0)
        elif (self.ui.Tab_Pages.currentIndex() == 5):
            if (platform.release() == 'XP'): # if we are trying to do dac caracterisation on win XP 
               self.showdialog(1)
               self.ui.statusbar.setStyleSheet("color : red")
               self.ui.statusbar.showMessage('The OS is Windows XP\nUnder XP the Dac caracterisation is not operationnal',5000) # le 0 est un temps en milli-seconde 
               self.ui.Tab_Pages.setCurrentIndex(0)
            elif (ANALOG_DISCOVERY_DISABLED == True): # if we are trying to do dac caracterisation without the analog discovery
               self.showdialog(2)
               self.ui.statusbar.setStyleSheet("color : red")
               self.ui.statusbar.showMessage('The Analog discovery is not enabled\nthe Dac caracterisation is not operationnal',5000) # le 0 est un temps en milli-seconde 
               self.ui.Tab_Pages.setCurrentIndex(0)
        
    def AccessModeSelection(self): 
        """
            callback for the combo box of the 'Access mode' group of the main tab 
        """
        PicmicHLF.FSetRegisterOpMode(self.ui.CoBMainAccessMode.currentIndex())

     
    def PrePostParamSelection(self):
        """
            callback for the combo box of the 'Pre Post params' group of the main tab 
        """
        if self.ui.CoBPrePostParam.currentIndex() == 0:
            # No pre or post params
            self.ui.SBMainPrePostParam.setValue(0)
            self.ui.LblMainPostParam.hide()
            self.ui.LblMainPreParam.hide()
            self.ui.LblMainNoPreOrPostParam.show()
        elif self.ui.CoBPrePostParam.currentIndex() == 1:
            #Pre operation
            self.ui.LblMainPostParam.hide()
            self.ui.LblMainPreParam.show()
            self.ui.LblMainNoPreOrPostParam.hide()
        elif self.ui.CoBPrePostParam.currentIndex() == 2:
            #Post operation
            self.ui.LblMainPostParam.show()
            self.ui.LblMainPreParam.hide()
            self.ui.LblMainNoPreOrPostParam.hide()

            
    def SendPrePostParams(self):
        """
            callback for the send pre post params button of the 'Pre Post params' group of the main tab 
        """
    
        PicmicHLF.FSetPrePostOperationMode (self.ui.CoBPrePostParam.currentIndex(), self.ui.SBMainPrePostParam.value())

    
    def UpdateClicked(self):
        """
            update the list of available com ports
        """

        #get all the com ports availables
        self.ui.menu_COM.clear() #clear all items to avoid having the same item 2 times
        import serial.tools.list_ports
        ports = list(serial.tools.list_ports.comports())
        for p in ports:    
            self.ui.menu_COM.addItem(str(p))

        # MS 26 08 22 added the automatic selection of the Arduino Due Programming port
        for VIndex in range (self.ui.menu_COM.count()):
            if "Arduino Due Prog" in self.ui.menu_COM.itemText(VIndex):
                self.logger.info("Correct board found at index :{:d}".format(VIndex))
                self.ui.menu_COM.setCurrentIndex(VIndex)
                break
        # Update Target connection status
        self.TargetConnected = PicmicHLF.VGDueConnected

        if (self.TargetConnected == True) : #If we are serial connected to arduino
            self.ui.connection_status.setStyleSheet("color : green")
            self.ui.connection_status.setText("Connected") # set connection text
            self.ui.push_connect.setEnabled(False) #disable connect button cuz we are connected ...
            self.ui.push_disconnect.setEnabled(True) #enable disconnect button
        else:
            self.ui.connection_status.setStyleSheet("color : red")
            self.ui.connection_status.setText("Disconnected")
            self.ui.push_connect.setEnabled(True)
            self.ui.push_disconnect.setEnabled(False)
       

    def ConnectButtonClicked(self):
        """
            connect to the selected com port
        """

        try:
            VCurrentComSelected = self.ui.menu_COM.currentText() # Get the text selected in the combobox "Menu_Com"
            VSplittedComSentence = VCurrentComSelected.split(' - ') # Split the text to get the port name and the Com name
            VSelectedCom = VSplittedComSentence[0] # the first part is the port name
            VComName = VSplittedComSentence[1]     # the seconf part is the full name ( eg Arduino Due Prog )
            self.logger.info("Port: {}".format(VSplittedComSentence[0])) # log the port name
        except:
            self.logger.error("Bad Com Name")
            self.ui.statusbar.setStyleSheet("QStatusBar{background:red;color:white;font-weight:normal;}")      
            self.ui.statusbar.showMessage('Bad Com Name',0) # le 0 est un temps en seconde 
            VComName = "Bad Name"

        if ('Arduino Due Prog' in VComName) : # If selected port is COM X
            self.ui.statusbar.setStyleSheet("QStatusBar{background:MidLight;color:black;font-weight:normal;}")      
            self.ui.statusbar.showMessage('Board selected OK',0)  
            VResult = PicmicHLF.FConnectToDueBoard(VSelectedCom,dsrdtr = self.ui.ChBMainAutomaticResetDisable.isChecked())
            if (PicmicHLF.VGDueConnected == True) : #If we are serial connected to arduino
                self.ui.statusbar.showMessage('Board Connected ready to use ;-)',0) # le 0 est un temps en seconde 
                self.ui.connection_status.setStyleSheet("color : green")
                self.ui.connection_status.setText("Connected") # set connection text
                self.ui.push_connect.setEnabled(False) #disable connect button cuz we are connected ...
                self.ui.push_disconnect.setEnabled(True) #enable disconnect button
            else : # if cannot connect 
                self.ui.connection_status.setStyleSheet("color : orange")
                self.ui.connection_status.setText("Error") #set connection message as error 
                if (VResult == -1 ):
                    self.logger.error("Already connected, nothing done")
                elif (VResult == -2 ):
                    self.logger.error("Could not connect to the arduino board (system problem)")
                    self.ui.statusbar.setStyleSheet("QStatusBar{background:red;color:white;font-weight:normal;}")      
                    self.ui.statusbar.showMessage('Could not connect to the arduino board (system problem)',0) 
                else:
                    self.logger.error("Connection done, but communication errors")
                
            
        else : # If port selected is not COM 
            #print("ERROR : WRONG COM")
            self.ui.connection_status.setStyleSheet("color : orange")
            self.ui.connection_status.setText("Error") #set connection message as error 
            self.ui.statusbar.setStyleSheet("QStatusBar{background:red;color:white;font-weight:normal;}")      
            self.ui.statusbar.showMessage('ERROR : WRONG Element selected',0) # set message bas de page
            
        self.TargetConnected = PicmicHLF.VGDueConnected
            

    def DisconnectButtonClicked(self):
        """
            disconnect from the com port
        """
    
        PicmicHLF.FDisconnectFromDueBoard()
        if (PicmicHLF.VGDueConnected == False) :
                self.ui.connection_status.setStyleSheet("color : red")
                self.ui.connection_status.setText("Disconnected")
                self.ui.push_connect.setEnabled(True)
                self.ui.push_disconnect.setEnabled(False)
        self.TargetConnected = PicmicHLF.VGDueConnected
        
        
    def StopProgClicked(self):
        """
            end the slow control software
        """

        self.logger.critical("picmic slow control now ending")

        if (PicmicHLF.VGDueConnected == True) :
            self.logger.critical("Disconnecting the due board")
            PicmicHLF.FDisconnectFromDueBoard()

        # Release all the logging handlers

        handlers = logging.getLogger('picmic0').handlers[:]
        for handler in handlers:
            logging.getLogger('picmic0').removeHandler(handler)

        handlers = logging.getLogger('pm0_emul').handlers[:]
        for handler in handlers:
            logging.getLogger('pm0_emul').removeHandler(handler)

        handlers = logging.getLogger('pm0_sc').handlers[:]
        for handler in handlers:
            logging.getLogger('pm0_sc').removeHandler(handler)

        handlers = logging.getLogger('pm0_RT').handlers[:]
        for handler in handlers:
            logging.getLogger('pm0_RT').removeHandler(handler)

        handlers = logging.getLogger('pm0_fct').handlers[:]
        for handler in handlers:
            logging.getLogger('pm0_fct').removeHandler(handler)

        handlers = logging.getLogger('pm0_GUI').handlers[:]
        for handler in handlers:
            logging.getLogger('pm0_GUI').removeHandler(handler)

        handlers = self.logger.handlers[:]
        for handler in handlers:
            handler.close()
            self.logger.removeHandler(handler)
       
        logging.shutdown()  
        #sys.path.remove('./modules')
        
        app.closeAllWindows()


    def ConfigurationLoadFileSelection(self):
        """
            Selection of the load file
            displays the comments fields of the file 
        """

        VOldFilePath = os.path.join(os.getcwd(),  'Conf_Files')

        VFDialog = QFileDialog(self)
        VFDialog.setWindowTitle('Configuration load file selection')
        VFDialog.setNameFilter('configuration Files (*.conf)')
        VFDialog.setDirectory(VOldFilePath)
        VFDialog.setFileMode(QFileDialog.ExistingFile)
        
        if VFDialog.exec_() == QDialog.Accepted:
            VFileName = str(VFDialog.selectedFiles()[0])
            if os.path.isfile(VFileName):

                self.ui.leConfLoadPath.setText(str(VFDialog.directory().path()))
                self.ui.leConfLoadFileName.setText(os.path.basename(VFileName))
                
                self.ui.TEConfFileConfLoadFileInfo.clear()

                #‗config = configparser.ConfigParser(allow_no_value=True)
                self.config.read(VFileName)
                AuthorName= self.config['Comments']['author']
                FileDate = self.config['Comments']['date']
                #self.logger.info('Author:{}'.format(AuthorName))
                FileInfo = "Configuration file\nAuthor:{}      Date:{}".format(AuthorName,FileDate)
                self.ui.TEConfFileConfLoadFileInfo.append(FileInfo)
                self.ui.TEConfFileConfLoadFileInfo.append(self.config['Comments']['description'])
                self.ui.TEConfFileConfLoadFileInfo.append(self.config['Comments']['comment'])
            else:
                self.logger.error('File does not exist :%s',VFileName)
        else:
            self.logger.error ('File Selection CANCELLED ')

        pass
    def LoadSelectedConfigurationFile(self):
        """
            Load the selected configuration file
            and fill the GUI fields with the fields from the configuration file
        """
        VFileName =  os.path.join(self.ui.leConfLoadPath.text(),  self.ui.leConfLoadFileName.text())

        #config = configparser.ConfigParser(allow_no_value=True)
        self.config.read(VFileName)
        if (self.config.sections() == []):
            self.logger.error("Configuration File Loading failed")
            self.ui.statusbar.setStyleSheet("QStatusBar{background:red;color:white;font-weight:bold;}")      
            self.ui.statusbar.showMessage('Config file loading  FAILED',0) # le 0 est un temps en seconde 
        else:
            self.ui.LEConfFileAuthor.setText(self.config['Comments']['author'])
            self.ui.LEConfFileDate.setText(self.config['Comments']['date'])
            self.ui.LEConfFileDescription.setText(self.config['Comments']['description'])
            self.ui.LEconfFileComment.setText(self.config['Comments']['comment'])
            # set all the pixel sequencer regs
            self.ui.Set_FlushModule_PixSeq.setText('{:s}'.format( self.config['Pixel_Sequencer']['Flush_mod'] ))
            self.ui.Set_NU_PixSeq.setText('{:s}'.format( self.config['Pixel_Sequencer']['NU0'] ))
            self.ui.Set_MarkedMod_PixSeq.setText('{:s}'.format( self.config['Pixel_Sequencer']['Marker_mod'] ))
            self.ui.Set_NU2_PixSeq.setText('{:s}'.format( self.config['Pixel_Sequencer']['NU1'] ))
            self.ui.Set_PulseMod_PixSeq.setText('{:s}'.format( self.config['Pixel_Sequencer']['Pulse_Mod'] ))
            self.ui.Set_LoadWidth_PixSeq.setText('{:s}'.format( self.config['Pixel_Sequencer']['Load_Width'] ))
            self.ui.Set_Load_pLSB_PixSeq.setText('{:s}'.format( self.config['Pixel_Sequencer']['Load_p_LSB'] ))
            self.ui.Set_Load_PMSB_PixSeq.setText('{:s}'.format( self.config['Pixel_Sequencer']['Load_p_MSB'] ))
            self.ui.Set_Flush_PLSB_PixSeq.setText('{:s}'.format( self.config['Pixel_Sequencer']['Flush_p_LSB'] ))
            self.ui.Set_Flush_PMSB_PixSeq.setText('{:s}'.format( self.config['Pixel_Sequencer']['Flush_p_MSB'] ))
            self.ui.Set_APulse_pLSB_PixSeq.setText('{:s}'.format( self.config['Pixel_Sequencer']['APulse_LSB'] ))
            self.ui.Set_APulse_pMSB_PixSeq.setText('{:s}'.format( self.config['Pixel_Sequencer']['APulse_MSB'] ))
            self.ui.Set_DPulse_pLSB_PixSeq.setText('{:s}'.format( self.config['Pixel_Sequencer']['DPulse_LSB'] ))
            self.ui.Set_DPulse_pMSB_PixSeq.setText('{:s}'.format( self.config['Pixel_Sequencer']['DPulse_MSB'] ))
            self.ui.Set_RdPixMaskLSB_PixSeq.setText('{:s}'.format( self.config['Pixel_Sequencer']['RdpixMask_LSB'] ))
            self.ui.Set_RdPixMaskMSB_PixSeq.setText('{:s}'.format( self.config['Pixel_Sequencer']['RdpixMask_MSB'] ))
            self.ui.Set_MaxFrameLSB_PixSeq.setText('{:s}'.format( self.config['Pixel_Sequencer']['MaxFrame_LSB'] ))
            self.ui.Set_MaxFrameMSB_PixSeq.setText('{:s}'.format( self.config['Pixel_Sequencer']['MaxFrame_MSB'] ))
            self.ui.Set_PolarityLSB_PixSeq.setText('{:s}'.format( self.config['Pixel_Sequencer']['Polarity_LSB'] ))
            self.ui.Set_PolarityMSB_PixSeq.setText('{:s}'.format( self.config['Pixel_Sequencer']['Polarity_MSB'] ))
            self.ui.Set_Marker1LSB_PixSeq.setText('{:s}'.format( self.config['Pixel_Sequencer']['Marker1_LSB'] ))
            self.ui.Set_Marker1MSB_PixSeq.setText('{:s}'.format( self.config['Pixel_Sequencer']['Marker1_MSB'] ))
            self.ui.Set_Marker2LSB_PixSeq.setText('{:s}'.format( self.config['Pixel_Sequencer']['Marker2_LSB'] ))
            self.ui.Set_Marker2MSB_PixSeq.setText('{:s}'.format( self.config['Pixel_Sequencer']['Marker2_MSB'] ))
            # set all the VPulse SW registers
            if '0x' in self.config['VPulseSW']['byte0']:
                self.binary_input_VpulseSwitch1 = int(self.config['VPulseSW']['byte0'][2::],16)
            else:
                self.binary_input_VpulseSwitch1 = int(self.config['VPulseSW']['byte0'],10)
            if '0x' in self.config['VPulseSW']['byte1']:
                self.binary_input_VpulseSwitch2 = int(self.config['VPulseSW']['byte1'][2::],16)
            else:
                self.binary_input_VpulseSwitch2 = int(self.config['VPulseSW']['byte1'],10)
            if '0x' in self.config['VPulseSW']['byte2']:
                self.binary_input_VpulseSwitch3 = int(self.config['VPulseSW']['byte2'][2::],16)
            else:
                self.binary_input_VpulseSwitch3 = int(self.config['VPulseSW']['byte2'],10)
            if '0x' in self.config['VPulseSW']['byte3']:
                self.binary_input_VpulseSwitch4 = int(self.config['VPulseSW']['byte3'][2::],16)
            else:
                self.binary_input_VpulseSwitch4 = int(self.config['VPulseSW']['byte3'],10)
            if '0x' in self.config['VPulseSW']['byte4']:
                self.binary_input_VpulseSwitch5 = int(self.config['VPulseSW']['byte4'][2::],16)
            else:
                self.binary_input_VpulseSwitch5 = int(self.config['VPulseSW']['byte4'],10)
            if '0x' in self.config['VPulseSW']['byte5']:
                self.binary_input_VpulseSwitch6 = int(self.config['VPulseSW']['byte5'][2::],16)
            else:
                self.binary_input_VpulseSwitch6 = int(self.config['VPulseSW']['byte5'],10)
            if '0x' in self.config['VPulseSW']['byte6']:
                self.binary_input_VpulseSwitch7 = int(self.config['VPulseSW']['byte6'][2::],16) & 0x111111
            else:
                self.binary_input_VpulseSwitch7 = int(self.config['VPulseSW']['byte6'],10)
            
            self.ui.ListWidget_ByteState_Vpulse.clear()
            
            VpulseString = '{:06b} {:08b} {:08b} {:08b} {:08b} {:08b} {:08b}'.format( self.binary_input_VpulseSwitch7 , self.binary_input_VpulseSwitch6, self.binary_input_VpulseSwitch5 , self.binary_input_VpulseSwitch4 , self.binary_input_VpulseSwitch3 , self.binary_input_VpulseSwitch2 , self.binary_input_VpulseSwitch1 )
            self.ui.ListWidget_ByteState_Vpulse.addItem(VpulseString[::-1])
            
            # set the Test structure / global bias register
            if '0x' in self.config['Tst_St_Global_bias']['value']:
                self.ui.Text_Set_Test_Struct.setText(self.config['Tst_St_Global_bias']['value'][2::])
            else:
                self.ui.Text_Set_Test_Struct.setText(self.config['Tst_St_Global_bias']['value'])

            # set the DAC registers
            self.ui.Text_Set_DAC0.setText('{:s}'.format( self.config['Dac_values']['Dac0_VRefP'] ))
            self.ui.Text_Set_DAC1.setText('{:s}'.format( self.config['Dac_values']['Dac1_VRefN'] ))
            self.ui.Text_Set_DAC2.setText('{:s}'.format( self.config['Dac_values']['Dac2_VBN'] ))
            self.ui.Text_Set_DAC3.setText('{:s}'.format( self.config['Dac_values']['Dac3_VBN_adj'] ))
            self.ui.Text_Set_DAC4.setText('{:s}'.format( self.config['Dac_values']['Dac4_VBP'] ))
            # set the Dac Sw registers
            if '0x' in self.config['Dac_sw']['Byte0']:
                self.ui.RegDacText_Set_Byte1.setText('{:s}'.format(self.config['Dac_sw']['Byte0'][2::]))
            else:
                self.ui.RegDacText_Set_Byte1.setText('{:s}'.format(self.config['Dac_sw']['Byte0']))
            if '0x' in self.config['Dac_sw']['Byte1']:
                self.ui.RegDacText_Set_Byte2.setText('{:s}'.format(self.config['Dac_sw']['Byte1'][2::]))
            else:
                self.ui.RegDacText_Set_Byte2.setText('{:s}'.format(self.config['Dac_sw']['Byte1']))
            if '0x' in self.config['Dac_sw']['Byte2']:
                self.ui.RegDacText_Set_Byte3.setText('{:s}'.format(self.config['Dac_sw']['Byte2'][2::]))
            else:
                self.ui.RegDacText_Set_Byte3.setText('{:s}'.format(self.config['Dac_sw']['Byte2']))
                
            # Pulsing params
            if self.config.has_section('Pulsing'):
                if '0x' in self.config['Pulsing']['Pulsed_Params']:
                    self.ui.LEPulsingPPRegValue.setText('{:s}'.format(self.config['Pulsing']['Pulsed_Params'][2::]))
                else:
                    self.ui.LEPulsingPPRegValue.setText('{:s}'.format(self.config['Pulsing']['Pulsed_Params']))
                if '0x' in self.config['Pulsing']['Not_Pulsed_Params']:
                    self.ui.LEPulsingNOTPRegValue.setText('{:s}'.format(self.config['Pulsing']['Not_Pulsed_Params'][2::]))
                else:
                    self.ui.LEPulsingNOTPRegValue.setText('{:s}'.format(self.config['Pulsing']['Not_Pulsed_Params']))

            self.ui.statusbar.setStyleSheet("QStatusBar{background:white;color:black;font-weight:normal;}")      
            self.ui.statusbar.showMessage('Config file loading  Successfull',0) # le 0 est un temps en seconde 


    def SaveConfigurationFile(self):
        """
            Save a configuration file
        """
        # Setting the config with the values of the GUI field
        if (self.config.sections() == []):
            # config empty
            self.config.add_section('Comments')
            self.config.add_section('Pixel_Sequencer')
            self.config.add_section('VPulseSW')
            self.config.add_section('Tst_St_Global_bias')
            self.config.add_section('Dac_values')
            self.config.add_section('Dac_sw')
            self.config.add_section('Pulsing')
        else:
            # configuration existing
            pass
            
        self.config['Comments']['author'] = self.ui.LEConfFileAuthor.text()
        self.config['Comments']['date'] = self.ui.LEConfFileDate.text()
        self.config['Comments']['description'] = self.ui.LEConfFileDescription.text()
        self.config['Comments']['comment'] = self.ui.LEconfFileComment.text()

        self.config['Pixel_Sequencer']['Flush_mod'] = self.ui.Set_FlushModule_PixSeq.text()
        self.config['Pixel_Sequencer']['NU0'] = self.ui.Set_NU_PixSeq.text()
        self.config['Pixel_Sequencer']['Marker_mod'] = self.ui.Set_MarkedMod_PixSeq.text()
        self.config['Pixel_Sequencer']['NU1'] = self.ui.Set_NU2_PixSeq.text()
        self.config['Pixel_Sequencer']['Pulse_Mod'] = self.ui.Set_PulseMod_PixSeq.text()
        self.config['Pixel_Sequencer']['Load_Width'] = self.ui.Set_LoadWidth_PixSeq.text()
        self.config['Pixel_Sequencer']['Load_p_LSB'] = self.ui.Set_Load_pLSB_PixSeq.text()
        self.config['Pixel_Sequencer']['Load_p_MSB'] = self.ui.Set_Load_PMSB_PixSeq.text()
        self.config['Pixel_Sequencer']['Flush_p_LSB'] = self.ui.Set_Flush_PLSB_PixSeq.text()
        self.config['Pixel_Sequencer']['Flush_p_MSB'] = self.ui.Set_Flush_PMSB_PixSeq.text()
        self.config['Pixel_Sequencer']['APulse_LSB'] = self.ui.Set_APulse_pLSB_PixSeq.text()
        self.config['Pixel_Sequencer']['APulse_MSB'] = self.ui.Set_APulse_pMSB_PixSeq.text()
        self.config['Pixel_Sequencer']['DPulse_LSB'] = self.ui.Set_DPulse_pLSB_PixSeq.text()
        self.config['Pixel_Sequencer']['DPulse_MSB'] = self.ui.Set_DPulse_pMSB_PixSeq.text()
        self.config['Pixel_Sequencer']['RdpixMask_LSB'] = self.ui.Set_RdPixMaskLSB_PixSeq.text()
        self.config['Pixel_Sequencer']['RdpixMask_MSB'] = self.ui.Set_RdPixMaskMSB_PixSeq.text()
        self.config['Pixel_Sequencer']['MaxFrame_LSB'] = self.ui.Set_MaxFrameLSB_PixSeq.text()
        self.config['Pixel_Sequencer']['MaxFrame_MSB'] = self.ui.Set_MaxFrameMSB_PixSeq.text()
        self.config['Pixel_Sequencer']['Polarity_LSB'] = self.ui.Set_PolarityLSB_PixSeq.text()
        self.config['Pixel_Sequencer']['Polarity_MSB'] = self.ui.Set_PolarityMSB_PixSeq.text()
        self.config['Pixel_Sequencer']['Marker1_LSB'] = self.ui.Set_Marker1LSB_PixSeq.text()
        self.config['Pixel_Sequencer']['Marker1_MSB'] = self.ui.Set_Marker1MSB_PixSeq.text()
        self.config['Pixel_Sequencer']['Marker2_LSB'] = self.ui.Set_Marker2LSB_PixSeq.text()
        self.config['Pixel_Sequencer']['Marker2_MSB'] = self.ui.Set_Marker2MSB_PixSeq.text()

        self.config['VPulseSW']['byte0'] = "{:X}".format(self.binary_input_VpulseSwitch1)
        self.config['VPulseSW']['byte1'] = "{:X}".format(self.binary_input_VpulseSwitch2)
        self.config['VPulseSW']['byte2'] = "{:X}".format(self.binary_input_VpulseSwitch3)
        self.config['VPulseSW']['byte3'] = "{:X}".format(self.binary_input_VpulseSwitch4)
        self.config['VPulseSW']['byte4'] = "{:X}".format(self.binary_input_VpulseSwitch5)
        self.config['VPulseSW']['byte5'] = "{:X}".format(self.binary_input_VpulseSwitch6)
        self.config['VPulseSW']['byte6'] = "{:X}".format(self.binary_input_VpulseSwitch7)

        self.config['Tst_St_Global_bias']['value'] = self.ui.Text_Set_Test_Struct.text()

        self.config['Dac_values']['Dac0_VRefP'] = self.ui.Text_Set_DAC0.text()
        self.config['Dac_values']['Dac1_VRefN'] = self.ui.Text_Set_DAC1.text()
        self.config['Dac_values']['Dac2_VBN'] = self.ui.Text_Set_DAC2.text()
        self.config['Dac_values']['Dac3_VBN_adj'] = self.ui.Text_Set_DAC3.text()
        self.config['Dac_values']['Dac4_VBP'] = self.ui.Text_Set_DAC4.text()

        self.config['Dac_sw']['Byte0'] = self.ui.RegDacText_Set_Byte1.text()
        self.config['Dac_sw']['Byte1'] = self.ui.RegDacText_Set_Byte2.text()
        self.config['Dac_sw']['Byte2'] = self.ui.RegDacText_Set_Byte3.text()

        self.config['Pulsing']['Pulsed_Params'] = '0x' + self.ui.LEPulsingPPRegValue.text()
        self.config['Pulsing']['Not_Pulsed_Params'] = '0x' + self.ui.LEPulsingNOTPRegValue.text()

        
        VOldFilePath = self.ui.leConfLoadPath.text()

        VFileName, _ = QFileDialog.getSaveFileName(self,'Configuration file saving',VOldFilePath,'configuration Files (*.conf)')
        
        if  VFileName != '': 
                if (not ('.conf' in VFileName)):
                    VFileName = VFileName.split('.')[0] # remove the extension if any
                    VFileName = "".join((VFileName,".conf")); # add the correct extension        
                self.logger.info("saving file name:{}".format(VFileName))
                try :
                    with open(VFileName, 'w') as configfile:
                        self.config.write(configfile)
                except:
                    self.logger.error("Configuration file writing FAILED")
        else:
            self.logger.error ('File Selection CANCELLED ')
        
        pass


    def SendConfigurationToChip(self):
        """
            Send the current configuration of the GUi to the chip
        """

        self.ui.statusbar.setStyleSheet("QStatusBar{background:MidLight;color:black;font-weight:normal;}")      

        self.ui.setPixSeq.click()
        self.ui.statusbar.showMessage('Pixel sequencer sent to chip, step 1 of 4',5000) # le 0 est un temps en milli seconde 
        self.ui.Set_Button_Test_Struct.click()
        self.ui.statusbar.showMessage('Test structure/ global bias sent to chip , step 2 of 4',5000) # le 0 est un temps en milliseconde 
        self.ui.Set_Button_All_DAC.click()
        self.ui.statusbar.showMessage('DAC registers sent to chip, step 3 of 4',5000) # le 0 est un temps en milliseconde 
        self.ui.Set_All_Bytes_DacSwitch.click()
        self.ui.statusbar.showMessage('DAC SW registers sent to chip, step 4 of 4',5000) # le 0 est un temps en milliseconde 

 
    def SteeringCoBResetActivated(self):
        """
            callback for the 'Reset' combo box of the Steering Tab
        """
        if (self.ui.coBSteerRstState.currentIndex() == 1):
            self.logger.info("Reset State changed to :High")
            VErr = PicmicHLF.FSetResetSignal(1)
        else:
            self.logger.info("Reset State changed to :Low")
            VErr = PicmicHLF.FSetResetSignal(0)
        if VErr < 0 :
            #Error
            self.ui.statusbar.setStyleSheet("QStatusBar{background:red;color:white;font-weight:bold;}")      
            self.ui.statusbar.showMessage('Steering Reset signal FAILED',0) # le 0 est un temps en seconde 
            pass
        else:
            # OK
            self.ui.statusbar.setStyleSheet("QStatusBar{background:MidLight;color:black;font-weight:normal;}")      
            self.ui.statusbar.showMessage('Steering Reset signal successfull',0) # le 0 est un temps en seconde 
            pass
    

    def SteeringBtResetToggleClicked(self):
        """
            callback for the Toggle button for the reset signal of the Steering Tab
        """
        if (self.ui.coBSteerRstState.currentIndex() == 1):
            self.logger.info("Reset State Toggled to :Low")
            self.ui.coBSteerRstState.setCurrentIndex(0)
            VErr = PicmicHLF.FSetResetSignal(0)
        else:
            self.logger.info("Reset State Toggled to :High")
            self.ui.coBSteerRstState.setCurrentIndex(1)
            VErr = PicmicHLF.FSetResetSignal(1)
        if VErr < 0 :
            #Error
            self.ui.statusbar.setStyleSheet("QStatusBar{background:red;color:white;font-weight:bold;}")      
            self.ui.statusbar.showMessage('Steering reset signal toggle FAILED',0) # le 0 est un temps en seconde 
        else:
            # OK
            self.ui.statusbar.setStyleSheet("QStatusBar{background:MidLight;color:black;font-weight:normal;}")      
            self.ui.statusbar.showMessage('Steering reset signal toggle successfull',0) # le 0 est un temps en seconde 
    

    def SteeringCoBReset_I2CActivated(self):
        """
            callback for the 'Reset_I2C' combo box of the Steering Tab
        """
        if (self.ui.coBSteerRst_I2CState.currentIndex() == 1):
            self.logger.info("Reset_I2C State changed to :High")
            VErr = PicmicHLF.FSetResetI2CSignal(1)
        else:
            self.logger.info("Reset_I2C State changed to :Low")
            VErr = PicmicHLF.FSetResetI2CSignal(0)
        if VErr < 0 :
            #Error
            self.ui.statusbar.setStyleSheet("QStatusBar{background:red;color:white;font-weight:bold;}")      
            self.ui.statusbar.showMessage('Steering Reset_I2C signal setting FAILED',0) # le 0 est un temps en seconde 
        else:
            # OK
            self.ui.statusbar.setStyleSheet("QStatusBar{background:MidLight;color:black;font-weight:normal;}")      
            self.ui.statusbar.showMessage('Steering Reset_I2C signal setting successfull',0) # le 0 est un temps en seconde 
    

    def SteeringBtReset_I2CToggleClicked(self):
        """
            callback for the Toggle button for the reset_I2C signal of the Steering Tab
        """
        if (self.ui.coBSteerRst_I2CState.currentIndex() == 1):
            self.logger.info("Reset_I2C State Toggled to :Low")
            self.ui.coBSteerRst_I2CState.setCurrentIndex(0)
            VErr = PicmicHLF.FSetResetI2CSignal(0)
        else:
            self.logger.info("Reset_I2C State Toggled to :High")
            self.ui.coBSteerRst_I2CState.setCurrentIndex(1)
            VErr = PicmicHLF.FSetResetI2CSignal(1)
        if VErr < 0 :
            #Error
            self.ui.statusbar.setStyleSheet("QStatusBar{background:red;color:white;font-weight:bold;}")      
            self.ui.statusbar.showMessage('Steering Reset_I2C signal toggle FAILED',0) # le 0 est un temps en seconde 
        else:
            # OK
            self.ui.statusbar.setStyleSheet("QStatusBar{background:MidLight;color:black;font-weight:normal;}")      
            self.ui.statusbar.showMessage('Steering Reset_I2C signal toggle successfull',0) # le 0 est un temps en seconde 

    def SteeringCoBStartActivated(self):
        """
            callback for the 'Start' combo box of the Steering Tab
        """
        if (self.ui.coBSteerStartState.currentIndex() == 1):
            self.logger.info("Start State changed to :High")
            VErr = PicmicHLF.FSetStartSignal(1)
        else:
            self.logger.info("Start State changed to :Low")
            VErr = PicmicHLF.FSetStartSignal(0)
        if VErr < 0 :
            #Error
            self.ui.statusbar.setStyleSheet("QStatusBar{background:red;color:white;font-weight:bold;}")      
            self.ui.statusbar.showMessage('Steering start signal setting FAILED',0) # le 0 est un temps en seconde 
        else:
            # OK
            self.ui.statusbar.setStyleSheet("QStatusBar{background:MidLight;color:black;font-weight:normal;}")      
            self.ui.statusbar.showMessage('Steering start signal setting successfull',0) # le 0 est un temps en seconde 
    

    def SteeringBtStartToggleClicked(self):
        """
            callback for the Toggle button for the Start signal of the Steering Tab
        """
        if (self.ui.coBSteerStartState.currentIndex() == 1):
            self.logger.info("Start State Toggled to :Low")
            self.ui.coBSteerStartState.setCurrentIndex(0)
            VErr = PicmicHLF.FSetStartSignal(0)
        else:
            self.logger.info("Start State Toggled to :High")
            self.ui.coBSteerStartState.setCurrentIndex(1)
            VErr = PicmicHLF.FSetStartSignal(1)
        if VErr < 0 :
            #Error
            self.ui.statusbar.setStyleSheet("QStatusBar{background:red;color:white;font-weight:bold;}")      
            self.ui.statusbar.showMessage('Steering start signal toggle FAILED',0) # le 0 est un temps en seconde 
        else:
            # OK
            self.ui.statusbar.setStyleSheet("QStatusBar{background:MidLight;color:black;font-weight:normal;}")      
            self.ui.statusbar.showMessage('Steering start signal toggle successfull',0) # le 0 est un temps en seconde 


    def SteeringCoBTestmodActivated(self):
        """
            callback for the 'Reset' combo box of the Steering Tab
        """
        if (self.ui.coBSteerTestmodState.currentIndex() == 1):
            self.logger.info("Testmod State changed to :High")
            VErr = PicmicHLF.FSetTestModSignal(1)
        else:
            self.logger.info("Testmod State changed to :Low")
            VErr = PicmicHLF.FSetTestModSignal(0)
        if VErr < 0 :
            #Error
            self.ui.statusbar.setStyleSheet("QStatusBar{background:red;color:white;font-weight:bold;}")      
            self.ui.statusbar.showMessage('Steering Testmod signal setting FAILED',0) # le 0 est un temps en seconde 
        else:
            # OK
            self.ui.statusbar.setStyleSheet("QStatusBar{background:MidLight;color:black;font-weight:normal;}")      
            self.ui.statusbar.showMessage('Steering Testmod signal setting successfull',0) # le 0 est un temps en seconde 
    

    def SteeringBtTestmodToggleClicked(self):
        """
            callback for the Toggle button for the reset signal of the Steering Tab
        """
        if (self.ui.coBSteerTestmodState.currentIndex() == 1):
            self.logger.info("Testmod State Toggled to :Low")
            self.ui.coBSteerTestmodState.setCurrentIndex(0)
            VErr = PicmicHLF.FSetTestModSignal(0)
        else:
            self.logger.info("Testmod State Toggled to :High")
            self.ui.coBSteerTestmodState.setCurrentIndex(1)
            VErr = PicmicHLF.FSetTestModSignal(1)
        if VErr < 0 :
            #Error
            self.ui.statusbar.setStyleSheet("QStatusBar{background:red;color:white;font-weight:bold;}")      
            self.ui.statusbar.showMessage('Steering Testmod signal toggle FAILED',0) # le 0 est un temps en seconde 
        else:
            # OK
            self.ui.statusbar.setStyleSheet("QStatusBar{background:MidLight;color:black;font-weight:normal;}")      
            self.ui.statusbar.showMessage('Steering Testmod signal toggle successfull',0) # le 0 est un temps en seconde 


    def PulsingFileSelection(self):
        """
            callback for the File selection button of the pulsing tab
        """
        VOldFilePath = os.path.join(os.getcwd(),  'Pulsing_Files')

        VFDialog = QFileDialog(self)
        VFDialog.setWindowTitle('Open Conf file')
        VFDialog.setNameFilter('text Files (*.txt)')
        VFDialog.setDirectory(VOldFilePath)
        VFDialog.setFileMode(QFileDialog.ExistingFile)
        
        if VFDialog.exec_() == QDialog.Accepted:
            VFileName = str(VFDialog.selectedFiles()[0])
            if os.path.isfile(VFileName):
                self.ui.lePulsingPath.setText(str(VFDialog.directory().path()))
                self.ui.lePulsingFileName.setText(os.path.basename(VFileName))
                Result, CommentsFromFile = PM0EMUL.FGetCommentsFromFile(VFileName)
                self.ui.TEPulsingFileComments.clear()
                self.ui.TEPulsingFileComments.append(CommentsFromFile)
            else:
                self.logger.error('File does not exist :%s',VFileName)
        else:
            self.logger.error ('File Reading CANCELLED ')

    
    def LEPulsingPPRegValue_Changed(self) : #Bit 0 à 2
        """
            Callback for the modification of the Pulsed pixel Line edit for the pulsed pixels params
        """
        if (self.ui.LEPulsingPPRegValue.text() != ''):
            PPixelsReg = int(self.ui.LEPulsingPPRegValue.text(),16)
            self.ui.SBPulsingPulsed_IADJ_Data_PixConf.setValue(PPixelsReg & 0x07)
            self.ui.ChBPulsingPP_ENA_CM_Data_PixConf.setChecked((PPixelsReg & 0x08) == 0x08)
            self.ui.ChBPulsingPP_SW0_Data_PixConf.setChecked((PPixelsReg & 0x10) == 0x10)
            self.ui.ChBPulsingPP_SW1_Data_PixConf.setChecked((PPixelsReg & 0x20) == 0x20)
            self.ui.ChBPulsingPP_ENA_CC_Data_PixConf.setChecked((PPixelsReg & 0x40) == 0x40)
            self.ui.ChBPulsingPP_Act_Pulse_Data_PixConf.setChecked((PPixelsReg & 0x80) == 0x80)

 
    def SBPulsingPulsed_IADJ_Data_PixConfValueChanged(self):
        """
            Callback for the modification of the IADJ Line edit for the pulsed pixels params
        """
    
        if (self.ui.LEPulsingPPRegValue.text() == ''):
            PPixelsReg = 0
        else:
            PPixelsReg = int(self.ui.LEPulsingPPRegValue.text(),16)
        PPixelsReg = (PPixelsReg & 0xF8) | self.ui.SBPulsingPulsed_IADJ_Data_PixConf.value()
        self.ui.LEPulsingPPRegValue.setText('{:X}'.format(PPixelsReg))

            
    def ChBPulsingPP_ENA_CM_Data_PixConf_Clicked(self) :
        """
            Callback for the modification of the ENA_CM Checkbox for the pulsed pixels params
        """
         
        if (self.ui.LEPulsingPPRegValue.text() == ''):
            PPixelsReg = 0
        else:
            PPixelsReg = int(self.ui.LEPulsingPPRegValue.text(),16)
        #If checked 
        if self.ui.ChBPulsingPP_ENA_CM_Data_PixConf.isChecked():
            PPixelsReg = PPixelsReg | 0x08
        else : 
            PPixelsReg = PPixelsReg & 0xF7
            
        self.ui.LEPulsingPPRegValue.setText('{:X}'.format(PPixelsReg))

            
    def ChBPulsingPP_SW0_Data_PixConf_Clicked(self) :
        """
            Callback for the modification of the SW0 Checkbox for the pulsed pixels params
        """
         
        if (self.ui.LEPulsingPPRegValue.text() == ''):
            PPixelsReg = 0
        else:
            PPixelsReg = int(self.ui.LEPulsingPPRegValue.text(),16)
        #If checked 
        if self.ui.ChBPulsingPP_SW0_Data_PixConf.isChecked():
            PPixelsReg = PPixelsReg | 0x10
        else : 
            PPixelsReg = PPixelsReg & 0xEF
            
        self.ui.LEPulsingPPRegValue.setText('{:X}'.format(PPixelsReg))

        
    def ChBPulsingPP_SW1_Data_PixConf_Clicked(self) :
        """
            Callback for the modification of the SW1 Checkbox for the pulsed pixels params
        """

        if (self.ui.LEPulsingPPRegValue.text() == ''):
            PPixelsReg = 0
        else:
            PPixelsReg = int(self.ui.LEPulsingPPRegValue.text(),16)
        #If checked 
        if self.ui.ChBPulsingPP_SW1_Data_PixConf.isChecked():
            PPixelsReg = PPixelsReg | 0x20
        else : 
            PPixelsReg = PPixelsReg & 0xDF
            
        self.ui.LEPulsingPPRegValue.setText('{:X}'.format(PPixelsReg))
         
            
    def ChBPulsingPP_ENA_CC_Data_PixConf_Clicked(self) :
        """
            Callback for the modification of the ENA_CC Checkbox for the pulsed pixels params
        """

        if (self.ui.LEPulsingPPRegValue.text() == ''):
            PPixelsReg = 0
        else:
            PPixelsReg = int(self.ui.LEPulsingPPRegValue.text(),16)
        #If checked 
        if self.ui.ChBPulsingPP_ENA_CC_Data_PixConf.isChecked():
            PPixelsReg = PPixelsReg | 0x40
        else : 
            PPixelsReg = PPixelsReg & 0xBF
            
        self.ui.LEPulsingPPRegValue.setText('{:X}'.format(PPixelsReg))
         
             
    def ChBPulsingPP_Act_Pulse_Data_PixConf_Clicked(self) :
        """
            Callback for the modification of the ActivatePulse Checkbox for the pulsed pixels params
        """
         
        if (self.ui.LEPulsingPPRegValue.text() == ''):
            PPixelsReg = 0
        else:
            PPixelsReg = int(self.ui.LEPulsingPPRegValue.text(),16)
        #If checked 
        if self.ui.ChBPulsingPP_Act_Pulse_Data_PixConf.isChecked():
            PPixelsReg = PPixelsReg | 0x80
        else : 
            PPixelsReg = PPixelsReg & 0x7F
            
        self.ui.LEPulsingPPRegValue.setText('{:X}'.format(PPixelsReg))


    
    def LEPulsingNOTPRegValue_Changed(self) : #Bit 0 à 2
        """
            Callback for the modification of the Pulsed pixel Line edit for the pulsed pixels params
        """
        if (self.ui.LEPulsingNOTPRegValue.text() != ''):
            NOTPixelsReg = int(self.ui.LEPulsingNOTPRegValue.text(),16)
            self.ui.SBPulsingNOTPulsed_IADJ_Data_PixConf.setValue(NOTPixelsReg & 0x07)
            self.ui.ChBPulsingNOTP_ENA_CM_Data_PixConf.setChecked((NOTPixelsReg & 0x08) == 0x08)
            self.ui.ChBPulsingNOTP_SW0_Data_PixConf.setChecked((NOTPixelsReg & 0x10) == 0x10)
            self.ui.ChBPulsingNOTP_SW1_Data_PixConf.setChecked((NOTPixelsReg & 0x20) == 0x20)
            self.ui.ChBPulsingNOTP_ENA_CC_Data_PixConf.setChecked((NOTPixelsReg & 0x40) == 0x40)
            self.ui.ChBPulsingNOTP_Act_Pulse_Data_PixConf.setChecked((NOTPixelsReg & 0x80) == 0x80)
 
    def SBPulsingNOTPulsed_IADJ_Data_PixConfValueChanged(self):
        """
            Callback for the modification of the IADJ Line edit for the pulsed pixels params
        """
    
        if (self.ui.LEPulsingNOTPRegValue.text() == ''):
            NOTPixelsReg = 0
        else:
            NOTPixelsReg = int(self.ui.LEPulsingNOTPRegValue.text(),16)
        NOTPixelsReg = (NOTPixelsReg & 0xF8) | self.ui.SBPulsingNOTPulsed_IADJ_Data_PixConf.value()
        self.ui.LEPulsingNOTPRegValue.setText('{:X}'.format(NOTPixelsReg))

            
    def ChBPulsingNOTP_ENA_CM_Data_PixConf_Clicked(self) :
        """
            Callback for the modification of the ENA_CM Checkbox for the pulsed pixels params
        """
         
        if (self.ui.LEPulsingNOTPRegValue.text() == ''):
            NOTPixelsReg = 0
        else:
            NOTPixelsReg = int(self.ui.LEPulsingNOTPRegValue.text(),16)
        #If checked 
        if self.ui.ChBPulsingNOTP_ENA_CM_Data_PixConf.isChecked():
            NOTPixelsReg = NOTPixelsReg | 0x08
        else : 
            NOTPixelsReg = NOTPixelsReg & 0xF7
            
        self.ui.LEPulsingNOTPRegValue.setText('{:X}'.format(NOTPixelsReg))

            
    def ChBPulsingNOTP_SW0_Data_PixConf_Clicked(self) :
        """
            Callback for the modification of the SW0 Checkbox for the pulsed pixels params
        """
         
        if (self.ui.LEPulsingNOTPRegValue.text() == ''):
            NOTPixelsReg = 0
        else:
            NOTPixelsReg = int(self.ui.LEPulsingNOTPRegValue.text(),16)
        #If checked 
        if self.ui.ChBPulsingNOTP_SW0_Data_PixConf.isChecked():
            NOTPixelsReg = NOTPixelsReg | 0x10
        else : 
            NOTPixelsReg = NOTPixelsReg & 0xEF
            
        self.ui.LEPulsingNOTPRegValue.setText('{:X}'.format(NOTPixelsReg))

        
    def ChBPulsingNOTP_SW1_Data_PixConf_Clicked(self) :
        """
            Callback for the modification of the SW1 Checkbox for the pulsed pixels params
        """

        if (self.ui.LEPulsingNOTPRegValue.text() == ''):
            NOTPixelsReg = 0
        else:
            NOTPixelsReg = int(self.ui.LEPulsingNOTPRegValue.text(),16)
        #If checked 
        if self.ui.ChBPulsingNOTP_SW1_Data_PixConf.isChecked():
            NOTPixelsReg = NOTPixelsReg | 0x20
        else : 
            NOTPixelsReg = NOTPixelsReg & 0xDF
            
        self.ui.LEPulsingNOTPRegValue.setText('{:X}'.format(NOTPixelsReg))
         
            
    def ChBPulsingNOTP_ENA_CC_Data_PixConf_Clicked(self) :
        """
            Callback for the modification of the ENA_CC Checkbox for the pulsed pixels params
        """

        if (self.ui.LEPulsingNOTPRegValue.text() == ''):
            NOTPixelsReg = 0
        else:
            NOTPixelsReg = int(self.ui.LEPulsingNOTPRegValue.text(),16)
        #If checked 
        if self.ui.ChBPulsingNOTP_ENA_CC_Data_PixConf.isChecked():
            NOTPixelsReg = NOTPixelsReg | 0x40
        else : 
            NOTPixelsReg = NOTPixelsReg & 0xBF
            
        self.ui.LEPulsingNOTPRegValue.setText('{:X}'.format(NOTPixelsReg))
         
             
    def ChBPulsingNOTP_Act_Pulse_Data_PixConf_Clicked(self) :
        """
            Callback for the modification of the ActivatePulse Checkbox for the pulsed pixels params
        """
         
        if (self.ui.LEPulsingNOTPRegValue.text() == ''):
            NOTPixelsReg = 0
        else:
            NOTPixelsReg = int(self.ui.LEPulsingNOTPRegValue.text(),16)
        #If checked 
        if self.ui.ChBPulsingNOTP_Act_Pulse_Data_PixConf.isChecked():
            NOTPixelsReg = NOTPixelsReg | 0x80
        else : 
            NOTPixelsReg = NOTPixelsReg & 0x7F
            
        self.ui.LEPulsingNOTPRegValue.setText('{:X}'.format(NOTPixelsReg))


    def SendPulsingToChip(self):
        """
            callback for the send pulsing button of the Pulsing Tab
        """
        self.logger.info("Send pulsing to chip")

        VPixelToSend = self.ui.CoBPulsingPixelSel.currentIndex()
        VPulsingFileName = self.ui.lePulsingPath.text()+"/"+self.ui.lePulsingFileName.text()
        VPulsingReg = int(self.ui.LEPulsingPPRegValue.text(),16)
        VNotPulsingReg = int(self.ui.LEPulsingNOTPRegValue.text(),16)
        VErr, BitMap,Comments,HitNb = PicmicHLF.FSetBitmapInPixMemFromFile(VPixelToSend,VPulsingFileName,VPulsingReg,VNotPulsingReg)
        
        if VErr < 0 :
            #Error
            self.ui.statusbar.setStyleSheet("QStatusBar{background:red;color:white;font-weight:bold;}")      
            self.ui.statusbar.showMessage('Pulsing sending FAILED',0) # le 0 est un temps en seconde 
        else:
            # OK
            self.ui.statusbar.setStyleSheet("QStatusBar{background:MidLight;color:black;font-weight:normal;}")      
            self.ui.statusbar.showMessage('Pulsing sending successfull',0) # le 0 est un temps en seconde 
        
            self.ui.TEPulsingFileComments.clear()
            self.ui.TEPulsingFileComments.append(Comments)
            self.ui.TEPulsingFileComments.append("")
            self.ui.TEPulsingFileComments.append("")
            self.ui.TEPulsingFileComments.append("Total hit sent :{:d}".format(HitNb))
            # refresh the CaracDiscri Tab fields for of the pulsing file name and path
            self.ui.leCarDisPulsingPath.setText(self.ui.lePulsingPath.text())
            self.ui.leCarDisPulsingFileName.setText(self.ui.lePulsingFileName.text())
            if (platform.release() != 'XP'):
                self.plotPulsing.matshow(BitMap,cmap='Greys')
                self.canvasPulsing.draw()
            else:
                fig = plt.figure('Data from Picmic')
                PlotAx = plt.axes([0.05,0.15,0.95,0.75])
                VRowNb = np.size(BitMap,0)
                VColNb = np.size(BitMap,1)
                self.logger.info("Plotting the matrix, matrix size :{:d},{:d}".format(VRowNb,VColNb))
                plt.set_cmap('Greys')
                MatrixShow = PlotAx.matshow(BitMap)
                fig.canvas.draw()
                plt.show()

    
        #////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
        #//////////////////////////////////////  FONCTIONS PAGE REGISTERS  //////////////////////////////////////////////////////
        #////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    

  
    
    """
         Global Command TAB

        Everything related to Global command Fcts is here
    """
    
    #GET/SET Buttons 
    def Set_Button_Global_Cmd_Clicked(self) :
        """
            callback for the Set button for the Global command register
        """
        
        VErr = PicmicHLF.FSetGlobalCommandReg(self.binary_input_GlobalCommand)  

        self.Flag_Set_GlobalCmd = 1
        if VErr < 0 :
            #Error
            self.ui.statusbar.setStyleSheet("QStatusBar{background:red;color:white;font-weight:bold;}")      
            self.ui.statusbar.showMessage('Global_cmd setting FAILED',0) # le 0 est un temps en seconde 
            pass
        else:
            # OK
            self.ui.statusbar.setStyleSheet("QStatusBar{background:MidLight;color:black;font-weight:normal;}")      
            self.ui.statusbar.showMessage('Global_cmd setting successfull',0) # le 0 est un temps en seconde 
            pass

            
    def Get_Global_Cmd_Clicked(self) :
        """
            callback for the Get button for the Global command register
        """
     
        VErr, returned_value = PicmicHLF.FGetGlobalCommandReg()


        if VErr < 0 :
            #Error
            self.ui.statusbar.setStyleSheet("QStatusBar{background:red;color:white;font-weight:bold;}")      
            self.ui.statusbar.showMessage('Global_cmd setting FAILED',0) # le 0 est un temps en seconde 
        else:
            # OK
            self.ui.statusbar.setStyleSheet("QStatusBar{background:MidLight;color:black;font-weight:normal;}")      
            self.ui.statusbar.showMessage('Global_cmd setting successfull',0) # le 0 est un temps en seconde 


            self.ui.Text_Get_Global_Cmd.setText('{:X}'.format( returned_value[0] ))
            
            
            if(self.Flag_Set_GlobalCmd == 1):
     
                if(int(returned_value[0]) != self.binary_input_GlobalCommand):
                    self.ui.statusbar.setStyleSheet("color : red")
                    self.ui.statusbar.showMessage('GET ERROR : Value to send different from Current Value',0)
                    
                else :
                    self.ui.statusbar.setStyleSheet("color : green")
                    self.ui.statusbar.showMessage('GET OK : Value to send = Current Value',0)
            
            self.DisplayBinaryOnGlobalCommandOutputCheckboxes(returned_value[0])
    
    
    
    #Input CheckBoxes clicked 
    def EnExtPulse_Global_Cmd_Clicked(self) :
        """
            Registers Tab
                Global command Tab
                    Enable Ext pulse checkbox callback
        """
    
        if self.ui.Set_EnExtPulse_Global_Cmd.isChecked():
            self.binary_input_GlobalCommand = self.binary_input_GlobalCommand | 0x01
        else : 
            self.binary_input_GlobalCommand = self.binary_input_GlobalCommand & 0xFE
            
        self.ui.Text_Set_GlobalCmd.setText('{:X}'.format( self.binary_input_GlobalCommand ))
 


    def Set_ExtPulse_Global_Cmd_Clicked(self) :
        """
            Registers Tab
                Global command Tab
                    Set Ext pulse checkbox callback
        """
        

        if self.ui.Set_ExtPulse_Global_Cmd.isChecked():
            self.binary_input_GlobalCommand = self.binary_input_GlobalCommand | 0x02
        else : 
            self.binary_input_GlobalCommand = self.binary_input_GlobalCommand & 0xFD
            
        self.ui.Text_Set_GlobalCmd.setText('{:X}'.format( self.binary_input_GlobalCommand ))
 

    def SetRstFrCnt_Global_Cmd_Clicked(self) :
        """
            Registers Tab
                Global command Tab
                    Reset Frame Counter checkbox callback
        """
    
        
        
        if self.ui.SetRstFrCnt_Global_Cmd.isChecked():
            self.binary_input_GlobalCommand = self.binary_input_GlobalCommand | 0x04
        else : 
            self.binary_input_GlobalCommand = self.binary_input_GlobalCommand & 0xFB
            
        self.ui.Text_Set_GlobalCmd.setText('{:X}'.format( self.binary_input_GlobalCommand ))



    def Set_StartSeq_Global_Cmd_Clicked(self) :
        """
            Registers Tab
                Global command Tab
                    Start Sequencer checkbox callback
        """
        
        
        
        if self.ui.Set_StartSeq_Global_Cmd.isChecked():
            self.binary_input_GlobalCommand = self.binary_input_GlobalCommand | 0x08
        else : 
            self.binary_input_GlobalCommand = self.binary_input_GlobalCommand & 0xF7
            
        self.ui.Text_Set_GlobalCmd.setText('{:X}'.format( self.binary_input_GlobalCommand ))


    def GlobalCmdTextChanged(self):
        """
            Registers Tab
                Global command Tab
                    Global command set text box callback
        """

        if self.ui.Text_Set_GlobalCmd.text() != "":
            if self.binary_input_GlobalCommand != int(self.ui.Text_Set_GlobalCmd.text(),16):
                # report change to the checkboxes
                self.binary_input_GlobalCommand = int(self.ui.Text_Set_GlobalCmd.text(),16)
                self.ui.Set_EnExtPulse_Global_Cmd.setChecked((self.binary_input_GlobalCommand & 0x01) == 0x01)
                self.ui.Set_ExtPulse_Global_Cmd.setChecked((self.binary_input_GlobalCommand & 0x02) == 0x02)
                self.ui.SetRstFrCnt_Global_Cmd.setChecked((self.binary_input_GlobalCommand & 0x04) == 0x04)
                self.ui.Set_StartSeq_Global_Cmd.setChecked((self.binary_input_GlobalCommand & 0x08) == 0x08)


    def DisplayBinaryOnGlobalCommandOutputCheckboxes(self,number) :
         
        self.ui.Check_EnExtPulse_Global_Cmd.setChecked((number & 0x01 ) == 0x01)
        self.ui.Check_ExtPulse_Global_Cmd.setChecked((number & 0x02 ) == 0x02)
        self.ui.Check_RstFrCnt_Global_Cmd.setChecked((number & 0x04 ) == 0x04)
        self.ui.Check_StartSeq_Global_Cmd.setChecked((number & 0x08 ) == 0x08)
    

    """
         Pixel Sequence TAB

        Everything related to Pixel Sequence Fcts is here
    """ 
            
    #Execute when "Set Activated" is clicked 
    def setPixSeq_Clicked(self) :
        """
            Registers Tab
                Pixel Sequencer Tab
                    Set button callback
        """
    
        Byte0_converti = int(self.ui.Set_FlushModule_PixSeq.text(),10)
        Byte1_converti = int(self.ui.Set_NU_PixSeq.text(),10)
        Byte2_converti = int(self.ui.Set_MarkedMod_PixSeq.text(),10)
        Byte3_converti = int(self.ui.Set_NU2_PixSeq.text(),10)
        Byte4_converti = int(self.ui.Set_PulseMod_PixSeq.text(),10)
        Byte5_converti = int(self.ui.Set_LoadWidth_PixSeq.text(),10)
        Byte6_converti = int(self.ui.Set_Load_pLSB_PixSeq.text(),10)
        Byte7_converti = int(self.ui.Set_Load_PMSB_PixSeq.text(),10)
        Byte8_converti = int(self.ui.Set_Flush_PLSB_PixSeq.text(),10)
        Byte9_converti = int(self.ui.Set_Flush_PMSB_PixSeq.text(),10)
        Byte10_converti = int(self.ui.Set_APulse_pLSB_PixSeq.text(),10)
        Byte11_converti = int(self.ui.Set_APulse_pMSB_PixSeq.text(),10)
        Byte12_converti = int(self.ui.Set_DPulse_pLSB_PixSeq.text(),10)
        Byte13_converti = int(self.ui.Set_DPulse_pMSB_PixSeq.text(),10)
        Byte14_converti = int(self.ui.Set_RdPixMaskLSB_PixSeq.text(),10)
        Byte15_converti = int(self.ui.Set_RdPixMaskMSB_PixSeq.text(),10)
        Byte16_converti = int(self.ui.Set_MaxFrameLSB_PixSeq.text(),10)
        Byte17_converti = int(self.ui.Set_MaxFrameMSB_PixSeq.text(),10)
        Byte18_converti = int(self.ui.Set_PolarityLSB_PixSeq.text(),10)
        Byte19_converti = int(self.ui.Set_PolarityMSB_PixSeq.text(),10)
        Byte20_converti = int(self.ui.Set_Marker1LSB_PixSeq.text(),10)
        Byte21_converti = int(self.ui.Set_Marker1MSB_PixSeq.text(),10)
        Byte22_converti = int(self.ui.Set_Marker2LSB_PixSeq.text(),10)
        Byte23_converti = int(self.ui.Set_Marker2MSB_PixSeq.text(),10)
        
        ListeBytes = [Byte0_converti,Byte1_converti,Byte2_converti,Byte3_converti,Byte4_converti,
                        Byte5_converti,Byte6_converti,Byte7_converti,Byte8_converti,Byte9_converti
                        ,Byte10_converti,Byte11_converti,Byte12_converti,Byte13_converti,Byte14_converti
                        ,Byte15_converti,Byte16_converti,Byte17_converti,Byte18_converti,Byte19_converti
                        ,Byte20_converti,Byte21_converti,Byte22_converti,Byte23_converti]
    
        self.logger.info("Values to send :{}".format(ListeBytes))
        VErr = PicmicHLF.FSetPixelSequencerRegs(ListeBytes)    

        if VErr < 0 :
            #Error
            self.ui.statusbar.setStyleSheet("QStatusBar{background:red;color:white;font-weight:bold;}")      
            self.ui.statusbar.showMessage('Set pixel sequencer FAILED',0) # le 0 est un temps en seconde 
            pass
        else:
            # OK
            self.ui.statusbar.setStyleSheet("QStatusBar{background:MidLight;color:black;font-weight:normal;}")      
            self.ui.statusbar.showMessage('Set pixel sequencer successfull',0) # le 0 est un temps en seconde 
            pass
        
        self.Flag_Set_PixelSequence = 1
    
    
    #Execute when "Get Activated" is clicked 
    def get_PixSeq_Clicked(self) :
        """
            Registers Tab
                Pixel Sequencer Tab
                    Get button callback
        """

        VErr , returned_value = PicmicHLF.FGetPixelSequencerRegs()

        if VErr < 0 :
            #Error
            self.ui.statusbar.setStyleSheet("QStatusBar{background:red;color:white;font-weight:bold;}")      
            self.ui.statusbar.showMessage('Get pixel sequencer FAILED',0) # le 0 est un temps en seconde 
        else:
            # OK
            self.ui.statusbar.setStyleSheet("QStatusBar{background:MidLight;color:black;font-weight:normal;}")      
            self.ui.statusbar.showMessage('Get pixel sequencer  successfull',0) # le 0 est un temps en seconde 

            #returned_value[0] -> element 0 de la liste
            self.ui.Get_FlushModule_PixSeq.setText('{:d}'.format( int(returned_value[0]) ))
            self.ui.Get_NU1_Pix_PixSeq.setText('{:d}'.format( int(returned_value[1]) ))
            self.ui.Get_MarkedMod_PixSeq.setText('{:d}'.format( int(returned_value[2]) ))
            self.ui.Get_NU2_Pix_PixSeq.setText('{:d}'.format( int(returned_value[3]) ))
            self.ui.Get_PulseMod_PixSeq.setText('{:d}'.format( int(returned_value[4]) ))
            self.ui.Get_LoadWidth_PixSeq.setText('{:d}'.format( int(returned_value[5]) ))
            self.ui.Get_Load_pLSB_PixSeq.setText('{:d}'.format( int(returned_value[6]) ))
            self.ui.Get_Load_PMSB_PixSeq.setText('{:d}'.format( int(returned_value[7]) ))
            self.ui.Get_Flush_PLSB_PixSeq.setText('{:d}'.format( int(returned_value[8]) ))
            self.ui.Get_Flush_PMSB_PixSeq.setText('{:d}'.format( int(returned_value[9]) ))
            self.ui.Get_APulse_pLSB_PixSeq.setText('{:d}'.format( int(returned_value[10]) ))
            self.ui.Get_APulse_pMSB_PixSeq.setText('{:d}'.format( int(returned_value[11]) ))
            self.ui.Get_DPulse_pLSB_PixSeq.setText('{:d}'.format( int(returned_value[12]) ))
            self.ui.Get_DPulse_pMSB_PixSeq.setText('{:d}'.format( int(returned_value[13]) ))
            self.ui.Get_RdPixMaskLSB_PixSeq.setText('{:d}'.format( int(returned_value[14]) ))
            self.ui.Get_RdPixMaskMSB_PixSeq.setText('{:d}'.format( int(returned_value[15]) ))
            self.ui.Get_MaxFrameLSB_PixSeq.setText('{:d}'.format( int(returned_value[16]) ))
            self.ui.Get_MaxFrameMSB_PixSeq.setText('{:d}'.format( int(returned_value[17]) ))
            self.ui.Get_PolarityLSB_PixSeq.setText('{:d}'.format( int(returned_value[18]) ))
            self.ui.Get_PolarityMSB_PixSeq.setText('{:d}'.format( int(returned_value[19]) ))
            self.ui.Get_Marker1LSB_PixSeq.setText('{:d}'.format( int(returned_value[20]) ))
            self.ui.Get_Marker1MSB_PixSeq.setText('{:d}'.format( int(returned_value[21]) ))
            self.ui.Get_Marker2LSB_PixSeq.setText('{:d}'.format( int(returned_value[22]) ))
            self.ui.Get_Marker2MSB_PixSeq.setText('{:d}'.format( int(returned_value[23]) ))

            if(self.Flag_Set_PixelSequence == 1):
                pass
    
    
    # Set / Get buttons : 
    def Set_Button_Test_Struct_Clicked(self) :
        """
            Registers Tab
                Test Structure and Control Tab
                    Set button callback
        """
   
        VErr = PicmicHLF.FSetTestGlobBiasReg(self.binary_input_TestStruct)    

        if VErr < 0 :
            #Error
            self.ui.statusbar.setStyleSheet("QStatusBar{background:red;color:white;font-weight:bold;}")      
            self.ui.statusbar.showMessage('Set test structure FAILED',0) # le 0 est un temps en seconde 
            pass
        else:
            # OK
            self.ui.statusbar.setStyleSheet("QStatusBar{background:MidLight;color:black;font-weight:normal;}")      
            self.ui.statusbar.showMessage('Set test structure successfull',0) # le 0 est un temps en seconde 
            pass
            
        self.Flag_Set_TestStruct = 1

            
    def Get_Test_Struct_Clicked(self) :
        """
            Registers Tab
                Test Structure and Control Tab
                    Set button callback
        """
    
        VErr, returned_value = PicmicHLF.FGetTestGlobBiasReg()

        if VErr < 0 :
            #Error
            self.ui.statusbar.setStyleSheet("QStatusBar{background:red;color:white;font-weight:bold;}")      
            self.ui.statusbar.showMessage('Get test Structure FAILED',0) # le 0 est un temps en seconde 
            pass
        else:
            # OK
            self.ui.statusbar.setStyleSheet("QStatusBar{background:MidLight;color:black;font-weight:normal;}")      
            self.ui.statusbar.showMessage('Get test Structure successfull',0) # le 0 est un temps en seconde 
        
            if(self.Flag_Set_TestStruct == 1):
     
                if(int(returned_value[0]) != self.binary_input_TestStruct):
                    self.ui.statusbar.setStyleSheet("color : red")
                    self.ui.statusbar.showMessage('GET ERROR : Value to send different from Current Value',0)
                    
                else :
                    self.ui.statusbar.setStyleSheet("color : green")
                    self.ui.statusbar.showMessage('GET OK : Value to send = Current Value',0)

            self.ui.Text_Get_Test_Struct.setText('{:X}'.format( returned_value[0] ))
                    
            self.DisplayBinaryOnTestStructOutputCheckboxes(returned_value[0])


    def TestStructTextChanged(self):
        """
            Registers Tab
                Test Structure and Control Tab
                    Set text box  callback
        """

        if self.ui.Text_Set_Test_Struct.text() != "":
            if self.binary_input_TestStruct != int(self.ui.Text_Set_Test_Struct.text(),16):
                # report change to the checkboxes
                self.binary_input_TestStruct = int(self.ui.Text_Set_Test_Struct.text(),16)
                self.ui.Set_SW0.setChecked((self.binary_input_TestStruct & 0x01) == 0x01)
                self.ui.Set_SW1.setChecked((self.binary_input_TestStruct & 0x02) == 0x02)
                self.ui.Set_EN_CM.setChecked((self.binary_input_TestStruct & 0x04) == 0x04)
                self.ui.Set_EN_CC.setChecked((self.binary_input_TestStruct & 0x08) == 0x08)
                self.ui.Set_ENA_CM1.setChecked((self.binary_input_TestStruct & 0x10) == 0x10)
                self.ui.Set_ENA_D2P.setChecked((self.binary_input_TestStruct & 0x20) == 0x20)
                self.ui.Set_ENA_D1P.setChecked((self.binary_input_TestStruct & 0x40) == 0x40)
        
     
    def Set_SW0_Clicked(self) :
        """
            Registers Tab
                Test Structure and Control Tab
                    SW0 Checkbox  callback
        """
    
        #If checked 
        if self.ui.Set_SW0.isChecked():
            self.binary_input_TestStruct = self.binary_input_TestStruct | 0x01
        else : 
            self.binary_input_TestStruct = self.binary_input_TestStruct & 0xFE
            
        self.ui.Text_Set_Test_Struct.setText('{:X}'.format( self.binary_input_TestStruct ))
            
            
    def Set_SW1_Clicked(self) :
        """
            Registers Tab
                Test Structure and Control Tab
                    SW1 Checkbox  callback
        """

        #If checked 
        if self.ui.Set_SW1.isChecked():
            self.binary_input_TestStruct = self.binary_input_TestStruct | 0x02
        else : 
            self.binary_input_TestStruct = self.binary_input_TestStruct & 0xFD
            
        self.ui.Text_Set_Test_Struct.setText('{:X}'.format( self.binary_input_TestStruct ))
            
            
    def Set_EN_CM_Clicked(self) :
        """
            Registers Tab
                Test Structure and Control Tab
                    Enable CM Checkbox  callback
        """

        #If checked 
        if self.ui.Set_EN_CM.isChecked():
            self.binary_input_TestStruct = self.binary_input_TestStruct | 0x04
        else : 
            self.binary_input_TestStruct = self.binary_input_TestStruct & 0xFB
            
        self.ui.Text_Set_Test_Struct.setText('{:X}'.format( self.binary_input_TestStruct ))
            
            
    def Set_EN_CC_Clicked(self) :
        """
            Registers Tab
                Test Structure and Control Tab
                    Enable CC  callback
        """
         
        #If checked 
        if self.ui.Set_EN_CC.isChecked():
            self.binary_input_TestStruct = self.binary_input_TestStruct | 0x08
        else : 
            self.binary_input_TestStruct = self.binary_input_TestStruct & 0xF7
            
        self.ui.Text_Set_Test_Struct.setText('{:X}'.format( self.binary_input_TestStruct ))
            
            
    def Set_ENA_CM1_Clicked(self) :
        """
            Registers Tab
                Test Structure and Control Tab
                    Enable CM1 Checkbox  callback
        """
         
        #If checked 
        if self.ui.Set_ENA_CM1.isChecked():
            self.binary_input_TestStruct = self.binary_input_TestStruct | 0x10
        else : 
            self.binary_input_TestStruct = self.binary_input_TestStruct & 0xEF
            
        self.ui.Text_Set_Test_Struct.setText('{:X}'.format( self.binary_input_TestStruct ))
            
            
    def Set_ENA_D2P_Clicked(self) :
        """
            Registers Tab
                Test Structure and Control Tab
                    Enable 2nd protection diod Checkbox  callback
                    WARNING : inverted logic: when checked disable the diod
        """
         
        #If checked 
        if self.ui.Set_ENA_D2P.isChecked():
            self.binary_input_TestStruct = self.binary_input_TestStruct | 0x20
        else : 
            self.binary_input_TestStruct = self.binary_input_TestStruct & 0xDF
            
        self.ui.Text_Set_Test_Struct.setText('{:X}'.format( self.binary_input_TestStruct ))
            
            
    def Set_ENA_D1P_Clicked(self) :
        """
            Registers Tab
                Test Structure and Control Tab
                    Enable 1st protection diod Checkbox  callback
                    WARNING : inverted logic: when checked disable the diod
        """
         
        #If checked 
        if self.ui.Set_ENA_D1P.isChecked():
            self.binary_input_TestStruct = self.binary_input_TestStruct | 0x40
        else : 
            self.binary_input_TestStruct = self.binary_input_TestStruct & 0xBF
            
        self.ui.Text_Set_Test_Struct.setText('{:X}'.format( self.binary_input_TestStruct ))
  
  
    def DisplayBinaryOnTestStructOutputCheckboxes(self,number) :
        """
            Registers Tab
                Test Structure and Control Tab
                    set the checkboxes accordingly to the byte value
        """
        
        self.ui.Check_SW0.setChecked((number & 0x01) == 0x01)
        self.ui.Check_SW1.setChecked((number & 0x02) == 0x02)
        self.ui.Check_EN_CM.setChecked((number & 0x04) == 0x04)
        self.ui.Check_EN_CC.setChecked((number & 0x08) == 0x08)
        self.ui.Check_ENA_CM1.setChecked((number & 0x10) == 0x10)
        self.ui.Check_ENA_D2P.setChecked((number & 0x20) == 0x20)
        self.ui.Check_ENA_D1P.setChecked((number & 0x40) == 0x40)


            
    def ResetPixelMatrixMemories(self):
        """
            Registers Tab
                Pixel Configuration  Tab
                    Reset Pixel matrix memorie button  callback
        """
        
        #ResetValue = self.ui.Text_Set_Data_PixConf.text()
        VErr = PicmicHLF.FResetPixelMemoryMatrix(self.binary_input_PixConfData) 
        if VErr < 0 :
            #Error
            self.ui.statusbar.setStyleSheet("QStatusBar{background:red;color:white;font-weight:bold;}")      
            
            self.ui.statusbar.showMessage('Reset Pixel matrix FAILED',0) # le 0 est un temps en seconde 
            pass
        else:
            # OK
            self.ui.statusbar.setStyleSheet("QStatusBar{background:MidLight;color:black;font-weight:normal;}")      
            
            self.ui.statusbar.showMessage('Reset Pixel matrix successfull',0) # le 0 est un temps en seconde 
            pass
            
        
    def Set_Button_Col_PixConf_Clicked(self) :
        """
            Registers Tab
                Pixel Configuration  Tab
                    Set Column pixel conf register button  callback
        """
     
        input_PixConfCol = int(self.ui.Text_Set_Col_PixConf.text(),16) # get the current text

        VErr = PicmicHLF.FSetPixConfColReg(input_PixConfCol) 
        
        self.Flag_Set_PixSeqCol = 1
        if VErr < 0 :
            #Error
            self.ui.statusbar.setStyleSheet("QStatusBar{background:red;color:white;font-weight:bold;}")      
            self.ui.statusbar.showMessage('Set Pix col conf FAILED',0) # le 0 est un temps en seconde 
            pass
        else:
            # OK
            self.ui.statusbar.setStyleSheet("QStatusBar{background:MidLight;color:black;font-weight:normal;}")      
            self.ui.statusbar.showMessage('Set Pix col conf successfull',0) # le 0 est un temps en seconde 
            pass
            
            
    def Get_Col_PixConf_Clicked(self) :
        """
            Registers Tab
                Pixel Configuration  Tab
                    Get Column pixel conf register button  callback
        """
             
        VErr, returned_value = PicmicHLF.FGetPixConfColReg()

        if VErr < 0 :
            #Error
            self.ui.statusbar.setStyleSheet("QStatusBar{background:red;color:white;font-weight:bold;}")      
            self.ui.statusbar.showMessage('Get Pix col conf FAILED',0) # le 0 est un temps en seconde 
        else:
            # OK
            self.ui.statusbar.setStyleSheet("QStatusBar{background:MidLight;color:black;font-weight:normal;}")      
            self.ui.statusbar.showMessage('Get Pix col conf successfull',0) # le 0 est un temps en seconde 

        
            self.ui.Text_Get_Col_PixConf.setText('{:X}'.format( returned_value[0] ))

            self.ui.Check_SelSelAllCol_PixConf.setChecked((returned_value[0] & 0x40)==0x40)
            self.ui.Check_SelDeselAllCol_PixConf.setChecked((returned_value[0] & 0x80)==0x80)
        
            if(self.Flag_Set_PixSeqCol == 1):
     
                if(returned_value[0] != self.byte_input_PixConfCol):
                    self.ui.statusbar.setStyleSheet("color : red")
                    self.ui.statusbar.showMessage('GET ERROR : Value to send different from Current Value',0)
                    
                else :
                    self.ui.statusbar.setStyleSheet("color : green")
                    self.ui.statusbar.showMessage('GET OK : Value to send = Current Value',0)
    
    
     
    def Radio_SelCol_PixConf_Clicked(self) :
        """
            Registers Tab
                Pixel Configuration  Tab
                    Enable individual column selection
                    Column selection radio button  callback
        """
             
        #If checked 
        if self.ui.Radio_SelCol_PixConf.isChecked():
            self.ui.Text_Set_Col_PixConf.setEnabled(True) # Enable the possibility of adding own value
            self.byte_input_PixConfCol= 0x00 
            self.ui.Text_Set_Col_PixConf.setText('{:X}'.format( self.byte_input_PixConfCol ))   
            
            
    def Radio_SelAllCol_PixConf_Clicked(self) :
        """
            Registers Tab
                Pixel Configuration  Tab
                    Select all columns
                    Column selection radio button  callback
        """
             
        #If checked 
        if self.ui.Radio_SelAllCol_PixConf.isChecked():
            self.ui.Text_Set_Col_PixConf.setEnabled(False) #Disable the possibility to add your own value 
            self.byte_input_PixConfCol= 0x40 #64 in dec, mean that the SEL ALL bit is on
            
            self.ui.Text_Set_Col_PixConf.setText('{:X}'.format( self.byte_input_PixConfCol ))   
    
    
    def Radio_DeselAllCol_PixConf_Clicked(self) :
        """
            Registers Tab
                Pixel Configuration  Tab
                    Unselect all collumns
                    Column selection radio button  callback
        """
             
        #If checked 
        if self.ui.Radio_DeselAllCol_PixConf.isChecked():
            self.ui.Text_Set_Col_PixConf.setEnabled(False) #Disable the possibility to add your own value 
            self.byte_input_PixConfCol= 0x80 #128 in dec, mean that the DESELALL bit is on
            self.ui.Text_Set_Col_PixConf.setText('{:X}'.format( self.byte_input_PixConfCol ))   


    def Set_Button_Row_PixConf_Clicked(self) :
        """
            Registers Tab
                Pixel Configuration  Tab
                    Set Row pixel conf register button  callback
        """
    
        self.byte_input_PixConfRow = int(self.ui.Text_Set_Row_PixConf.text(),10) ## 16) comment to set row,col in decimal
        VErr = PicmicHLF.FSetPixConfRowReg(self.byte_input_PixConfRow) 
        if VErr < 0 :
            #Error
            self.ui.statusbar.setStyleSheet("QStatusBar{background:red;color:white;font-weight:bold;}")      
            self.ui.statusbar.showMessage('Set Pix row conf FAILED',0) # le 0 est un temps en seconde 
            pass
        else:
            # OK
            self.ui.statusbar.setStyleSheet("QStatusBar{background:MidLight;color:black;font-weight:normal;}")      
            self.ui.statusbar.showMessage('Set Pix row conf successfull',0) # le 0 est un temps en seconde 
            pass
        
        self.Flag_Set_PixSeqRow = 1

          
    def Get_Row_PixConf_Clicked(self) :
        """
            Registers Tab
                Pixel Configuration  Tab
                    Get Row pixel conf register button  callback
        """
    
        VErr, returned_value = PicmicHLF.FGetPixConfRowReg()

        if VErr < 0 :
            #Error
            self.ui.statusbar.setStyleSheet("QStatusBar{background:red;color:white;font-weight:bold;}")      
            self.ui.statusbar.showMessage('Get Pix row conf FAILED',0) # le 0 est un temps en seconde 
        else:
            # OK
            self.ui.statusbar.setStyleSheet("QStatusBar{background:MidLight;color:black;font-weight:normal;}")      
            self.ui.statusbar.showMessage('Get Pix row conf successfull',0) # le 0 est un temps en seconde 

            self.ui.Text_Get_Row_PixConf.setText('{:d}'.format( returned_value[0] )) # to set row,col to decimal '{:X}' changed by '{:d}'
            self.ui.Check_SelAllRow_Row_PixConf.setChecked((returned_value[0] & 0x80)==0x80)
        
            if(self.Flag_Set_PixSeqRow == 1):

                if(returned_value[0] != self.byte_input_PixConfRow):
                    self.ui.statusbar.setStyleSheet("color : red")
                    self.ui.statusbar.showMessage('GET ERROR : Value to send different from Current Value',0)
                    
                else :
                    self.ui.statusbar.setStyleSheet("color : green")
                    self.ui.statusbar.showMessage('GET OK : Value to send = Current Value',0)
        
     
    def Radio_SelRow_Row_PixConf_Clicked(self) :
        """
            Registers Tab
                Pixel Configuration  Tab
                    Enable individual Row selection
                    Row selection radio button  callback
        """
         
        #If checked 
        if self.ui.Radio_SelRow_Row_PixConf.isChecked():
            self.ui.Text_Set_Row_PixConf.setEnabled(True) # Enable the possibility of adding own value
            self.byte_input_PixConfRow = 0
            self.ui.Text_Set_Row_PixConf.setText('{:X}'.format( self.byte_input_PixConfRow ))            
            
            
    def Radio_SelAllRow_Row_PixConf_Clicked(self) :
        """
            Registers Tab
                Pixel Configuration  Tab
                    Select all rows
                    Row selection radio button  callback
        """
         
        #If checked 
        if self.ui.Radio_SelAllRow_Row_PixConf.isChecked():
            self.ui.Text_Set_Row_PixConf.setEnabled(False) #Disable the possibility to add your own value 
            self.byte_input_PixConfRow = 0x80
            self.ui.Text_Set_Row_PixConf.setText('{:X}'.format( self.byte_input_PixConfRow ))            
    
    
    #Pixel Conf DATA GROUP : 
    
    #Set/Get buttons 
    def Set_Button_Data_PixConf_Clicked(self) :
        """
            Registers Tab
                Pixel Configuration  Tab
                    Set Data pixel conf register button  callback
        """
        
        self.logger.info("pixconfdata to send :{}".format(self.binary_input_PixConfData))
        VErr = PicmicHLF.FSetPixConfDataReg(self.binary_input_PixConfData) 
        
        self.Flag_Set_PixSeqData = 1
        if VErr < 0 :
            #Error
            self.ui.statusbar.setStyleSheet("QStatusBar{background:red;color:white;font-weight:bold;}")      
            self.ui.statusbar.showMessage('Set Pix data conf FAILED',0) # le 0 est un temps en seconde 
            pass
        else:
            # OK
            self.ui.statusbar.setStyleSheet("QStatusBar{background:MidLight;color:black;font-weight:normal;}")      
            self.ui.statusbar.showMessage('Set Pix data conf successfull',0) # le 0 est un temps en seconde 
            pass
            
            
    def Get_Data_PixConf_Clicked(self) :
        """
            Registers Tab
                Pixel Configuration  Tab
                    Get Data pixel conf register button  callback
        """
    
        VErr, returned_value = PicmicHLF.FGetPixConfDataReg()
        
        if VErr < 0 :
            #Error
            self.ui.statusbar.setStyleSheet("QStatusBar{background:red;color:white;font-weight:bold;}")      
            self.ui.statusbar.showMessage('Set Pix data conf FAILED',0) # le 0 est un temps en seconde 
        else:
            # OK
            self.ui.statusbar.setStyleSheet("QStatusBar{background:MidLight;color:black;font-weight:normal;}")      
            self.ui.statusbar.showMessage('Set Pix data conf successfull',0) # le 0 est un temps en seconde 
        
            if(self.Flag_Set_PixSeqData == 1):
     
                if(returned_value[0] != self.binary_input_PixConfData):
                    self.ui.statusbar.setStyleSheet("color : red")
                    self.ui.statusbar.showMessage('GET ERROR : Value to send different from Current Value',0)
                    
                else :
                    self.ui.statusbar.setStyleSheet("color : green")
                    self.ui.statusbar.showMessage('GET OK : Value to send = Current Value',0)
    
            self.ui.Text_Get_Data_PixConf.setText('{:X}'.format( returned_value[0] ))
            self.ui.Get_IADJ_Data_PixConf.setText('{:X}'.format( returned_value[0]& 0x07 ))
            self.ui.Check_ENA_CM_Data_PixConf.setChecked(  ( returned_value[0] & 0x08 ) == 0x08 )
            self.ui.Check_SW0_Data_PixConf.setChecked(  ( returned_value[0] & 0x10 ) == 0x10 )
            self.ui.Check_SW1_Data_PixConf.setChecked(  ( returned_value[0] & 0x20 ) == 0x20 )
            self.ui.Check_ENA_CC_Data_PixConf.setChecked(  ( returned_value[0] & 0x40 ) == 0x40 )
            self.ui.Check_ActVpulse_Data_PixConf.setChecked(  ( returned_value[0] & 0x80 ) == 0x80 )
 

    def Text_Set_Data_PixConf_textChanged(self):
        """
            Registers Tab
                Pixel Configuration  Tab
                    Set text box  callback
        """
        if (self.ui.Text_Set_Data_PixConf.text() != ''):
            self.binary_input_PixConfData = int(self.ui.Text_Set_Data_PixConf.text(),16)
            self.ui.Set_IADJ_Data_PixConf.setValue(self.binary_input_PixConfData & 0x07)
            self.ui.Set_ENA_CM_Data_PixConf.setChecked((self.binary_input_PixConfData & 0x08) == 0x08)
            self.ui.Set_SW0_Data_PixConf.setChecked((self.binary_input_PixConfData & 0x10) == 0x10)
            self.ui.Set_SW1_Data_PixConf.setChecked((self.binary_input_PixConfData & 0x20) == 0x20)
            self.ui.Set_ENA_CC_Data_PixConf.setChecked((self.binary_input_PixConfData & 0x40) == 0x40)
            self.ui.Set_ActivateVpulse_Data_PixConf.setChecked((self.binary_input_PixConfData & 0x80) == 0x80)
    
    
    # ALL CHECKBOXES FUNCTIONS
    def Set_IADJ_Data_PixConf_Clicked(self) : #Bit 0 à 2
        """
            Registers Tab
                Pixel Configuration  Tab
                    IAdj spinbox  callback
        """
        
        self.binary_input_PixConfData = (self.binary_input_PixConfData & 0xF8) | (self.ui.Set_IADJ_Data_PixConf.value() & 0x07)
        self.ui.Text_Set_Data_PixConf.setText('{:X}'.format(self.binary_input_PixConfData))
            
            
    def Set_ENA_CM_Data_PixConf_Clicked(self) :
        """
            Registers Tab
                Pixel Configuration  Tab
                    Ena_CM Checkbox  callback
        """
         
        #If checked 
        if self.ui.Set_ENA_CM_Data_PixConf.isChecked():
            self.binary_input_PixConfData = self.binary_input_PixConfData | 0x08
        else : 
            self.binary_input_PixConfData = self.binary_input_PixConfData & 0xF7
            
        self.ui.Text_Set_Data_PixConf.setText('{:X}'.format(self.binary_input_PixConfData))
            
    def Set_SW0_Data_PixConf_Clicked(self) :
        """
            Registers Tab
                Pixel Configuration  Tab
                    SW0 Checkbox  callback
        """
         
        #If checked 
        if self.ui.Set_SW0_Data_PixConf.isChecked():
            self.binary_input_PixConfData = self.binary_input_PixConfData | 0x10
        else : 
            self.binary_input_PixConfData = self.binary_input_PixConfData & 0xEF
            
        self.ui.Text_Set_Data_PixConf.setText('{:X}'.format(self.binary_input_PixConfData))
        
    def Set_SW1_Data_PixConf_Clicked(self) :
        """
            Registers Tab
                Pixel Configuration  Tab
                    SW1 Checkbox  callback
        """
         
        #If checked 
        if self.ui.Set_SW1_Data_PixConf.isChecked():
            self.binary_input_PixConfData = self.binary_input_PixConfData | 0x20
        else : 
            self.binary_input_PixConfData = self.binary_input_PixConfData & 0xDF
            
        self.ui.Text_Set_Data_PixConf.setText('{:X}'.format(self.binary_input_PixConfData))
            
    def Set_ENA_CC_Data_PixConf_Clicked(self) :
        """
            Registers Tab
                Pixel Configuration  Tab
                    Ena_CC Checkbox  callback
        """
         
        #If checked 
        if self.ui.Set_ENA_CC_Data_PixConf.isChecked():
            self.binary_input_PixConfData = self.binary_input_PixConfData | 0x40
        else : 
            self.binary_input_PixConfData = self.binary_input_PixConfData & 0xBF
            
        self.ui.Text_Set_Data_PixConf.setText('{:X}'.format(self.binary_input_PixConfData))
             
    def Set_ActivateVpulse_Data_PixConf_Clicked(self) :
        """
            Registers Tab
                Pixel Configuration  Tab
                    Activate VPulse Checkbox  callback
        """
         
        #If checked 
        if self.ui.Set_ActivateVpulse_Data_PixConf.isChecked():
            self.binary_input_PixConfData = self.binary_input_PixConfData | 0x80
        else : 
            self.binary_input_PixConfData = self.binary_input_PixConfData & 0x7F
            
        self.ui.Text_Set_Data_PixConf.setText('{:X}'.format(self.binary_input_PixConfData))
    
    def Set_Button_All_DAC_Clicked(self) :
        """
            Registers Tab
                DAC  Tab
                    Set DAC values button  callback
        """
        
        DAC0_value = int(self.ui.Text_Set_DAC0.text(),10)
        DAC1_value = int(self.ui.Text_Set_DAC1.text(),10)
        DAC2_value = int(self.ui.Text_Set_DAC2.text(),10)
        DAC3_value = int(self.ui.Text_Set_DAC3.text(),10)
        DAC4_value = int(self.ui.Text_Set_DAC4.text(),10)
        
        VErr = PicmicHLF.FSetDacRegs ([DAC0_value,DAC1_value,DAC2_value,DAC3_value,DAC4_value])
        
        self.Flag_Set_DAC = 1
        if VErr < 0 :
            #Error
            self.ui.statusbar.setStyleSheet("QStatusBar{background:red;color:white;font-weight:bold;}")      
            self.ui.statusbar.showMessage('Set dac regs FAILED',0) # le 0 est un temps en seconde 
            pass
        else:
            # OK
            self.ui.statusbar.setStyleSheet("QStatusBar{background:MidLight;color:black;font-weight:normal;}")      
            self.ui.statusbar.showMessage('Set dac regs successfull',0) # le 0 est un temps en seconde 
            pass

        
    def Get_Button_All_DAC_Clicked(self) :
        """
            Registers Tab
                DAC  Tab
                    Get DAC values button  callback
        """

        VErr, returned_value = PicmicHLF.FGetDacRegs()
        
        if VErr < 0 :
            #Error
            self.ui.statusbar.setStyleSheet("QStatusBar{background:red;color:white;font-weight:bold;}")      
            self.ui.statusbar.showMessage('get dac regs FAILED',0) # le 0 est un temps en seconde 
        else:
            # OK
            self.ui.statusbar.setStyleSheet("QStatusBar{background:MidLight;color:black;font-weight:normal;}")      
            self.ui.statusbar.showMessage('get dac regs successfull',0) # le 0 est un temps en seconde 

            self.ui.Text_Get_DAC0.setText('{:d}'.format( returned_value[0] ))
            self.ui.Text_Get_DAC1.setText('{:d}'.format( returned_value[1] ))
            self.ui.Text_Get_DAC2.setText('{:d}'.format( returned_value[2] ))
            self.ui.Text_Get_DAC3.setText('{:d}'.format( returned_value[3] ))
            self.ui.Text_Get_DAC4.setText('{:d}'.format( returned_value[4] ))

        
    #Set/Get buttons DAC Switch
    def Set_All_Bytes_DacSwitch_Clicked(self) :
        """
            Registers Tab
                DAC  Tab
                    Set DAC switches button  callback
        """
        
        VErr = PicmicHLF.FSetDacSWRegs ([self.binary_input_DAC_Byte1,self.binary_input_DAC_Byte2,self.binary_input_DAC_Byte3])
        
        self.Flag_Set_DACSW = 1
        if VErr < 0 :
            #Error
            self.ui.statusbar.setStyleSheet("QStatusBar{background:red;color:white;font-weight:bold;}")      
            self.ui.statusbar.showMessage('Set dac sw FAILED',0) # le 0 est un temps en seconde 
            pass
        else:
            # OK
            self.ui.statusbar.setStyleSheet("QStatusBar{background:MidLight;color:black;font-weight:normal;}")      
            self.ui.statusbar.showMessage('Set dac sw successfull',0) # le 0 est un temps en seconde 
            pass

           
    def Get_All_Bytes_DacSwitch_Clicked(self) :
        """
            Registers Tab
                DAC  Tab
                    Get DAC switches button  callback
        """
    
        VErr, returned_value = PicmicHLF.FGetDacSWRegs()

        if VErr < 0 :
            #Error
            self.ui.statusbar.setStyleSheet("QStatusBar{background:red;color:white;font-weight:bold;}")      
            self.ui.statusbar.showMessage('Get dac sw FAILED',0) # le 0 est un temps en seconde 
        else:
            # OK
            self.ui.statusbar.setStyleSheet("QStatusBar{background:MidLight;color:black;font-weight:normal;}")      
            self.ui.statusbar.showMessage('Get dac sw successfull',0) # le 0 est un temps en seconde 

            self.ui.RegDacText_Get_Byte1.setText('{:X}'.format( int(returned_value[0]) ))
            self.ui.RegDacText_Get_Byte2.setText('{:X}'.format( int(returned_value[1]) ))
            self.ui.RegDacText_Get_Byte3.setText('{:X}'.format( int(returned_value[2]) ))
            
            self.DisplayBinaryOnDACSwitchOutputCheckboxes(int(returned_value[0]),int(returned_value[1]),int(returned_value[2]))
    
    
    
    def Set_en_bg_Byte1_Clicked(self) :
        """
            Registers Tab
                DAC  Tab
                    en_bg checkbox  callback
        """
        #If checked 
        if self.ui.Set_en_bg_Byte1.isChecked():
            self.binary_input_DAC_Byte1 = self.binary_input_DAC_Byte1 | 0x01            
        else : 
            self.binary_input_DAC_Byte1 = self.binary_input_DAC_Byte1 & 0xFE   
            
        self.ui.RegDacText_Set_Byte1.setText('{:X}'.format( self.binary_input_DAC_Byte1 ))
        

    def Set_IREF_b0_Byte1_Clicked(self) :
        """
            Registers Tab
                DAC  Tab
                    IRef_b0 checkbox  callback
        """
        #If checked 
        if self.ui.Set_IREF_b0_Byte1.isChecked():
            self.binary_input_DAC_Byte1 = self.binary_input_DAC_Byte1 | 0x02
        else : 
            self.binary_input_DAC_Byte1 = self.binary_input_DAC_Byte1 & 0xFD
            
        self.ui.RegDacText_Set_Byte1.setText('{:X}'.format( self.binary_input_DAC_Byte1 ))

    
    def Set_IREF_b1_Byte1_Clicked(self) :
        """
            Registers Tab
                DAC  Tab
                    IRef_b1 checkbox  callback
        """

        #If checked 
        if self.ui.Set_IREF_b1_Byte1.isChecked():
            self.binary_input_DAC_Byte1 = self.binary_input_DAC_Byte1 | 0x04
        else : 
            self.binary_input_DAC_Byte1 = self.binary_input_DAC_Byte1 & 0xFB
            
        self.ui.RegDacText_Set_Byte1.setText('{:X}'.format( self.binary_input_DAC_Byte1 ))
            

    def Set_IREF_b2_Byte1_Clicked(self) :
        """
            Registers Tab
                DAC  Tab
                    IRef_b2 checkbox  callback
        """

        #If checked 
        if self.ui.Set_IREF_b2_Byte1.isChecked():
            self.binary_input_DAC_Byte1 = self.binary_input_DAC_Byte1 | 0x08
        else : 
            self.binary_input_DAC_Byte1 = self.binary_input_DAC_Byte1 & 0xF7
            
        self.ui.RegDacText_Set_Byte1.setText('{:X}'.format( self.binary_input_DAC_Byte1 ))


    def Set_ENA_IREF_ext_Byte1_Clicked(self) :
        """
            Registers Tab
                DAC  Tab
                    Ena_IRef_ext checkbox  callback
        """

        #If checked 
        if self.ui.Set_ENA_IREF_ext_Byte1.isChecked():
            self.binary_input_DAC_Byte1 = self.binary_input_DAC_Byte1 | 0x10
        else : 
            self.binary_input_DAC_Byte1 = self.binary_input_DAC_Byte1 & 0xEF
            
        self.ui.RegDacText_Set_Byte1.setText('{:X}'.format( self.binary_input_DAC_Byte1 ))
            

    def Set_ENA_IP_Byte1_Clicked(self) :
        """
            Registers Tab
                DAC  Tab
                    Ena_IP checkbox  callback
        """

        #If checked 
        if self.ui.Set_ENA_IP_Byte1.isChecked():
            self.binary_input_DAC_Byte1 = self.binary_input_DAC_Byte1 | 0x20
        else : 
            self.binary_input_DAC_Byte1 = self.binary_input_DAC_Byte1 & 0xDF
            
        self.ui.RegDacText_Set_Byte1.setText('{:X}'.format( self.binary_input_DAC_Byte1 ))


    def Set_ENA_IN_Byte1_Clicked(self) :
        """
            Registers Tab
                DAC  Tab
                    Ena_IN checkbox  callback
        """

        #If checked 
        if self.ui.Set_ENA_IN_Byte1.isChecked():
            self.binary_input_DAC_Byte1 = self.binary_input_DAC_Byte1 | 0x40
        else : 
            self.binary_input_DAC_Byte1 = self.binary_input_DAC_Byte1 & 0xBF
            
        self.ui.RegDacText_Set_Byte1.setText('{:X}'.format( self.binary_input_DAC_Byte1 ))

     
    def Set_ENA_IP_ext_Byte1_Clicked(self) :
        """
            Registers Tab
                DAC  Tab
                    Ena_IP_ext checkbox  callback
        """

        #If checked 
        if self.ui.Set_ENA_IP_ext_Byte1.isChecked():
            self.binary_input_DAC_Byte1 = self.binary_input_DAC_Byte1 | 0x80
        else : 
            self.binary_input_DAC_Byte1 = self.binary_input_DAC_Byte1 & 0x7F
            
        self.ui.RegDacText_Set_Byte1.setText('{:X}'.format( self.binary_input_DAC_Byte1 ))


    def RegDacByte1TextChanged(self):
        """
            Registers Tab
                DAC  Tab
                    dac_switch byte 1 text box callback
        """

        if self.ui.RegDacText_Set_Byte1.text() != "":
            if self.binary_input_DAC_Byte1 != int(self.ui.RegDacText_Set_Byte1.text(),16):
                # report change to the checkboxes
                self.binary_input_DAC_Byte1 = int(self.ui.RegDacText_Set_Byte1.text(),16)
                self.ui.Set_en_bg_Byte1.setChecked((self.binary_input_DAC_Byte1 & 0x01) == 0x01)
                self.ui.Set_IREF_b0_Byte1.setChecked((self.binary_input_DAC_Byte1 & 0x02) == 0x02)
                self.ui.Set_IREF_b1_Byte1.setChecked((self.binary_input_DAC_Byte1 & 0x04) == 0x04)
                self.ui.Set_IREF_b2_Byte1.setChecked((self.binary_input_DAC_Byte1 & 0x08) == 0x08)
                self.ui.Set_ENA_IREF_ext_Byte1.setChecked((self.binary_input_DAC_Byte1 & 0x10) == 0x10)
                self.ui.Set_ENA_IP_Byte1.setChecked((self.binary_input_DAC_Byte1 & 0x20) == 0x20)
                self.ui.Set_ENA_IN_Byte1.setChecked((self.binary_input_DAC_Byte1 & 0x40) == 0x40)
                self.ui.Set_ENA_IP_ext_Byte1.setChecked((self.binary_input_DAC_Byte1 & 0x80) == 0x80)
        
        
    def Set_ENA_IN_ext_Byte2_Clicked(self) :
        """
            Registers Tab
                DAC  Tab
                    Ena_IN_ext checkbox  callback
        """

        #If checked 
        if self.ui.Set_ENA_IN_ext_Byte2.isChecked():
            self.binary_input_DAC_Byte2 = self.binary_input_DAC_Byte2 | 0x01
        else : 
            self.binary_input_DAC_Byte2 = self.binary_input_DAC_Byte2 & 0xFE
            
        self.ui.RegDacText_Set_Byte2.setText('{:X}'.format( self.binary_input_DAC_Byte2 ))

        
    def Set_ENA_Iadj_ext_Byte2_Clicked(self) :
        """
            Registers Tab
                DAC  Tab
                    Ena_Iadj_ext checkbox  callback
        """

        #If checked 
        if self.ui.Set_ENA_Iadj_ext_Byte2.isChecked():
            self.binary_input_DAC_Byte2 = self.binary_input_DAC_Byte2 | 0x02
        else : 
            self.binary_input_DAC_Byte2 = self.binary_input_DAC_Byte2 & 0xFD
            
        self.ui.RegDacText_Set_Byte2.setText('{:X}'.format( self.binary_input_DAC_Byte2 ))

            
    def Set_ENA_CM_mes_Byte2_Clicked(self) :
        """
            Registers Tab
                DAC  Tab
                    Ena_CM_mes checkbox  callback
        """
         
        #If checked 
        if self.ui.Set_ENA_CM_mes_Byte2.isChecked():
            self.binary_input_DAC_Byte2 = self.binary_input_DAC_Byte2 | 0x04
        else : 
            self.binary_input_DAC_Byte2 = self.binary_input_DAC_Byte2 & 0xFB
            
        self.ui.RegDacText_Set_Byte2.setText('{:X}'.format( self.binary_input_DAC_Byte2 ))


    def Set_ENA_VBP_ext_Byte2_Clicked(self) :
        """
            Registers Tab
                DAC  Tab
                    Ena_VBP_ext checkbox  callback
        """
         
        #If checked 
        if self.ui.Set_ENA_VBP_ext_Byte2.isChecked():
            self.binary_input_DAC_Byte2 = self.binary_input_DAC_Byte2 | 0x08
        else : 
            self.binary_input_DAC_Byte2 = self.binary_input_DAC_Byte2 & 0xF7
            
        self.ui.RegDacText_Set_Byte2.setText('{:X}'.format( self.binary_input_DAC_Byte2 ))


    def Set_ENA_IP_mes_Byte2_Clicked(self) :
        """
            Registers Tab
                DAC  Tab
                    Ena_IP_mes checkbox  callback
        """
         
        #If checked 
        if self.ui.Set_ENA_IP_mes_Byte2.isChecked():
            self.binary_input_DAC_Byte2 = self.binary_input_DAC_Byte2 | 0x10
        else : 
            self.binary_input_DAC_Byte2 = self.binary_input_DAC_Byte2 & 0xEF
            
        self.ui.RegDacText_Set_Byte2.setText('{:X}'.format( self.binary_input_DAC_Byte2 ))

            
    def Set_ENA_IN_mes_Byte2_Clicked(self) :
        """
            Registers Tab
                DAC  Tab
                    Ena_IN_mes checkbox  callback
        """
         
        #If checked 
        if self.ui.Set_ENA_IN_mes_Byte2.isChecked():
            self.binary_input_DAC_Byte2 = self.binary_input_DAC_Byte2 | 0x20
        else : 
            self.binary_input_DAC_Byte2 = self.binary_input_DAC_Byte2 & 0xDF
            
        self.ui.RegDacText_Set_Byte2.setText('{:X}'.format( self.binary_input_DAC_Byte2 ))

     
    def Set_ENA_CM_ext_Byte2_Clicked(self) :
        """
            Registers Tab
                DAC  Tab
                    Ena_CM_ext checkbox  callback
        """
         
        #If checked 
        if self.ui.Set_ENA_CM_ext_Byte2.isChecked():
            self.binary_input_DAC_Byte2 = self.binary_input_DAC_Byte2 | 0x40
        else : 
            self.binary_input_DAC_Byte2 = self.binary_input_DAC_Byte2 & 0xBF
            
        self.ui.RegDacText_Set_Byte2.setText('{:X}'.format( self.binary_input_DAC_Byte2 ))

    
    def Set_ENA_Iadj_mes_Byte2_Clicked(self) :
        """
            Registers Tab
                DAC  Tab
                    Ena_Iadj_mes checkbox  callback
        """
         
        #If checked 
        if self.ui.Set_ENA_Iadj_mes_Byte2.isChecked():
            self.binary_input_DAC_Byte2 = self.binary_input_DAC_Byte2 | 0x80
        else : 
            self.binary_input_DAC_Byte2 = self.binary_input_DAC_Byte2 & 0x7F
            
        self.ui.RegDacText_Set_Byte2.setText('{:X}'.format( self.binary_input_DAC_Byte2 ))
            
            
    def RegDacByte2TextChanged(self):
        """
            Registers Tab
                DAC  Tab
                    dac_switch byte 2 text box callback
        """
         
        if self.ui.RegDacText_Set_Byte2.text() != "":
            if self.binary_input_DAC_Byte2 != int(self.ui.RegDacText_Set_Byte2.text(),16):
                # report change to the checkboxes
                self.binary_input_DAC_Byte2 = int(self.ui.RegDacText_Set_Byte2.text(),16)
                self.ui.Set_ENA_IN_ext_Byte2.setChecked((self.binary_input_DAC_Byte2 & 0x01) == 0x01)
                self.ui.Set_ENA_Iadj_ext_Byte2.setChecked((self.binary_input_DAC_Byte2 & 0x02) == 0x02)
                self.ui.Set_ENA_CM_mes_Byte2.setChecked((self.binary_input_DAC_Byte2 & 0x04) == 0x04)
                self.ui.Set_ENA_VBP_ext_Byte2.setChecked((self.binary_input_DAC_Byte2 & 0x08) == 0x05)
                self.ui.Set_ENA_IP_mes_Byte2.setChecked((self.binary_input_DAC_Byte2 & 0x10) == 0x10)
                self.ui.Set_ENA_CM_ext_Byte2.setChecked((self.binary_input_DAC_Byte2 & 0x20) == 0x20)
                self.ui.Set_ENA_IN_mes_Byte2.setChecked((self.binary_input_DAC_Byte2 & 0x40) == 0x40)
                self.ui.Set_ENA_Iadj_mes_Byte2.setChecked((self.binary_input_DAC_Byte2 & 0x80) == 0x80)
            
            
    #Byte 3 
    def Set_ENA_VBP_PAD_Byte3_Clicked(self) :
        """
            Registers Tab
                DAC  Tab
                    Ena_VBP_pad checkbox  callback
        """
         
        #If checked 
        if self.ui.Set_ENA_VBP_PAD_Byte3.isChecked():
            self.binary_input_DAC_Byte3 = self.binary_input_DAC_Byte3 | 0x01
            
        else : 
            self.binary_input_DAC_Byte3 = self.binary_input_DAC_Byte3 & 0xFE
            
        self.ui.RegDacText_Set_Byte3.setText('{:X}'.format( self.binary_input_DAC_Byte3 ))


    def RegDacByte3TextChanged(self):
        """
            Registers Tab
                DAC  Tab
                    dac_switch byte 3 text box callback
        """
         
        if self.ui.RegDacText_Set_Byte3.text() != "":
            if self.binary_input_DAC_Byte3 != int(self.ui.RegDacText_Set_Byte3.text()):
                # report change to the checkboxes
                self.ui.Set_ENA_VBP_PAD_Byte3.setChecked((self.binary_input_DAC_Byte3 & 0x01) == 0x01)
 
    
    def DisplayBinaryOnDACSwitchOutputCheckboxes(self,number1,number2,number3) :
        """
            Registers Tab
                DAC  Tab
                    Refresh readback checkboxes for  the DAC switches
        """

        #Byte 1
        self.ui.Check_en_bg_Byte1.setChecked((number1 & 0x01) == 0x01)
        self.ui.Check_IREF_b0_Byte1.setChecked((number1 & 0x02) == 0x02)
        self.ui.Check_IREF_b1_Byte1.setChecked((number1 & 0x04) == 0x04)
        self.ui.Check_IREF_b2_Byte1.setChecked((number1 & 0x08) == 0x08)
        self.ui.Check_ENA_IREF_ext_Byte1.setChecked((number1 & 0x10) == 0x10)
        self.ui.Check_ENA_IP_Byte1.setChecked((number1 & 0x20) == 0x20)
        self.ui.Check_ENA_IN_Byte1.setChecked((number1 & 0x40) == 0x40)
        self.ui.Check_ENA_IP_ext_Byte1.setChecked((number1 & 0x80) == 0x80)
 
        #Byte 2
        self.ui.Check_ENA_IN_ext_Byte2.setChecked((number2 & 0x01) == 0x01)
        self.ui.Check_ENA_Iadj_ext_Byte2.setChecked((number2 & 0x02) == 0x02)
        self.ui.Check_ENA_CM_mes_Byte2.setChecked((number2 & 0x04) == 0x04)
        self.ui.Check_ENA_VBP_ext_Byte2.setChecked((number2 & 0x08) == 0x05)
        self.ui.Check_ENA_IP_mes_Byte2.setChecked((number2 & 0x10) == 0x10)
        self.ui.Check_ENA_IN_mes_Byte2.setChecked((number2 & 0x20) == 0x20)
        self.ui.Check_ENA_CM_ext_Byte2.setChecked((number2 & 0x40) == 0x40)
        self.ui.Check_ENA_Iadj_mes_Byte2.setChecked((number2 & 0x80) == 0x80)
   
        #Byte 3
        self.ui.Check_ENA_VBP_PAD_Byte3.setChecked((number3 & 0x01) == 0x01)
    
    
    def SetResetBitOfVpulseSwitch(self,ByteToSet,BitToSet,BitOfSetReset) :
        '''
        ...
        
        Initialise the DLL used for the acquisition
        
        Param
        - ByteToSet     : selection of the byte 
        - BitToSet      : selection of the bit of the byte
        - BitOfSetReset : 1 :set the selected bit
                          0 : reset the selected bit
        
        Returns
        - nothinf
        
        28/11/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI
        
        '''

        if ByteToSet == 0 :
            if BitOfSetReset == 1:
                MaskToApply = 1 << BitToSet
                self.binary_input_VpulseSwitch1 = self.binary_input_VpulseSwitch1 | MaskToApply
            else:
                MaskToApply = ~(1 << BitToSet)
                self.binary_input_VpulseSwitch1 = self.binary_input_VpulseSwitch1 & MaskToApply
        elif ByteToSet == 1 :
            if BitOfSetReset == 1:
                MaskToApply = 1 << BitToSet
                self.binary_input_VpulseSwitch2 = self.binary_input_VpulseSwitch2 | MaskToApply
            else:
                MaskToApply = ~(1 << BitToSet)
                self.binary_input_VpulseSwitch2 = self.binary_input_VpulseSwitch2 & MaskToApply
            
        elif ByteToSet == 2 :
            if BitOfSetReset == 1:
                MaskToApply = 1 << BitToSet
                self.binary_input_VpulseSwitch3 = self.binary_input_VpulseSwitch3 | MaskToApply
            else:
                MaskToApply = ~(1 << BitToSet)
                self.binary_input_VpulseSwitch3 = self.binary_input_VpulseSwitch3 & MaskToApply
            
        elif ByteToSet == 3 :
            if BitOfSetReset == 1:
                MaskToApply = 1 << BitToSet
                self.binary_input_VpulseSwitch4 = self.binary_input_VpulseSwitch4 | MaskToApply
            else:
                MaskToApply = ~(1 << BitToSet)
                self.binary_input_VpulseSwitch4 = self.binary_input_VpulseSwitch4 & MaskToApply
            
        elif ByteToSet == 4 :
            if BitOfSetReset == 1:
                MaskToApply = 1 << BitToSet
                self.binary_input_VpulseSwitch5 = self.binary_input_VpulseSwitch5 | MaskToApply
            else:
                MaskToApply = ~(1 << BitToSet)
                self.binary_input_VpulseSwitch5 = self.binary_input_VpulseSwitch5 & MaskToApply
            
        elif ByteToSet == 5 :
            if BitOfSetReset == 1:
                MaskToApply = 1 << BitToSet
                self.binary_input_VpulseSwitch6 = self.binary_input_VpulseSwitch6 | MaskToApply
            else:
                MaskToApply = ~(1 << BitToSet)
                self.binary_input_VpulseSwitch6 = self.binary_input_VpulseSwitch6 & MaskToApply
            
        elif ByteToSet == 6 :
            if BitOfSetReset == 1:
                MaskToApply = 1 << BitToSet
                self.binary_input_VpulseSwitch7 = self.binary_input_VpulseSwitch7 | MaskToApply
            else:
                MaskToApply = ~(1 << BitToSet)
                self.binary_input_VpulseSwitch7 = self.binary_input_VpulseSwitch7 & MaskToApply

    
    #Set/Get buttons : 
    def Set_Vpulse_Clicked(self) :
        """
            Registers Tab
                VPulseSwitch  Tab
                    Set bits button callback
        """
        
        begin_col = int(self.ui.Text_Set_BeginCol_Vpulse.text())
        number_of_col = int(self.ui.Text_Set_NumberCol_Vpulse.text())
        
        
        bytes_index = begin_col//8              # Nous donne le numéro du byte concerné
        bit_index = begin_col%8                 #Nous donne l'index DANS le byte concerné
        
        for i in range(number_of_col) :
            
            self.SetResetBitOfVpulseSwitch(bytes_index,bit_index,1)
            
            bit_index +=1 #Increase the bit index inside of a Byte
            if bit_index >= 8 :#If we reach the end of a Byte
                bit_index = 0   #Reset the bit index for the next Byte
                bytes_index +=1 #switch to the next byte 
            
        self.ui.ListWidget_ByteState_Vpulse.clear()
        VpulseString = '{:06b} {:08b} {:08b} {:08b} {:08b} {:08b} {:08b}'.format( self.binary_input_VpulseSwitch7 , self.binary_input_VpulseSwitch6, self.binary_input_VpulseSwitch5 , self.binary_input_VpulseSwitch4 , self.binary_input_VpulseSwitch3 , self.binary_input_VpulseSwitch2 , self.binary_input_VpulseSwitch1 )
        self.ui.ListWidget_ByteState_Vpulse.addItem(VpulseString[::-1])

        
    #Reset buttons
    
    def Reset_Vpulse_Clicked(self) : #Only reset selected Columns
        """
            Registers Tab
                VPulseSwitch  Tab
                    Reset bits button callback
        """
        
        begin_col = int(self.ui.Text_Set_BeginCol_Vpulse.text())
        number_of_col = int(self.ui.Text_Set_NumberCol_Vpulse.text())
        bytes_index = begin_col//8              # Nous donne le numéro du byte concerné
        bit_index = begin_col%8                 #Nous donne l'index DANS le byte concerné
        index_total = bit_index + number_of_col #Nous donne l'index de début et l'index de fin 
        
        for i in range(number_of_col) :
            
            self.SetResetBitOfVpulseSwitch(bytes_index,bit_index,0)
            
            bit_index +=1 #Increase the bit index inside of a Byte
            if bit_index >= 8 :#If we reach the end of a Byte
                bit_index = 0   #Reset the bit index for the next Byte
                bytes_index +=1 #switch to the next byte 
            
        self.ui.ListWidget_ByteState_Vpulse.clear()

        VpulseString = '{:06b} {:08b} {:08b} {:08b} {:08b} {:08b} {:08b}'.format( self.binary_input_VpulseSwitch7 , self.binary_input_VpulseSwitch6, self.binary_input_VpulseSwitch5 , self.binary_input_VpulseSwitch4 , self.binary_input_VpulseSwitch3 , self.binary_input_VpulseSwitch2 , self.binary_input_VpulseSwitch1 )
        self.ui.ListWidget_ByteState_Vpulse.addItem(VpulseString[::-1])

            
    def ResetAll_Vpulse_Clicked(self) : # Reset ALL Columns
        """
            Registers Tab
                VPulseSwitch  Tab
                    Reset all button callback
        """
   
        self.binary_input_VpulseSwitch1 = 0
        self.binary_input_VpulseSwitch2 = 0
        self.binary_input_VpulseSwitch3 = 0
        self.binary_input_VpulseSwitch4 = 0
        self.binary_input_VpulseSwitch5 = 0
        self.binary_input_VpulseSwitch6 = 0
        self.binary_input_VpulseSwitch7 = 0
        
        self.ui.ListWidget_ByteState_Vpulse.clear()
        
        VpulseString = '{:06b} {:08b} {:08b} {:08b} {:08b} {:08b} {:08b}'.format( self.binary_input_VpulseSwitch7 , self.binary_input_VpulseSwitch6, self.binary_input_VpulseSwitch5 , self.binary_input_VpulseSwitch4 , self.binary_input_VpulseSwitch3 , self.binary_input_VpulseSwitch2 , self.binary_input_VpulseSwitch1 )
        self.ui.ListWidget_ByteState_Vpulse.addItem(VpulseString[::-1])
    
    
    def Send_ByteState_Vpulse_Clicked(self) : # Send the bytes 
        """
            Registers Tab
                VPulseSwitch  Tab
                    Send bytes state button callback
        """
        
        ListeParam = [self.binary_input_VpulseSwitch1,self.binary_input_VpulseSwitch2,
                        self.binary_input_VpulseSwitch3,
                       self.binary_input_VpulseSwitch4,self.binary_input_VpulseSwitch5,
                       self.binary_input_VpulseSwitch6,
                        self.binary_input_VpulseSwitch7]

        VErr = PicmicHLF.FSetPulseSwitchRegs (ListeParam)
        
        if VErr < 0 :
            #Error
            self.ui.statusbar.setStyleSheet("QStatusBar{background:red;color:white;font-weight:bold;}")      
            self.ui.statusbar.showMessage('Set VPulse FAILED',0) # le 0 est un temps en seconde 
        else:
            # OK
            self.ui.statusbar.setStyleSheet("QStatusBar{background:MidLight;color:black;font-weight:normal;}")      
            self.ui.statusbar.showMessage('Set VPulse successfull',0) # le 0 est un temps en seconde 
            self.Flag_Set_VpulseSw = 1
        
        
    def Get_ByteState_Vpulse_Clicked(self) : # Send the bytes 
        """
            Registers Tab
                VPulseSwitch  Tab
                    Get bytes state button callback
        """
        
        VErr, returned_value = PicmicHLF.FGetPulseSwitcheRegs ()

        if VErr < 0 :
            #Error
            self.ui.statusbar.setStyleSheet("QStatusBar{background:red;color:white;font-weight:bold;}")      
            self.ui.statusbar.showMessage('Get VPulse FAILED',0) # le 0 est un temps en seconde 
        else:
            # OK
            self.ui.statusbar.setStyleSheet("QStatusBar{background:MidLight;color:black;font-weight:normal;}")      
            self.ui.statusbar.showMessage('Get VPulse successfull',0) # le 0 est un temps en seconde 
            self.binary_input_VpulseSwitch1 = returned_value[0]
            self.binary_input_VpulseSwitch2 = returned_value[1]
            self.binary_input_VpulseSwitch3 = returned_value[2]
            self.binary_input_VpulseSwitch4 = returned_value[3]
            self.binary_input_VpulseSwitch5 = returned_value[4]
            self.binary_input_VpulseSwitch6 = returned_value[5]
            self.binary_input_VpulseSwitch7 = returned_value[6]
            self.ui.ListWidget_ByteState_Vpulse.clear()
            self.ui.ListWidget_ByteState_Vpulse.setStyleSheet('color : green')
            VpulseString = '{:06b} {:08b} {:08b} {:08b} {:08b} {:08b} {:08b}'.format( returned_value[6] , returned_value[5], returned_value[4] , returned_value[3] , returned_value[2] , returned_value[1] , returned_value[0] )
            self.ui.ListWidget_ByteState_Vpulse.addItem(VpulseString[::-1])
            self.Flag_Set_VpulseSw = 1


    def CarDacActivateStepByStep(self):
        """
            Carac dac tab
                Callback for the step by step Caracterisation checkbox
        """
        if self.ui.ChBCarDacStepByStep.isChecked():
            self.ui.ChBCarDacNextStep.setEnabled(True)
            self.logger.info("Step by step caracterisation enabled")
        else:
            self.ui.ChBCarDacNextStep.setEnabled(False)
            self.logger.info("Step by step caracterisation disabled")

    
    def ADPSetParams(self):
        """
            Carac dac tab
                Callback for the Set params button for the Analog Discovery
        """
        if platform.release() != 'XP':
            AD2.FSetPar(self.ui.SBCarDacADPRes1.value(),
                        self.ui.SBCarDacADPRes2.value(),
                        self.ui.SBCarDacADPNbPtsEch.value(),
                        self.ui.SBCarDacADPFreqEch.value(),
                        self.ui.DSBCarDacADPRange.value())
 

    def RunCaracterisation(self):
        """
            Carac dac tab
                Callback for the Run Caracterisation button
        """
        if platform.release() != 'XP':

            # starting values for the local variables
            LstRgdSamples = []
            self.LstRegValDac = []
            VRegValDac = self.ui.CoBCarDacDacSel.currentIndex()

            # set all default values for the DAC registers
            Dac0 = int(self.ui.LECarDacDefValDac0.text(),10)
            Dac1 = int(self.ui.LECarDacDefValDac1.text(),10)
            Dac2 = int(self.ui.LECarDacDefValDac2.text(),10)
            Dac3 = int(self.ui.LECarDacDefValDac3.text(),10)
            Dac4 = int(self.ui.LECarDacDefValDac4.text(),10)

            LstValDac = [Dac0,Dac0,Dac2,Dac3,Dac4]

            VErr = PicmicHLF.FSetDacRegs([Dac0,Dac1,Dac2,Dac3,Dac4])

            #Init the Analog discovery board
            hdwf, ChannelA, ChannelB = AD2.FInit(self.ui.CobCarDacChannelASel.currentIndex()+1,self.ui.CobCarDacChannelBSel.currentIndex()+1)
            Start = self.ui.SBCarDacStartingValue.value()
            Stop = self.ui.SBCarDacEndingValue.value()
            Step = self.ui.SBCarDacStepValue.value()
            
            WaitingTime = float(self.ui.LECarDacWaitingTime.text())
            #disable the plot type selection
            self.ui.CoBCarDacPlotTypeSel.setEnabled(False)
            if self.ui.ChBCarDacStepByStep.isChecked() == False:
                # Automatic caracterisation
                if VRegValDac in [0,4] :
                    # positive ground polarized value using one channel
                    for VRegVal in range(Start, Stop + 1 , Step):
                        #VRegVal = int ( str(VRegValStr+2), 10)
                        self.ui.LECarDacRunStatus.setText("step:{:d} out of {}".format(VRegVal//Step,((Stop-Start)//Step)))
                        QtGui.QGuiApplication.processEvents() # update the GUI
                        LstValDac[VRegValDac] = VRegVal
                        #VErr = PM0SC.FCmdSetWrReg ( PM0SC.TRegId.DAC_VAL.value, VGRegOp, VGPrePostOp, VGPrePostParam, LstValDac )
                        VErr = PicmicHLF.FSetDacRegs(LstValDac)
                        time.sleep(WaitingTime)
                        #VStatus = "Reg op = {:s} - Write error = {:d}".format (VGStrRegOp[VGRegOp], VErr)
                        rgdSamples = AD2.FAcquisition(hdwf, ChannelA,VRegVal//Step,((Stop-Start)//Step))
                        LstRgdSamples.append(rgdSamples)
                        self.LstRegValDac.append(VRegVal)
                else:
                    # negative VDD polarized value using two channels
                    for VRegVal in range(Start, Stop + 1 , Step):
                        #VRegVal = int ( str(VRegValStr+2), 10)
                        self.ui.LECarDacRunStatus.setText("step:{:d} out of {}".format(VRegVal//Step,((Stop-Start)//Step)))
                        QtGui.QGuiApplication.processEvents() # update the GUI
                        LstValDac[VRegValDac] = VRegVal
                        #VErr = PM0SC.FCmdSetWrReg ( PM0SC.TRegId.DAC_VAL.value, VGRegOp, VGPrePostOp, VGPrePostParam, LstValDac )
                        VErr = PicmicHLF.FSetDacRegs(LstValDac)
                        time.sleep(WaitingTime)
                        #VStatus = "Reg op = {:s} - Write error = {:d}".format (VGStrRegOp[VGRegOp], VErr)
                        rgdSamples = AD2.FDualAcquisition(hdwf, ChannelA,ChannelB,VRegVal//Step,((Stop-Start)//Step))
                        LstRgdSamples.append(rgdSamples)
                        self.LstRegValDac.append(VRegVal)
            else:
                #Step by step caracterisation
                if VRegValDac in [0,4] :
                    # positive ground polarized value using one channel
                    for VRegVal in range(Start, Stop + 1 , Step):
                        #VRegVal = int ( str(VRegValStr+2), 10)
                        self.ui.LECarDacRunStatus.setText("step:{:d} out of {}".format(VRegVal//Step,((Stop-Start)//Step)))
                        QtGui.QGuiApplication.processEvents() # update the GUI
                        LstValDac[VRegValDac] = VRegVal
                        #VErr = PM0SC.FCmdSetWrReg ( PM0SC.TRegId.DAC_VAL.value, VGRegOp, VGPrePostOp, VGPrePostParam, LstValDac )
                        VErr = PicmicHLF.FSetDacRegs(LstValDac)
                        time.sleep(WaitingTime)
                        #VStatus = "Reg op = {:s} - Write error = {:d}".format (VGStrRegOp[VGRegOp], VErr)
                        rgdSamples = AD2.FAcquisition(hdwf, ChannelA)
                        LstRgdSamples.append(rgdSamples)
                        self.LstRegValDac.append(VRegVal)
                        while self.ui.ChBCarDacNextStep.isChecked() == False:
                            QtGui.QGuiApplication.processEvents() # update the GUI
                        self.ui.ChBCarDacNextStep.setChecked(False)
                else:
                    # negative VDD polarized value using two channels
                    for VRegVal in range(Start, Stop + 1 , Step):
                        #VRegVal = int ( str(VRegValStr+2), 10)
                        self.ui.LECarDacRunStatus.setText("step:{:d} out of {}".format(VRegVal//Step,((Stop-Start)//Step)))
                        QtGui.QGuiApplication.processEvents() # update the GUI

                        LstValDac[VRegValDac] = VRegVal
                        #VErr = PM0SC.FCmdSetWrReg ( PM0SC.TRegId.DAC_VAL.value, VGRegOp, VGPrePostOp, VGPrePostParam, LstValDac )
                        VErr = PicmicHLF.FSetDacRegs(LstValDac)
                        time.sleep(WaitingTime)
                        #VStatus = "Reg op = {:s} - Write error = {:d}".format (VGStrRegOp[VGRegOp], VErr)
                        rgdSamples = AD2.FDualAcquisition(hdwf, ChannelA,ChannelB)
                        LstRgdSamples.append(rgdSamples)
                        self.LstRegValDac.append(VRegVal)
                        while self.ui.ChBCarDacNextStep.isChecked() == False:
                            QtGui.QGuiApplication.processEvents() # update the GUI
                        self.ui.ChBCarDacNextStep.setChecked(False)
                
            AD2.FCloseDevice()
            self.ui.LECarDacRunStatus.setText("Acquisition ended. Postprocessing")
            QtGui.QGuiApplication.processEvents() # update the GUI
            # Post processing and data saving
            self.lstDC,self.lstRMS = AD2.FSeparation(LstRgdSamples, self.LstRegValDac, VRegValDac,int(self.ui.ChBCaracDacSaveAllFiles.isChecked())) 
            # set back the default values
            Dac0 = int(self.ui.LECarDacDefValDac0.text(),10)
            Dac1 = int(self.ui.LECarDacDefValDac1.text(),10)
            Dac2 = int(self.ui.LECarDacDefValDac2.text(),10)
            Dac3 = int(self.ui.LECarDacDefValDac3.text(),10)
            Dac4 = int(self.ui.LECarDacDefValDac4.text(),10)
            VErr = PicmicHLF.FSetDacRegs([Dac0,Dac1,Dac2,Dac3,Dac4])
            # Result Plotting
            self.CarDacChangePottingType()
            self.ui.LECarDacRunStatus.setText("Caracterisation ended")
            QtGui.QGuiApplication.processEvents() # update the GUI
            # enable the plot type selection
            self.ui.CoBCarDacPlotTypeSel.setEnabled(True)
        else:
            self.logger.error("DAc caracterisation is not operationnal under win XP")


    def CarDacChangePottingType(self):
        """
            Carac dac tab
                Plot the measures from the last DAC caracterisation done
        
        """

        if platform.release() != 'XP':
            # System is not XP
            if self.ui.CoBCarDacDacSel.currentIndex() in [0,1,2,3] :
                # Dac in current
                # Result Plotting
                if self.ui.CoBCarDacPlotTypeSel.currentIndex() == 0:
                    # set the axes legends
                    self.plotCarDac.cla()
                    self.plotCarDac.set_xlim(0, max(self.LstRegValDac))
                    MinDC = min(self.lstDC)
                    MaxDC = max(self.lstDC)
                    self.plotCarDac.set_ylim(MinDC, MaxDC)
                    self.plotCarDac.grid()
                    self.plotCarDac.set_xlabel("Code(uDAC)")
                    self.plotCarDac.set_ylabel("Current DC ( mA)")
                    # Plot the data
                    self.plotCarDac.plot(self.LstRegValDac,self.lstDC)
                    self.canvasCarDac.draw()
                else:
                    #set the axes legends
                    self.plotCarDac.cla()
                    self.plotCarDac.set_xlabel("Code(DAC)")
                    self.plotCarDac.set_ylabel("Current RMS (mA)")
                    self.plotCarDac.set_xlim(0, max(self.LstRegValDac))
                    MinRMS = min(self.lstRMS)
                    MaxRMS = max(self.lstRMS)
                    self.plotCarDac.set_ylim(MinRMS, MaxRMS)
                    self.plotCarDac.grid()
                    #Plot the noise RMS
                    self.plotCarDac.plot(self.LstRegValDac,self.lstRMS)
                    self.canvasCarDac.draw()
            else:
                # Dac in tension
                # Result Plotting
                if self.ui.CoBCarDacPlotTypeSel.currentIndex() == 0:
                    # set the axes legends
                    self.plotCarDac.cla()
                    self.plotCarDac.set_xlabel("Code(DAC)")
                    self.plotCarDac.set_ylabel("Tension DC (V)")
                    self.plotCarDac.set_xlim(0, max(self.LstRegValDac))
                    MinDC = min(self.lstDC)
                    MaxDC = max(self.lstDC)
                    self.plotCarDac.set_ylim(MinDC, MaxDC)
                    self.plotCarDac.grid()
                    # Plot the data
                    self.plotCarDac.plot(self.LstRegValDac,self.lstDC)
                    self.canvasCarDac.draw()
                else:
                    #set the axes legends
                    self.plotCarDac.cla()
                    self.plotCarDac.xlabel("Code(DAC)")
                    self.plotCarDac.set_ylabel("Tension RMS (V)")
                    self.plotCarDac.set_xlim(0, max(self.LstRegValDac))
                    MinRMS = min(self.lstRMS)
                    MaxRMS = max(self.lstRMS)
                    self.plotCarDac.set_ylim(MinRMS, MaxRMS)
                    self.plotCarDac.grid()
                    #Plot the noise RMS
                    self.plotCarDac.plot(self.LstRegValDac,self.lstRMS)
                    self.canvasCarDac.draw()
        else:
            # system is XP
            self.logger.error("DAc caracterisation is not operationnal under win XP")

    def BtCarDisRunCaracClicked(self):
        """
            Carac Discri tab
                run a discri caracterisation
                saves the caracterisation in two files :
                   - one with _DC suffix : the floating values use a comma as separator
                   - one with _DD suffix : the floating values use a dot as separator
        
        """
        VStartValue = self.ui.SBCarDisStartingValue.value()
        VEndValue = self.ui.SBCarDisEndingValue.value()
        VStepValue = self.ui.SBCarDisStepValue.value()
        VFilePath = self.ui.leCarDisSavePath.text()
        
        VRunNb = self.ui.sBCarDisTestNo.value()
        VFrameLength = self.ui.SBCarDisRPFrameLength.value()
        VFileName = self.ui.LECarDisSPFileName.text()+'_'+str(VRunNb)+'step'


        VCurrStep = 0
        totalPixelList = []
        
        # set the dac registers with the starting values
        VDacRegIndex = self.ui.CoBCarDisDacSel.currentIndex()

        # set all default values for the DAC registers
        Dac0 = int(self.ui.LECarDisStValDac0.text(),10)
        Dac1 = int(self.ui.LECarDisStValDac1.text(),10)
        Dac2 = int(self.ui.LECarDisStValDac2.text(),10)
        Dac3 = int(self.ui.LECarDisStValDac3.text(),10)
        Dac4 = int(self.ui.LECarDisStValDac4.text(),10)

        LstValDac = [Dac0,Dac1,Dac2,Dac3,Dac4]

        VErr = PicmicHLF.FSetDacRegs(LstValDac)
        # create the configuration file for the results
        ConfFileName = VFilePath +'/'+ VFileName+str(VRunNb)+'.conf'
        ConfFile = open (ConfFileName,'w')
        ConfFile.writelines('[Pulsing]\n')
        ConfFile.writelines('PulsingPath = '+self.ui.leCarDisPulsingPath.text()+'\n')
        ConfFile.writelines('PulsingName = '+self.ui.leCarDisPulsingFileName.text()+'\n')
        ConfFile.writelines('PulsedReg = 0x' + str(self.ui.LEPulsingPPRegValue.text())+'\n')
        ConfFile.writelines('NoPulsedReg = 0x' + str(self.ui.LEPulsingNOTPRegValue.text())+'\n')
        ConfFile.writelines('\n[Registers]\n')
        ConfFile.writelines('VRefP = '+self.ui.LECarDisStValDac0.text()+'\n')
        ConfFile.writelines('VRefN = '+self.ui.LECarDisStValDac1.text()+'\n')
        ConfFile.writelines('VBN = '+self.ui.LECarDisStValDac2.text()+'\n')
        ConfFile.writelines('VBN_adj = '+self.ui.LECarDisStValDac3.text()+'\n')
        ConfFile.writelines('VBP = ' +self.ui.LECarDisStValDac4.text()+'\n')  
        ConfFile.writelines('RegIndex = ' + str(self.ui.CoBCarDisDacSel.currentIndex())+'\n')
        ConfFile.writelines('StartVal = ' + str(self.ui.SBCarDisStartingValue.value())+'\n')
        ConfFile.writelines('StopVal = ' + str(self.ui.SBCarDisEndingValue.value())+'\n')
        ConfFile.writelines('StepVal = ' + str(self.ui.SBCarDisStepValue.value())+'\n')
        ConfFile.close()
        
        #loop for the caracterisation 
        for VCurrentDacValue in range (VStartValue,VEndValue+1,VStepValue):
            #set dac value
            LstValDac[VDacRegIndex] = VCurrentDacValue
            VErr = PicmicHLF.FSetDacRegs(LstValDac)
            self.ui.LECarDisRunStatus.setText("step:{:d} out of {}".format(VCurrStep,((VEndValue-VStartValue)//VStepValue)))
            QApplication.processEvents() # update the GUI
            
            #start caracterisation
            VResult,VPixelList = PM0_DF.SCurveTakeOneStep(VFilePath,VCurrStep,VFileName,VFrameLength)
            if VResult < 0:
                self.logger.error('Error in caracterisation step {}'.format(VCurrStep))
            # append the pixel list to the total pixel list
            if len(VPixelList) > 0:
                for VIndex in range (len(VPixelList)):
                    if VPixelList[VIndex] not in totalPixelList:
                        totalPixelList.append(VPixelList[VIndex])
            VCurrStep +=1

        #Generate the global result file
        ResultArray = np.zeros(shape =(len(totalPixelList),VCurrStep),dtype=float)
        ResultFileNameDC = VFilePath +'/'+ self.ui.LECarDisSPFileName.text()+str(VRunNb)+'_DC.txt'
        ResultFileNameDD = VFilePath +'/'+ self.ui.LECarDisSPFileName.text()+str(VRunNb)+'_DD.txt'
        ResultFileDC = open (ResultFileNameDC,'w')
        ResultFileDD = open (ResultFileNameDD,'w')
        # list of pixels:
        rowLine = "R"
        colLine = "C"
        if len(totalPixelList) > 0:
            for VIndex in range (len(totalPixelList)):
                Row = totalPixelList[VIndex][0]
                Col = totalPixelList[VIndex][1]
                rowLine += ";" + str(Row)
                colLine += ";" + str(Col) 
        rowLine += ';\n'
        colLine += ';\n'
        ResultFileDD.writelines(rowLine)
        ResultFileDD.writelines(colLine)
        ResultFileDC.writelines(rowLine)
        ResultFileDC.writelines(colLine)
        VCurrentIndex = 0
        # generate array from the saving files
        for VCurrentDacValue in range (VStartValue,VEndValue+1,VStepValue):
            #open save text file
            currentFileName = VFilePath +'/'+ VFileName+str(VCurrentIndex)+'Norm.txt'
            try:
                currentFile = open(currentFileName,'r')
            except :
                self.logger.error('Error opening file :{}'.format(currentFileName))
            lines = currentFile.readlines()
            for line in lines:
                Data = line.split(';')
                Row=int(Data[0])
                Col =int(Data[1])
                PixData=float(Data[2])
                HitIndex = totalPixelList.index([Row,Col])
                ResultArray[HitIndex,VCurrentIndex] = PixData
            VCurrentIndex += 1
        # write array into file
        for VLineIndex in range (VCurrentIndex):
            LineToSaveDD = str(VStartValue + (VStepValue * VLineIndex))
            for VColIndex in range (len(totalPixelList)):
                LineToSaveDD += ';'+str(ResultArray[VColIndex,VLineIndex])
            LineToSaveDD += ';\n'  
            LineToSaveDC = LineToSaveDD.replace('.',',') 
            ResultFileDD.writelines(LineToSaveDD)
            ResultFileDC.writelines(LineToSaveDC)
        ResultFileDC.close()
        ResultFileDD.close()
        self.ui.LECarDisRunStatus.setText('Discri caracterisation ended')


    def CarDisInitAcq(self):
        """
            Carac Discri tab
                Initialise the Acquisition
        
        """
        self.ui.GBCarDisRunParams.setEnabled(True)
        VErr = PM0_DF.Init_DLL()
        VStatus = "Init DLL done - Result = {:d}".format (VErr)
        if (VErr >= 0):
            self.logger.info(VStatus)
        else:
            self.logger.error(VStatus)

    def CarDisPathSelect(self):
        """
            Carac Discri tab
                Select the directory where the discri caracterisation files will be saved
        
        """
        FolderPath = QFileDialog.getExistingDirectory(self,'Discri caracterisation Saving directory',os.getcwd())
        self.ui.leCarDisSavePath.setText(FolderPath)
        
        
    def closeEvent(self, event):
        """
            Catch an event ( the closing of the GUI )
            call the end function to properly ending the software ( closing com with the arduino due board, ... )
        """
        self.ui.BtEndSoftware.click()
        #if can_exit:
        #    event.accept() # let the window close
        #else:
        #    event.ignore()

    
    def __del__ (self):
        """
            Destructor of the class
        """
        #self.logger.critical('Destructor called')
        #PicmicHLF.FDisconnectFromDueBoard()
        #logging.shutdown()
        print('Destructor called')

    

if __name__ == "__main__":      # execute only if run as a script
    ## Application
    app = QApplication([])
    ## GUI
    application = Picmic_SC_GUI_Class ()
    application.show()
    sys.exit(app.exec_())
