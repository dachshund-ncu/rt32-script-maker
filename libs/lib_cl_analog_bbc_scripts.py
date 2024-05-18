#!/usr/bin/env python3
# -*- coding: utf-8 -*- 
""" @package lib_cl_analog_bbc_scripts.py
  \brief     Generowanie skryptów kalibracyjnych na starego fs.  
  \author    Rafał Sarniak
"""  
import os
from datetime import date

class cl_AnalogScript:
    def __init__(self, window):
        self.window = window
        #
        self.script_name  = self.window.lineEdit_CL_ScriptName.text()
        self.head_text    = self.window.textEdit_CL_message.toPlainText()
        self.head_comment = self.window.lineEdit_CL_message.text()
        #
        self.source   = self.window.catalog_continuum[self.window.comboBox_CL_ContSource.currentIndex()]
        self.rec      = self.window.comboBox_CL_Receiver.currentText()
        self.dfbbc    = int( self.window.comboBox_CL_DFBBC.currentText() )
        self.df       = self.window.comboBox_CL_df.currentText()
        self.bw       = int( self.window.comboBox_CL_bw.currentText() )
        self.start    = self.window.spinBox_CL_BBC_Start.value()
        self.end      = self.window.spinBox_CL_BBC_End.value()
        self.num_meas = int(((self.end-self.dfbbc*7)-self.start) / self.bw )
        self.num_iter = self.window.spinBox_CL_NumIter.value() 
        #
        self.initialAction()
    
    def initialAction(self):
        self.datafolder = './generated_scripts/'
        if not os.path.exists(self.datafolder):
            os.makedirs(self.datafolder)   
    
    def generate(self):
        self.plik = open( self.datafolder + '/' + self.script_name + '.snp', "w" )
        self.makeBegining()
        self.makeHeader()  
        self.makeBody()  
        self.plik.write('!+10s \n')
        self.plik.write('sy=brk onoff& \n')
        self.plik.write('wakeup \n')
        self.plik.write('sched_end \n')
        self.plik.close()
        print( "File generated to: " + self.datafolder + self.script_name )
        
    def makeBegining(self):
        today = date.today()
        self.plik.write(self.head_text)
        self.plik.write('" ' + self.head_comment + '\n')
        self.plik.write('" Script generated by Script_maker.\n'        )
        self.plik.write('" Date: ' + today.strftime("%Y-%m-%d") + '\n' )
        self.plik.write('" (kain@astro.umk.pl)\n'                      )
        self.plik.write('source=' + self.source.name + ',' + self.source.ra_str() + ',' + self.source.dec_str() + ',' + "2000" + ',neutral \n')
        self.generate_commented_sources()
    
    def makeHeader(self):
        self.plik.write("bbc01=%.2f,a,%.1f,1\n" % ( 510, self.bw ) )
        self.plik.write("bbc02=%.2f,c,%.1f,1\n" % ( 750, self.bw ) )
        self.plik.write("bbc03=%.2f,a,%.1f,1\n" % ( 750, self.bw ) )
        self.plik.write("bbc04=%.2f,c,%.1f,1\n" % ( 510, self.bw ) )
        self.plik.write("bbc05=%.2f,a,%.1f,1\n" % ( 510, self.bw ) )
        self.plik.write("bbc06=%.2f,a,%.1f,1\n" % ( 750, self.bw ) )
        self.plik.write("bbc07=%.2f,a,%.1f,1\n" % ( 510, self.bw ) )
        self.plik.write("bbc08=%.2f,c,%.1f,1\n" % ( 750, self.bw ) )
        self.plik.write("antenna=setss,%.1f\n" % 750)
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
            self.plik.write("lo=loa,%d,usb,lcp,1.00\n" % lo )
            self.plik.write("lo=loc,%d,usb,rcp,1.00\n" % lo )
        elif  self.rec == "X band":
            lo = int(self.window.comboBox_CL_LO_SX.currentText())
            self.plik.write("antenna=setlo,%.3f\n" % lo )
            self.plik.write("antenna=setsx,%.1f\n" % lo )
            self.plik.write("!+1s\n")
            self.plik.write("lo=loa,%d,usb,lcp,1.00\n" % lo )
            self.plik.write("lo=loc,%d,usb,rcp,1.00\n" % lo )
        elif  self.rec == "M band":
            lo = int(self.window.comboBox_CL_LO_SC.currentText())
            self.plik.write("antenna=setlo,%.3f\n" % lo    )
            self.plik.write("antenna=setsc,%.3f\n" % lo    )
            self.plik.write("!+1s\n")
            self.plik.write("lo=loa,%d,usb,lcp,1.00\n" % lo )
            self.plik.write("lo=loc,%d,usb,rcp,1.00\n" % lo )
        elif  self.rec == "C band":
            lo = int(self.window.comboBox_CL_LO_SC.currentText())
            self.plik.write("antenna=setlo,%.3f\n" % lo    )
            self.plik.write("antenna=setsc,%.3f\n" % lo    )
            self.plik.write("!+1s\n")
            self.plik.write("lo=loa,%d,usb,lcp,1.00\n" % lo )
            self.plik.write("lo=loc,%d,usb,rcp,1.00\n" % lo )
        elif  self.rec == "L band":
            lo = int(self.window.comboBox_CL_LO_SC.currentText())
            self.plik.write("antenna=setlo,%.3f\n" % lo    )
            self.plik.write("antenna=setsc,%.3f\n" % lo    )
            self.plik.write("!+1s\n")
            self.plik.write("lo=loa,%d,lsb,lcp,1.00\n" % lo )
            self.plik.write("lo=loc,%d,lsb,rcp,1.00\n" % lo )
        else:
            print("Wrong receiver!")
        self.plik.write('!+1s \n')
        self.plik.write('antenna=rt4,cor internal \n')
        self.plik.write('!+1s \n')
        self.plik.write('antenna=rt4,roh %s \n' % self.rec.split()[0] )
        self.plik.write('!+1s \n')
        self.plik.write('"\n')
        self.plik.write('bread\n')
        self.plik.write('" Poczekaj na najazd na zrodlo i cont\n')
        self.plik.write('halt\n')
        
    
    def pojedynczy_pomiar(self, shift = 0):
        self.plik.write('"\n')
        self.plik.write("bbc01=%.2f,a,%.1f,1\n" % ( self.start + self.dfbbc + shift, self.bw ) )
        self.plik.write("bbc02=%.2f,c,%.1f,1\n" % ( self.start + self.dfbbc + shift, self.bw ) )
        self.plik.write("bbc03=%.2f,a,%.1f,1\n" % ( self.start + self.dfbbc + shift, self.bw ) )
        self.plik.write("bbc04=%.2f,c,%.1f,1\n" % ( self.start + self.dfbbc + shift, self.bw ) )
        self.plik.write("antenna=setss,%.1f\n"  % ( self.start + self.dfbbc + shift) )
        #plik.write('calrx=trm.rxg,fixed,11460.0\n')
        self.plik.write('onoff\n')
        self.plik.write('!+1m\n')
        self.plik.write('azeloff=0d,0d\n')
        self.plik.write('!+10s\n')
        
    def makeBody(self):
        for i in range(self.num_iter):
            self.plik.write('"Start run %d/%d\n' % (i+1, self.num_iter) )
            self.plik.write('azeloff=0d,0d\n')
            self.plik.write('onsource\n')
            self.plik.write('onoff=1,3,75,3,600,ia,ic,1u,1l,2u,2l,3u,3l,4u,4l,5u,5l,6u,6l,7u,7l,8u,8l\n')
            self.plik.write('!+1s\n')
            self.plik.write('onoff\n')
            self.plik.write('!+1m\n')
            self.plik.write('azeloff=0d,0d\n')
            self.plik.write('!+10s\n')
            self.plik.write('"\n')
            self.plik.write('onsource\n')
            for j in range( self.num_meas ):
                self.pojedynczy_pomiar( shift = j * self.bw )
                
    def generate_commented_sources(self):
        for i in range(len(self.window.catalog_continuum)):
            if i == self.window.comboBox_CL_ContSource.currentIndex():
                continue
            source = self.window.catalog_continuum[i]
            self.plik.write('"source=' + source.name + ',' + source.ra_str() + ',' + source.dec_str() + ',' + "2000" + ',neutral \n')
