# Module which contains PICMIC 0 slow control registers definition and tools to handle them

# ===========================================================================
# Modules import
# ===========================================================================




import sys

import logging

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

register_list = (0,1,3,7,8,9) #list of all configured registers



VERSION_DATE = "V2.0 25/02/2022" # Module version &date

# modification by MS : added logging, added the modifications made on the sc module by MS

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
  
  


    
    

#used to display the list of available registers 
def FPrintRegListBitPerBitList() :


   
    print ( "" )
    print ( "=============== Bit per bit available REG LIST =================" )
    print ( " - 0 = GLB_CMD")
    print ( " - 1 = Pixel Sequence")
    print ( " - 3 = Test Structure Control" )
    print ( " - 7 = PIX_CONF_ROW" )
    print ( " - 8 = CONF_COL" )
    print ( " - 9 = CONF_DATA" )
    print ( "================================================================" )
    print ( "" )
    
    
    
    
    
    
    



# used in source code at the beginning of b/b write, to show current state of bits and their names
def FPrintBitOfReg(VRegToPrint) :


    # LECTURE HARDWARE POUR ETRE SUR

    #===========================================   GLB_CMD REGISTER PRINTING ==================================================== 

    if (VRegToPrint == PM0RT.TRegId.GLB_CMD.value) :
        print ( "" )
        print ( "=============== Bits list & current values of register Global Command : =================" )
        print ( " Whole register        : {:x}(h)".format (PM0RT.VRegGlbCmd.aw8[0]))
        print ( " bit 0 = EnExtPulse    : {:b}".format (PM0RT.VRegGlbCmd.b.EnExtPulse))
        print ( " bit 1 = ExtPulse      : {:b}".format (PM0RT.VRegGlbCmd.b.ExtPulse) )
        print ( " bit 2 = RstFrCnt      : {:b}".format (PM0RT.VRegGlbCmd.b.RstFrCnt) )
        print ( " bit 3 = StartSeq      : {:b}".format (PM0RT.VRegGlbCmd.b.StartSeq) )
        print ( " bit 4 - 7             : Non-Used" )
        print ( "=========================================================================================" )
        print ( "" )
        print ( "" )
        
        
        
        
         #===========================================   PIX_SEQ REGISTER PRINTING ================================================ 
    if (VRegToPrint == PM0RT.TRegId.PIX_SEQ.value) :
        print ( "" )
        print ( "=============== Bits list & current values of register Pixel Sequence : =================" )

 
        index = 0
        
        for x in PM0RT.PixSeqNameList:
            
            print ("Byte {:>2} = {:>12}  : {:x}(h)\n".format (index,x,PM0RT.VRegPixSeq.aw8[index])) # affiche + formate toute les donnees de pix_seq
          # print(index)
            index += 1
            
 
        print ( "=========================================================================================" )
        print ( "" )
        print ( "" )    
        
        
        
        
        
    
    #===========================================   TEST_S_CTRL REGISTER PRINTING ================================================ 

    if (VRegToPrint == PM0RT.TRegId.TEST_S_CTRL.value) :
        print ( "" )
        print ( "=============== Bits list & current values of register Test Structure Ctrl : =================" )
        print ( " Whole register         : {:x}(h)".format (PM0RT.VRegTestSCtrl.aw8[0]))
        print ( " bit 0 = SW0            : {:b}".format (PM0RT.VRegTestSCtrl.b.SW0))
        print ( " bit 1 = SW1            : {:b}".format (PM0RT.VRegTestSCtrl.b.SW1) )
        print ( " bit 2 = EN_CM          : {:b}".format (PM0RT.VRegTestSCtrl.b.EN_CM) )
        print ( " bit 3 = EN_CC          : {:b}".format (PM0RT.VRegTestSCtrl.b.EN_CC) )
        print ( " bit 4 = ENA_CM1        : {:b}".format (PM0RT.VRegTestSCtrl.b.ENA_CM1) )
        print ( " bit 5 = ENA_D2P        : {:b}".format (PM0RT.VRegTestSCtrl.b.ENA_D2P) )
        print ( " bit 6 = ENA_D1P        : {:b}".format (PM0RT.VRegTestSCtrl.b.ENA_D1P) )
        print ( " bit 7 = UnUsed         : {:b}".format (PM0RT.VRegTestSCtrl.b.UnUsed) )
        print ( "============================================================================" )
        print ( "" )
        print ( "" )
        
        
        
        #===========================================   CONFIG ROW REGISTER PRINTING ================================================ 

    if (VRegToPrint == PM0RT.TRegId.PIX_CONF_ROW.value) :
        print ( "" )
        print ( "=============== Bits list & current values of register Config ROW : =================" )
        print ( " Whole register                : {:x}(h)".format (PM0RT.VRegCfgRow.aw8[0]))
        print ( " SelRow(type 0,max=128)        : {:x}(h)".format (PM0RT.VRegCfgRow.b.SelRow))
        print ( " SelAllRow(type 7)             : {:b}".format (PM0RT.VRegCfgRow.b.SelAllRow) )
        print ( "=============================================================================" )
        print ( "" )
        print ( "" )
        
        
        
        
        
            #===========================================   CONFIG COL REGISTER PRINTING ================================================ 

    if (VRegToPrint == PM0RT.TRegId.CONF_COL.value) :
        print ( "" )
        print ( "=============== Bits list & current values of register Config COL : =================" )
        print ( " Whole register                : {:x}(h)".format (PM0RT.VRegCfgCol.aw8[0]))
        print ( " SelCol(bit type 0,max=64)     : {:x}(h)".format (PM0RT.VRegCfgCol.b.SelCol))
        print ( " SelDeselAllCol(type 6,max=4)  : {:x}(h)".format (PM0RT.VRegCfgCol.b.SelDeselAllCol) )
        print ( "============================================================================" )
        print ( "" )
        print ( "" )
        
        
        
        
        
        
        
                    #===========================================   CONFIG DATA REGISTER PRINTING ================================================ 

    if (VRegToPrint == PM0RT.TRegId.CONF_DATA.value) :
        print ( "" )
        print ( "=============== Bits list & current values of register Config DATA : =================" )
        print ( " Whole register            : {:x}(h)".format (PM0RT.VRegCfgData.aw8[0]))
        print ( " I_Adj(type 0,max=8)       : {:x}(h)".format (PM0RT.VRegCfgData.b.I_Adj))
        print ( " Bit 3 : ENA_CM            : {:b}".format (PM0RT.VRegCfgData.b.ENA_CM) )
        print ( " Bit 4 : SW0               : {:b}".format (PM0RT.VRegCfgData.b.SW0) )
        print ( " Bit 5 : SW1               : {:b}".format (PM0RT.VRegCfgData.b.SW1) )
        print ( " Bit 6 : ENA_CC            : {:b}".format (PM0RT.VRegCfgData.b.ENA_CC) )
        print ( " Bit 7 : ActivateVpulse    : {:b}".format (PM0RT.VRegCfgData.b.ActivateVpulse) )
        print ( "============================================================================" )
        print ( "" )
        print ( "" )
        
    
    
    
    
   
    


        
       
       
       
       
       
       
       
       
       
         

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    # The goal of this function is to have almost no code in the SC, just execute this fct run test and that's all

def FAskingUserValues( RegOp, PrePostOp, PrePostParam) :
        
        #===========================================  RESET VARIABLES  =================================================
        VChoosenRegName = -1
        VCheckRegIsInList = -1;
        
        
        #===========================================   PRINTING AVAILABLE REGISTERS  ===================================
         
        # display every register available 
        FPrintRegListBitPerBitList()
        
        
        #===========================================   ASKING FOR WHICH REGISTER  =======================================
        
        
        
        print("Which register do you want to write bit per bit ?   (For example : Reg Global command -> Type 0) : ")
   
 
        #===========================================   REGISTER EXISTENCE CHECK  ======================================== 
        
        
       
        
        while (VCheckRegIsInList!= 1) :
  
            VChoosenRegName = int(input ())
            
            if (VChoosenRegName in register_list) :
                VCheckRegIsInList = 1
            else :
                   print("Wrong register, try again !")
                
            
          
            
                


        #===========================================   PRINTING VALUES + BITS NAMES  ==================================== 
        
        # We display every availables bits of the choosen register.
        
        #LECTURE HARDWARE AVANT CA
        
        FPrintBitOfReg(VChoosenRegName)
        
        

        
        #===========================================   ASKING WHICH BIT AND WHICH VALUE  ================================
        
        print("Now write your bit ID and the value you want, with a space (' ') between them\n")
        print("For example, to write in bit 3 the value 1, type '3 1'\n")

        VChosenBitToWrite, VChosenValueToWrite = input("Enter your bit ID then your value : ").split()
        
        print("Writing {} at Bit no : {}".format(VChosenBitToWrite, VChosenValueToWrite))
        
        
        #===========================================   STRING TO INT CONVERSION  ========================================
        
        VChosenBitToWrite = int(VChosenBitToWrite) #String to Int conversion
        VChosenValueToWrite = int(VChosenValueToWrite)  #String to Int conversion
        
        #===========================================   BIT/BIT PM0SC FUNCTION EXEC  =====================================
        

        #  PM0SC.FBitPerBitWrite ( Reg ID, Bit to change , value 1 or 0, Operation Mode )
        VBitPerBitReturnedValue = FBitPerBitWrite(VChoosenRegName,VChosenBitToWrite,VChosenValueToWrite, RegOp, PrePostOp, PrePostParam)
        
        
        #FBitPerBitWrite returns a value we need to check in the SC so we return it this way
        return VBitPerBitReturnedValue
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        

# FieldToModify -> Pas forcément 0/1 avec l'ajout de nouveaux registres 
# FieldValue 
def FBitPerBitWrite(RegId, RegBitToModify, ValueToChange, RegOp, PrePostOp, PrePostParam,) :

    logger = logging.getLogger('pm0_fct')


#===========================================   BINARY NUMBER TEST  ==================================================== 

    VTestIfExeption = FFieldExeptionList(RegId,RegBitToModify,ValueToChange)

    if ( VTestIfExeption == 0) :# si ce n'est pas une exeption, on teste le binaire
        
        # is the entered value a bool ? 
        if ((ValueToChange != 1) and (ValueToChange != 0)) :           
            #print("Fatal error. You should enter binary number instead of : {}".format(VChosenValueToWrite))
            logger.error("Bad value = {} ".format (ValueToChange))
            return(-1) # -1 is the error number for a binary number issue and stop function
       
    # Si la fonction de test d'exception à retourne une erreur on la transmet
    elif (VTestIfExeption == -1) :
        return -1
        

    



#===========================================   TEST AND WRITE FUNCTION CALL  ===========================================

    FTestAndWrByRegId(RegId,RegBitToModify,ValueToChange, RegOp, PrePostOp, PrePostParam) 


#===========================================   PRINT AFTER WRITING  ==================================================== 
   
    # (Re)Printing values after writing
    FPrintBitOfReg(RegId) 
 
 
    return (0)        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        

# find with RegID which register is concerned, which bit and which value
def FTestAndWrByRegId(RegId,RegBitToModify,ValueToChange, RegOp, PrePostOp, PrePostParam) :

 #===========================================   GLOBAL_COMMAND REGISTER  =================================================

   
    if RegId == PM0RT.TRegId.GLB_CMD.value :  # if register = Register Global Command
    
        #We execute the function that match the right bit to this reg and write it in soft & I2C 
        FRegisterIsGlobalCommand(RegId,RegBitToModify,ValueToChange, RegOp, PrePostOp, PrePostParam)
            
            
  
 #===========================================   TEST_S_CTRL REGISTER  ====================================================    
            
            
    if RegId == PM0RT.TRegId.TEST_S_CTRL.value :  # if register = Test Scructure Control
    
        #We execute the function that match the right bit to this reg and write it in soft & I2C 
        FRegisterIsTestStructCtrl(RegId,RegBitToModify,ValueToChange, RegOp, PrePostOp, PrePostParam)
        
        
        
        
        
        
#===========================================   PIXEL SEQUENCE  ====================================================  
    if RegId == PM0RT.TRegId.PIX_SEQ.value :  # if register = Test Scructure Control
    
        #We execute the function that match the right bit to this reg and write it in soft & I2C 
        FRegisterIsPixSeq(RegId,RegBitToModify,ValueToChange, RegOp, PrePostOp, PrePostParam)
        
        
        
        
 #===========================================   CONFIG ROW  ====================================================  
    if RegId == PM0RT.TRegId.PIX_CONF_ROW.value :  # if register = Test Scructure Control
    
        #We execute the function that match the right bit to this reg and write it in soft & I2C 
        FRegisterIsConfigRow(RegId,RegBitToModify,ValueToChange, RegOp, PrePostOp, PrePostParam)
        
       


 #===========================================   CONFIG COL  ====================================================  
    if RegId == PM0RT.TRegId.CONF_COL.value :  # if register = Test Scructure Control
    
        #We execute the function that match the right bit to this reg and write it in soft & I2C 
        FRegisterIsConfigCol(RegId,RegBitToModify,ValueToChange, RegOp, PrePostOp, PrePostParam)
        
        
     #===========================================   CONFIG COL  ====================================================  
    if RegId == PM0RT.TRegId.CONF_DATA.value :  # if register = Test Scructure Control
    
        #We execute the function that match the right bit to this reg and write it in soft & I2C 
        FRegisterIsConfigData(RegId,RegBitToModify,ValueToChange, RegOp, PrePostOp, PrePostParam)
            
            
            
            
            









 #===========================================  Check if we need to modify a Field OR a particular bit =================================================
def FFieldExeptionList(RegID,RegBitToModify,ValueToChange) :
    logger = logging.getLogger('pm0_fct')

    # cas particulier du registre Config Row
    if (RegID == PM0RT.TRegId.PIX_CONF_ROW.value) :
        # premiere exeption ( 7 bits a remplir )
        if(RegBitToModify == 0) :
            if(ValueToChange >= 128) :           
                print("Fatal error. Overflow of register. Abort writing")
                logger.error("Fatal error. Overflow of register. Abort writing")
                return -1
            else :
                print ("value ok")
                return 1
                
        #if RegBitToModify isnt a particular case, we check if the value is binary 
        else :
            if ((ValueToChange != 1) and (ValueToChange != 0)) :           
                logger.error("Bad value = {} , should be [0,1]".format (ValueToChange))
                return(-1) # -1 is the error number for a binary number issue and stop function
        
          
           
            
            
            
            
    # cas particulier du registre Config Col      
    elif (RegID == PM0RT.TRegId.CONF_COL.value) :
        # premiere exeption ( 6 bits a remplir )
        if(RegBitToModify == 0) : 
            if(ValueToChange >= 64) :   
                logger.error("Fatal error. Overflow of register. Abort writing")            
                print("Fatal error. Overflow of register. Abort writing")
                return -1
            else :
                print ("value ok")
                return 1
        #if RegBitToModify isnt a particular case, we check if the value is binary 
        else :
            if ((ValueToChange != 1) and (ValueToChange != 0)) :           
                return(-1) # -1 is the error number for a binary number issue and stop function
                
                
                
                
        # deuxiemee exeption (2 bits a remplir )        
        if(RegBitToModify == 6) :
            if(ValueToChange >= 4) :           
                print("Fatal error. Overflow of register. Abort writing")
                logger.error("Fatal error. Overflow of register. Abort writing")
                return -1
            else :
                print ("value ok")
                return 1
        #if RegBitToModify isnt a particular case, we check if the value is binary 
        
        else :
            if ((ValueToChange != 1) and (ValueToChange != 0)) :       
                logger.error("Bad value = {} , should be [0,1]".format (ValueToChange))            
                return(-1) # -1 is the error number for a binary number issue and stop function
                
            
            
            
    # cas particulier du registre Config DATA      
    elif (RegID == PM0RT.TRegId.CONF_DATA.value) :
        # premiere exeption ( 3 bits a remplir )
        if(RegBitToModify == 0) :
            if(ValueToChange >= 8) :           
                print("Fatal error. Overflow of register. Abort writing")
                logger.error("Fatal error. Overflow of register. Abort writing")
                return -1
            else :
                print ("value ok")
                return 1
        #if RegBitToModify isnt a particular case, we check if the value is binary 
        else :
            if ((ValueToChange != 1) and (ValueToChange != 0)) : 
                logger.error("Bad value = {} , should be [0,1]".format (ValueToChange))            
                return(-1) # -1 is the error number for a binary number issue and stop function
      



                 # cas particulier du registre Config PIX_SEQ    -> Que des regi de 8 bits !  
    elif (RegID == PM0RT.TRegId.PIX_SEQ.value) :
        # exeption ( 8 bits a remplir )
        if(ValueToChange >= 256) :           
            print("Fatal error. Overflow of register. Abort writing")
            logger.error("Fatal error. Overflow of register. Abort writing")
            return -1
        else :
            print ("value ok")
            return 1




      
    else : 
        return 0


        
        
    
















 #===========================================   GLOBAL_COMMAND REGISTER FUNCTION =================================================
def FRegisterIsGlobalCommand(RegId,RegBitToModify,ValueToChange, RegOp, PrePostOp, PrePostParam) :
    logger = logging.getLogger('pm0_fct')
    
    # This value tell us to write on I2C bus or not (depend on Used bit or UnUsed Bit)
    VDoWrite = 1
        
        
    #depending on the value of RegBitToModify we write in the correct bit the chosen value
    if RegBitToModify == 0 :
        PM0RT.VRegGlbCmd.b.EnExtPulse = ValueToChange
        print ( "" )
        print ( "" )
    elif RegBitToModify == 1 :
        PM0RT.VRegGlbCmd.b.ExtPulse   = ValueToChange
        print ( "" )
        print ( "" )
    elif RegBitToModify == 2 :
        PM0RT.VRegGlbCmd.b.RstFrCnt   = ValueToChange
        print ( "" )
        print ( "" )
    elif RegBitToModify == 3 :
        PM0RT.VRegGlbCmd.b.StartSeq   = ValueToChange
        print ( "" )
        print ( "" )

        #Non used
    else :
                   
        print ( "" )
        print ( "You tried to write in a non-used bit the following value : ",ValueToChange)
        print ( "")
        VDoWrite = 0 # We do not want to write if bit is not used
        
        
        
        
        
    if (VDoWrite) :
        #to write on I2C, we use the FCmdSetWrReg Function(Reg ID,write mode,aw8 to write)
        PM0SC.FCmdSetWrReg (RegId,  RegOp, PrePostOp, PrePostParam, [PM0RT.VRegGlbCmd.aw8[0]] ) 
    else :
        logger.error ( "You tried to write in a non-used bit the following value : ",ValueToChange)
        return -2
            
    
    
    
    
    
    
    
    
    
    
    

    #===========================================   PIXEL SEQUENCE REGISTER FUNCTION ================================================= 
def FRegisterIsPixSeq(RegId,RegBitToModify,ValueToChange, RegOp, PrePostOp, PrePostParam) : 
    logger = logging.getLogger('pm0_fct')
   
# This value tell us to write on I2C bus or not (depend on Used bit or UnUsed Bit)
    VDoWrite = 1
        
        
    #depending on the value of RegBitToModify we write in the correct bit the chosen value
    if RegBitToModify == 0 :
        PM0RT.VRegPixSeq.f.FlushMod = ValueToChange
        print ( "" )
        print ( "" )
    elif RegBitToModify == 1 :
        PM0RT.VRegPixSeq.f.UnUsed = ValueToChange
        print ( "" )
        print ( "" )
    elif RegBitToModify == 2 :
        PM0RT.VRegPixSeq.f.MarkerMod   = ValueToChange
        print ( "" )
        print ( "" )
    elif RegBitToModify == 3 :
        PM0RT.VRegPixSeq.f.UnUsed   = ValueToChange
        print ( "" )
        print ( "" )
    elif RegBitToModify == 4 :
        PM0RT.VRegPixSeq.f.PulseMod   = ValueToChange
        print ( "" )
        print ( "" )
    elif RegBitToModify == 5 :
        PM0RT.VRegPixSeq.f.LoadWidth   = ValueToChange
        print ( "" )
        print ( "" )
    elif RegBitToModify == 6 :
        PM0RT.VRegPixSeq.f.Load_pLSB   = ValueToChange
        print ( "" )
        print ( "" )
    elif RegBitToModify == 7 :
        PM0RT.VRegPixSeq.f.Load_pMSB   = ValueToChange
        print ( "" )
        print ( "" )
    elif RegBitToModify == 8:
        PM0RT.VRegPixSeq.f.Flush_pLSB   = ValueToChange
        print ( "" )
        print ( "" )
    elif RegBitToModify == 9:
        PM0RT.VRegPixSeq.f.Flush_pMSB   = ValueToChange
        print ( "" )
        print ( "" )
    elif RegBitToModify == 10 :
        PM0RT.VRegPixSeq.f.Apulse_pLSB   = ValueToChange
        print ( "" )
        print ( "" )
    elif RegBitToModify == 11 :
        PM0RT.VRegPixSeq.f.Apulse_pMSB   = ValueToChange
        print ( "" )
        print ( "" )
    elif RegBitToModify == 12 :
        PM0RT.VRegPixSeq.f.Dpulse_pLSB   = ValueToChange
        print ( "" )
        print ( "" )
    elif RegBitToModify == 13 :
        PM0RT.VRegPixSeq.f.Dpulse_pMSB   = ValueToChange
        print ( "" )
        print ( "" )
    elif RegBitToModify == 14 :
        PM0RT.VRegPixSeq.f.RdpixMaskLSB   = ValueToChange
        print ( "" )
        print ( "" )
    elif RegBitToModify == 15 :
        PM0RT.VRegPixSeq.f.RdpixMaskMSB   = ValueToChange
        print ( "" )
        print ( "" )
    elif RegBitToModify == 16 :
        PM0RT.VRegPixSeq.f.MaxFrameLSB   = ValueToChange
        print ( "" )
        print ( "" )
    elif RegBitToModify == 17 :
        PM0RT.VRegPixSeq.f.MaxFrameMSB   = ValueToChange
        print ( "" )
        print ( "" )
    elif RegBitToModify == 18 :
        PM0RT.VRegPixSeq.f.PolarityLSB   = ValueToChange
        print ( "" )
        print ( "" )
    elif RegBitToModify == 19 :
        PM0RT.VRegPixSeq.f.PolarityMSB   = ValueToChange
        print ( "" )
        print ( "" )
    elif RegBitToModify == 20 :
        PM0RT.VRegPixSeq.f.Marker1LSB   = ValueToChange
        print ( "" )
        print ( "" )
    elif RegBitToModify == 21 :
        PM0RT.VRegPixSeq.f.Marker1MSB   = ValueToChange
        print ( "" )
        print ( "" )
    elif RegBitToModify == 22 :
        PM0RT.VRegPixSeq.f.Marker2LSB   = ValueToChange
        print ( "" )
        print ( "" )
    elif RegBitToModify == 23 :
        PM0RT.VRegPixSeq.f.Marker2MSB   = ValueToChange
        print ( "" )
        print ( "" )


        
    #UnUsed
    else :           
        print ( "" )
        print ( "You tried to write in a non-used bit the following value : ",ValueToChange)
        print ( "")    
        VDoWrite = 0
            
    #to write on I2C, we use the Function FCmdSetWrReg(Reg ID,  write mode,  aw8 to write) contained in module mod_pm0_sc_20
    if (VDoWrite) :
        PM0SC.FCmdSetWrReg (RegId,  RegOp, PrePostOp, PrePostParam, PM0RT.VRegPixSeq.aw8[0:24]) 
    else :
        print ( "You tried to write in a non-used bit the following value : ",ValueToChange)
        return -2       
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    #===========================================   TEST STRUCT CTRL REGISTER FUNCTION ================================================= 
def FRegisterIsTestStructCtrl(RegId,RegBitToModify,ValueToChange,RegOp, PrePostOp, PrePostParam) : 
    logger = logging.getLogger('pm0_fct')
   
# This value tell us to write on I2C bus or not (depend on Used bit or UnUsed Bit)
    VDoWrite = 1
        
        
    #depending on the value of RegBitToModify we write in the correct bit the chosen value
    if RegBitToModify == 0 :
        PM0RT.VRegTestSCtrl.b.SW0 = ValueToChange
        print ( "" )
        print ( "" )
    elif RegBitToModify == 1 :
        PM0RT.VRegTestSCtrl.b.SW1   = ValueToChange
        print ( "" )
        print ( "" )
    elif RegBitToModify == 2 :
        PM0RT.VRegTestSCtrl.b.EN_CM   = ValueToChange
        print ( "" )
        print ( "" )
    elif RegBitToModify == 3 :
        PM0RT.VRegTestSCtrl.b.EN_CC   = ValueToChange
        print ( "" )
        print ( "" )
    elif RegBitToModify == 4 :
        PM0RT.VRegTestSCtrl.b.ENA_CM1   = ValueToChange
        print ( "" )
        print ( "" )
    elif RegBitToModify == 5 :
        PM0RT.VRegTestSCtrl.b.ENA_D2P   = ValueToChange
        print ( "" )
        print ( "" )
    elif RegBitToModify == 6 :
        PM0RT.VRegTestSCtrl.b.ENA_D1P   = ValueToChange
        print ( "" )
        print ( "" )
        
    #UnUsed
    else :           
        print ( "" )
        print ( "You tried to write in a non-used bit the following value : ",ValueToChange)
        print ( "")    
        VDoWrite = 0
            
    #to write on I2C, we use the Function FCmdSetWrReg(Reg ID,  write mode,  aw8 to write) contained in module mod_pm0_sc_20
    if (VDoWrite) :
        PM0SC.FCmdSetWrReg (RegId, RegOp, PrePostOp, PrePostParam, [PM0RT.VRegTestSCtrl.aw8[0]] ) 
    else :
        print ( "You tried to write in a non-used bit the following value : ",ValueToChange)
        return -2   
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        

        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        



 #===========================================   CONFIG ROW REGISTER FUNCTION =================================================
def FRegisterIsConfigRow(RegId,RegBitToModify,ValueToChange,RegOp, PrePostOp, PrePostParam) : 
    logger = logging.getLogger('pm0_fct')
   
# This value tell us to write on I2C bus or not (depend on Used bit or UnUsed Bit)
    VDoWrite = 1
    
        
    #depending on the value of RegBitToModify we write in the correct bit the chosen value
    if RegBitToModify == 0 :
        PM0RT.VRegCfgRow.b.SelRow = ValueToChange # change the 6 first bits 
        print ( "" )
        print ( "" )

    elif RegBitToModify == 7 :
        PM0RT.VRegCfgRow.b.SelAllRow   = ValueToChange  #
        print ( "" )
        print ( "" )
       
            
    #to write on I2C, we use the Function FCmdSetWrReg(Reg ID,  write mode,  aw8 to write) contained in module mod_pm0_sc_20
    if (VDoWrite) :
        PM0SC.FCmdSetWrReg (RegId, RegOp, PrePostOp, PrePostParam, [PM0RT.VRegCfgRow.aw8[0]] ) 
    else :
        return -2  
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        



 #===========================================   CONFIG COL REGISTER FUNCTION =================================================
def FRegisterIsConfigCol(RegId,RegBitToModify,ValueToChange,RegOp, PrePostOp, PrePostParam) : 
    logger = logging.getLogger('pm0_fct')
   
# This value tell us to write on I2C bus or not (depend on Used bit or UnUsed Bit)
    VDoWrite = 1
        
    #print("\nWE ARE ENTERING FCT ISREGCONFCOL\n")
       
    #depending on the value of RegBitToModify we write in the correct bit the chosen value
    if RegBitToModify == 0 :
        PM0RT.VRegCfgCol.b.SelCol = ValueToChange
        print ( "" )
        print ( "" )
    elif RegBitToModify == 6 :
        PM0RT.VRegCfgCol.b.SelDeselAllCol = ValueToChange
        print ( "" )
        print ( "" )

       
            
    #to write on I2C, we use the Function FCmdSetWrReg(Reg ID,  write mode,  aw8 to write) contained in module mod_pm0_sc_20
    if (VDoWrite) :
        PM0SC.FCmdSetWrReg (RegId, RegOp, PrePostOp, PrePostParam, [PM0RT.VRegCfgCol.aw8[0]] ) 
    else :
        return -2  
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
 #===========================================   CONFIG DATA REGISTER FUNCTION =================================================
def FRegisterIsConfigData(RegId,RegBitToModify,ValueToChange,RegOp, PrePostOp, PrePostParam) : 
    logger = logging.getLogger('pm0_fct')
   
# This value tell us to write on I2C bus or not (depend on Used bit or UnUsed Bit)
    VDoWrite = 1
        
    #print("\nWE ARE ENTERING FCT ISREGCONFDATA\n")
        
    #depending on the value of RegBitToModify we write in the correct bit the chosen value
    if RegBitToModify == 0 :
        PM0RT.VRegCfgData.b.I_Adj = ValueToChange
        print ( "" )
        print ( "" )
    elif RegBitToModify == 3 :
        PM0RT.VRegCfgData.b.ENA_CM   = ValueToChange
        print ( "" )
        print ( "" )
    elif RegBitToModify == 4 :
        PM0RT.VRegCfgData.b.SW0   = ValueToChange
        print ( "" )
        print ( "" )
    elif RegBitToModify == 5 :
        PM0RT.VRegCfgData.b.SW1   = ValueToChange
        print ( "" )
        print ( "" )
    elif RegBitToModify == 6 :
        PM0RT.VRegCfgData.b.ENA_CC   = ValueToChange
        print ( "" )
        print ( "" )
    elif RegBitToModify == 7 :
        PM0RT.VRegCfgData.b.ActivateVpulse   = ValueToChange
        print ( "" )
        print ( "" )
       
            
    #to write on I2C, we use the Function FCmdSetWrReg(Reg ID,  write mode,  aw8 to write) contained in module mod_pm0_sc_20
    if (VDoWrite) :
        PM0SC.FCmdSetWrReg (RegId, RegOp, PrePostOp, PrePostParam, [PM0RT.VRegCfgData.aw8[0]] ) 
    else :
        return -2 