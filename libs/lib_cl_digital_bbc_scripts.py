#!/usr/bin/env python3
# -*- coding: utf-8 -*- 
""" @package lib_cl_digital_bbc_scripts.py
  \brief     Generowanie skryptów kalibracyjnych na nowego fs.  
  \author    Rafał Sarniak
"""  
import os
from datetime import date
from lib_cl_analog_bbc_scripts import cl_AnalogScript

class cl_DigitalScript(cl_AnalogScript):
    #    
    def makeHeader(self):
        self.plik.write('ifa=1,agc,1,40000\n')
        self.plik.write('ifb=1,agc,1,40000\n')
        self.plik.write('bbc_gain=all,agc\n')
        self.plik.write('!+10s\n')
        for i in range(1,9):
            self.plik.write("bbc%02d=%.2f,a,%.1f,1\n" % (i, 750, self.bw ) )
        for i in range(9,17):
            self.plik.write("bbc%02d=%.2f,b,%.1f,1\n" % (i, 750, self.bw ) )
        self.plik.write("onsource\n")
        #
        if    self.rec == "K band":
            lo_SC = int(self.window.comboBox_CL_LO_SC.currentText())
            lo_SL = int(self.window.comboBox_CL_LO_SL.currentText())
            lo    = lo_SC + lo_SL
            self.plik.write("antenna=setlo,%.3f\n" % lo    )
            self.plik.write("antenna=setsc,%.3f\n" % lo_SC )
            self.plik.write("antenna=setsl,%.3f\n" % lo_SL )
            self.plik.write("!+1s\n")
            self.plik.write("lo=lob,%d,usb,lcp,1.00\n" % lo )
            self.plik.write("lo=loa,%d,usb,rcp,1.00\n" % lo )
        elif  self.rec == "X band":
            lo = int(self.window.comboBox_CL_LO_SX.currentText())
            self.plik.write("antenna=setlo,%.3f\n" % lo )
            self.plik.write("antenna=setsx,%.1f\n" % lo )
            self.plik.write("!+1s\n")
            self.plik.write("lo=lob,%d,usb,lcp,1.00\n" % lo )
            self.plik.write("lo=loa,%d,usb,rcp,1.00\n" % lo )
        elif  self.rec == "M band":
            lo = int(self.window.comboBox_CL_LO_SC.currentText())
            self.plik.write("antenna=setlo,%.3f\n" % lo    )
            self.plik.write("antenna=setsc,%.3f\n" % lo    )
            self.plik.write("!+1s\n")
            self.plik.write("lo=lob,%d,usb,lcp,1.00\n" % lo )
            self.plik.write("lo=loa,%d,usb,rcp,1.00\n" % lo )
        elif  self.rec == "C band":
            lo = int(self.window.comboBox_CL_LO_SC.currentText())
            self.plik.write("antenna=setlo,%.3f\n" % lo    )
            self.plik.write("antenna=setsc,%.3f\n" % lo    )
            self.plik.write("!+1s\n")
            self.plik.write("lo=lob,%d,usb,lcp,1.00\n" % lo )
            self.plik.write("lo=loa,%d,usb,rcp,1.00\n" % lo )
        elif  self.rec == "L band":
            lo = int(self.window.comboBox_CL_LO_SC.currentText())
            self.plik.write("antenna=setlo,%.3f\n" % lo    )
            self.plik.write("antenna=setsc,%.3f\n" % lo    )
            self.plik.write("!+1s\n")
            self.plik.write("lo=lob,%d,lsb,lcp,1.00\n" % lo )
            self.plik.write("lo=loa,%d,lsb,rcp,1.00\n" % lo )
        else:
            print("Wrong receiver!")
        self.plik.write('tpicd=stop\n')
        self.plik.write('mk5c_mode=ext,0xffffffff,,32\n')
        self.plik.write('mk5c_mode\n')
        self.plik.write('form=astro\n')
        self.plik.write('bread\n')
        #
        cont_cal = self.window.comboBox_CL_ContCal.currentText()
        self.plik.write('cont_cal=%s\n' % cont_cal)
        #
        self.plik.write('bbc_gain=all,agc\n')
        self.plik.write('tpicd=yes,800\n')
        self.plik.write('" caltsys\n')
        self.plik.write('" Poczekaj na najazd na zrodlo i cont\n')
        self.plik.write('halt\n')        
    
    def pojedynczy_pomiar(self, shift = 0):
        self.plik.write('"\n')
        for i in range(1,9):
            self.plik.write("bbc%02d=%.2f,a,%.1f,1\n" % (i, self.start + self.dfbbc*(i-1) + shift, self.bw ) )
        for i in range(9,17):
            self.plik.write("bbc%02d=%.2f,b,%.1f,1\n" % (i, self.start + self.dfbbc*(i-9) + shift, self.bw ) )
        self.plik.write('onoff\n')
        self.plik.write('!+1m\n')
        self.plik.write('azeloff=0d,0d\n')
        self.plik.write('!+10s\n')
    
    def makeBody(self):
        for i in range(self.num_iter):
            self.plik.write('"Start run %d/%d\n' % (i+1, self.num_iter) )
            self.plik.write('azeloff=0d,0d\n')
            self.plik.write('onsource\n')
            self.plik.write('onoff=1,5,75,3,,180,ia,ib,1u,1l,2u,2l,3u,3l,4u,4l,5u,5l,6u,6l,7u,7l,8u,8l,9u,9l,au,al,bu,bl,cu,cl,du,dl,eu,el,fu,fl,gu,gl\n')
            self.plik.write('!+1s\n')
            self.plik.write('onoff\n')
            self.plik.write('!+1m\n')
            self.plik.write('azeloff=0d,0d\n')
            self.plik.write('!+10s\n')
            self.plik.write('"\n')
            self.plik.write('onsource\n')
            for j in range( self.num_meas ):
                self.pojedynczy_pomiar( shift = j * self.bw )
