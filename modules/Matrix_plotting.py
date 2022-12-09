#!/usr/bin/python
# -*- coding: utf-8 -*-
"""  @Matrix_plotting.py

  Module for the plotting of matrix
  
"""

import platform # for the detection of the windows version

import logging
import numpy as np
import ctypes as ct
import matplotlib.pyplot as plt
from matplotlib.pyplot import colormaps as cm


if platform.release() != 'XP':
    from matplotlib.widgets import RadioButtons,Slider,RangeSlider,Button
else:
    from matplotlib.widgets import RadioButtons,Slider,Button


RadioSelect = 0    


def PlotMatrix(MatrixToPlot,PlotType):
    '''
    ...
    
    Plot a matrix
    
    Param
    - Matrix to plot : 3d matrix containing all frames of a run
    - PlotType = 0: plot frame / 1 : plot sum of frames
    
    Returns
    - result of the fonction : 0 : successfull / negative number : failed
    
    06/04/2022 M.SPECHT CNRS/IN2P3/IPHC/C4PI
    
    '''

    logger = logging.getLogger('mat_plot')

    #fig, PlotAx = plt.subplots()
    fig = plt.figure('Data from Picmic')
    PlotAx = plt.axes([0.05,0.15,0.95,0.75])
    VRowNb = np.size(MatrixToPlot,0)
    VColNb = np.size(MatrixToPlot,1)
    VTotalFrameNb = np.size(MatrixToPlot,2)
    logger.info("Plotting the matrix, matrix size :{:d},{:d},{:d}".format(VRowNb,VColNb,VTotalFrameNb))
   
    if (PlotType == 0):
        # PlotType : Frame
        # Plot one frame at a time
        # add the frame selectioon slider
        plt.set_cmap('Greys')
        if platform.release() != 'XP':
            SliderAx = plt.axes([0.1, 0.05, 0.03, 0.85])
            SFrameSel = Slider(SliderAx,'Frame',0,VTotalFrameNb-1,valinit=0,valstep=1,orientation="vertical")
        else:
            SliderAx = plt.axes([0.1, 0.05, 0.80, 0.02])
            SFrameSel = Slider(SliderAx,'Frame',0,VTotalFrameNb-1,valinit=0,valfmt=u'%1.0f')
        MatrixShow = PlotAx.matshow(MatrixToPlot[:,:,0])
        
        def plotOneFrame(change):
            VFrameIndex = int(SFrameSel.val)
            MatrixShow = PlotAx.matshow(MatrixToPlot[:,:,VFrameIndex])
            fig.canvas.draw()
       
        SFrameSel.on_changed(plotOneFrame)

    elif (PlotType == 1):
        #PlotType : sum
        plt.set_cmap('hot')
        # Plot the sum of several frames
        if platform.release() != 'XP':
            # system is not Win XP

            MatrixShow = PlotAx.imshow(MatrixToPlot[:,:,0])
            # add the frame sum ranged slider
            RangeSliderAx = plt.axes([0.17, 0.30, 0.03, 0.60])
            SSumFramesSel = RangeSlider(RangeSliderAx,'Sum Frames',0,VTotalFrameNb-1,valstep=1,orientation="vertical")
            
            # add the refresh plot button
            PlotButtonAx = plt.axes([0.1,0.05,0.20,0.05])
            PlotButton = Button(PlotButtonAx,'Refresh Plot')
            # add the sum/percent display radio button
            RadioButtonAx = plt.axes([0.1,0.12,0.20,0.1])
            DisplaySelRadBut = RadioButtons(RadioButtonAx,('Sum','Per cent'))
            DisplaySelRBDist = {0:'Sum',1:'Per cent'}
            CBax = plt.axes([0.85, 0.1, 0.075, 0.8])
            CBar = fig.colorbar(MatrixShow,cax=CBax)

            def plotSumOfFrame(change):
                FirstFrame = int(SSumFramesSel.val[0])
                LastFrame = int(SSumFramesSel.val[1])
                logger.info("First frame:{:d},LastFrame:{:d}".format(FirstFrame,LastFrame))
                Matrix2DSum = np.zeros((VRowNb,VColNb),dtype=int)
                #sum all the frames hits
                VSum = ct.c_int(0)
                for VRowIndex in range (VRowNb):
                    for VColIndex in range (VColNb):
                        VSum.value = 0
                        #for VFrameIndex in range(VTotalFrameNb.value):
                        for VFrameIndex in range (FirstFrame,LastFrame+1):
                            VSum.value = VSum.value + MatrixToPlot[VRowIndex,VColIndex,VFrameIndex] 
                        Matrix2DSum[VRowIndex,VColIndex] = VSum.value
                if (DisplaySelRadBut.value_selected ==  DisplaySelRBDist[0]):
                    # Display the sum array
                    VMax = np.max(Matrix2DSum)
                    VMin = np.min(Matrix2DSum)
                    logger.info("min:{:d},max:{:d}".format(VMin,VMax))

                    MatrixShow.set_data(Matrix2DSum)
                    MatrixShow.set_clim(VMin,VMax)
                elif (DisplaySelRadBut.value_selected ==  DisplaySelRBDist[1]):
                    # Display the normalized array
                    VMax = np.max(Matrix2DSum)
                    #VMin = np.min(Matrix2DSum)
                    NormMatrix2D = Matrix2DSum / VMax
                    VMax = np.max(NormMatrix2D)
                    VMin = np.min(NormMatrix2D)
                    logger.info("min:{},max:{}".format(VMin,VMax))
                    MatrixShow.set_data(NormMatrix2D)
                    MatrixShow.set_clim(VMin,VMax)

                fig.canvas.draw()

            PlotButton.on_clicked(plotSumOfFrame)

            plotSumOfFrame(1)
            
        else:
            # system is Win XP => no rangeslider
#            MatrixShow = PlotAx.imshow(MatrixToPlot[:,:,0])
            MatrixShow = PlotAx.matshow(MatrixToPlot[:,:,0])
            # add the frame sum  sliders

            FirstFrameSliderAx = plt.axes([0.3, 0.05, 0.60, 0.02])
            SFirstFramesSel = Slider(FirstFrameSliderAx,'First Frames',0,VTotalFrameNb-1,valinit=0,valfmt=u'%1.0f')
            LastFrameSliderAx = plt.axes([0.3, 0.07, 0.60, 0.02])
            SLastFramesSel = Slider(LastFrameSliderAx,'Last Frames',0,VTotalFrameNb-1,valinit=0,valfmt=u'%1.0f')
            
            
            # add the refresh plot button
            PlotButtonAx = plt.axes([0.1,0.25,0.20,0.05])
            PlotButton = Button(PlotButtonAx,'Refresh Plot')
            # add the sum/percent display radio button
            RadioButtonAx = plt.axes([0.1,0.32,0.20,0.1])
            DisplaySelRadBut = RadioButtons(RadioButtonAx,('Sum','Per cent'))
            DisplaySelRBDist = {'Sum':0,'Per cent':1}
            CBax = plt.axes([0.85, 0.15, 0.075, 0.75])
            CBar = fig.colorbar(MatrixShow,cax=CBax)
            RadioSelect = 0

            def RBfunc(label):
                global RadioSelect
                RadioSelect = DisplaySelRBDist[label]
                logger.info("label:{},Radioselect:{}".format(label,RadioSelect))
            
            DisplaySelRadBut.on_clicked(RBfunc)

            def plotSumOfFrame(change):
                global RadioSelect
                FirstFrame = int(SFirstFramesSel.val)
                LastFrame = int(SLastFramesSel.val)
                if FirstFrame > LastFrame :
                    FirstFrame , LastFrame = LastFrame , FirstFrame
                logger.info("Plotting the matrix, matrix size :{:d},{:d},{:d}".format(VRowNb,VColNb,VTotalFrameNb))
                logger.info("First frame:{:d},LastFrame:{:d},RadioSelect:{}".format(FirstFrame,LastFrame,RadioSelect))
                Matrix2DSum = np.zeros((VRowNb,VColNb),dtype=int)
                #sum all the frames hits
                VSum = ct.c_int(0)
                for VRowIndex in range (VRowNb):
                    for VColIndex in range (VColNb):
                        VSum.value = 0
                        #for VFrameIndex in range(VTotalFrameNb.value):
                        for VFrameIndex in range (FirstFrame,LastFrame+1):
                            VSum.value = VSum.value + MatrixToPlot[VRowIndex,VColIndex,VFrameIndex] 
                        Matrix2DSum[VRowIndex,VColIndex] = VSum.value
                if (RadioSelect ==  0):
                    # Display the sum array
                    VMax = np.max(Matrix2DSum)
                    VMin = np.min(Matrix2DSum)
                    logger.info("min:{:d},max:{:d}".format(VMin,VMax))

                    MatrixShow.set_data(Matrix2DSum)
                    MatrixShow.set_clim(VMin,VMax)
                elif (RadioSelect ==  1):
                    # Display the normalized array
                    VMax = np.max(Matrix2DSum)
                    #VMin = np.min(Matrix2DSum)
                    NormMatrix2D = Matrix2DSum / VMax
                    VMax = np.max(NormMatrix2D)
                    VMin = np.min(NormMatrix2D)
                    logger.info("min:{},max:{}".format(VMin,VMax))
                    MatrixShow.set_data(NormMatrix2D)
                    MatrixShow.set_clim(VMin,VMax)

                fig.canvas.draw()

            PlotButton.on_clicked(plotSumOfFrame)

            plotSumOfFrame(1)

    elif (PlotType == 2):
        #PlotType : one frame only
        # PlotType : Frame
        # Plot one frame at a time
        # add the frame selectioon slider
        plt.set_cmap('Greys')
        ##if platform.release() != 'XP':
        ##    SliderAx = plt.axes([0.1, 0.05, 0.03, 0.85])
        ##    SFrameSel = Slider(SliderAx,'Frame',0,VTotalFrameNb-1,valinit=0,valstep=1,orientation="vertical")
        ##else:
        ##    SliderAx = plt.axes([0.1, 0.05, 0.80, 0.02])
        ##    SFrameSel = Slider(SliderAx,'Frame',0,VTotalFrameNb-1,valinit=0,valfmt=u'%1.0f')
        MatrixShow = PlotAx.matshow(MatrixToPlot)
        fig.canvas.draw()
        
        ##def plotOneFrame(change):
        ##    VFrameIndex = int(SFrameSel.val)
        ##    MatrixShow = PlotAx.matshow(MatrixToPlot[:,:,VFrameIndex])
        ##    fig.canvas.draw()
       
        ##SFrameSel.on_changed(plotOneFrame)



    plt.show()
