#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
\mainpage  Słowo wstępne
  \brief     Program do tworzenia skryptów Field systemu.  
  \date      14.05.2021
  \author    Rafał Sarniak
  
  
"""
""" @package Script_maker
  \brief     Main file of Script_maker.
  
  \author    Rafał Sarniak
"""
 
import sys
import os
import time

sys.path.append('./libs/')
sys.path.append('./ui/')

from PyQt5.QtWidgets import QDialog, QApplication, QWidget, QMainWindow, QFileDialog, QMessageBox
from PyQt5.QtGui     import QPalette, QColor

from UI_MainWindow              import Ui_MainWindow
from molecules                  import *
from catalogs                   import src_reader
from lib_fs_spectr_scripts      import generateSpectralScripts
from lib_cl_analog_bbc_scripts  import cl_AnalogScript
from lib_cl_digital_bbc_scripts import cl_DigitalScript


class Script_maker(QMainWindow, Ui_MainWindow):
    ''' Main class'''
    def __init__(self):
        super(Script_maker, self).__init__()
        self.setupUi(self)
        self.system_list      = ["", "K band", "X band", "M band", "C band", "L band"]
        # Spectral part
        self.molecules        = make_molecule_list("./libs/molecules")
        self.molecule_list    = [str(x) for x in self.molecules]
        self.catalog          = []
        self.source_from_cat  = None
        self.block_textupdate = False
        self.comboBox_Receiver.addItems(self.system_list)
        self.comboBox_Molecule.addItems(self.molecule_list)
        self.comboBox_Sources.insertItem(0,"")
        self.comboBox_Molecule_palette = self.comboBox_Molecule.palette()
        self.comboBox_Molecule_palette.setColor(QPalette.Button, QColor("red"))
        self.comboBox_Molecule.setPalette(self.comboBox_Molecule_palette)
        # Signals
        self.button_LoadFile.clicked.connect(               self.BTN_LoadFile         )
        self.actionLoad_list_of_sources.triggered.connect(  self.BTN_LoadFile         )
        self.comboBox_Sources.currentIndexChanged.connect(  self.CMBO_SelectOneSource )
        self.comboBox_Molecule.currentIndexChanged.connect( self.CMBO_MoleculeSelect  )
        self.button_GenerateScripts.clicked.connect(        self.BTN_GenerateScripts  )
        self.actionAuthor.triggered.connect( self.Author )
        # CL part
        proj_name, soft_name, band_name, self.catalog_continuum = src_reader("./catalogs/PozCalSRC_Cont.txt")
        self.catalog_continuum_list = [str(x) for x in self.catalog_continuum]
        self.comboBox_CL_ContSource.addItems(self.catalog_continuum_list)
        self.comboBox_CL_Receiver.addItems(self.system_list)
        # CL Signals
        self.button_GenerateClScript.clicked.connect(             self.BTN_GenerateCLScript      )
        self.comboBox_CL_FieldSystem.currentIndexChanged.connect( self.CMBO_CL_FieldSystemSelect )
        self.comboBox_CL_Receiver.currentIndexChanged.connect(    self.CMBO_CL_Receiver          )       
        
        self.comboBox_CL_LO_SC.currentIndexChanged.connect(       self.CL_message )
        self.comboBox_CL_LO_SC.currentTextChanged.connect(        self.CL_message )
        self.comboBox_CL_LO_SL.currentIndexChanged.connect(       self.CL_message )
        self.comboBox_CL_LO_SL.currentTextChanged.connect(        self.CL_message )
        self.comboBox_CL_LO_SX.currentIndexChanged.connect(       self.CL_message )
        self.comboBox_CL_LO_SX.currentTextChanged.connect(        self.CL_message )
        
        self.comboBox_CL_DFBBC.currentIndexChanged.connect(       self.CL_message )
        self.spinBox_CL_BBC_Start.valueChanged.connect(           self.CL_message )
        self.spinBox_CL_BBC_End.valueChanged.connect(             self.CL_message )
        self.spinBox_CL_NumIter.valueChanged.connect(             self.CL_message )
        self.comboBox_CL_ContCal.currentIndexChanged.connect(     self.CL_message )
        # CL after start
        self.CMBO_CL_FieldSystemSelect()
        self.CMBO_CL_Receiver()
        
    # ------ Spectral part
    def BTN_LoadFile(self):
        path = QFileDialog.getOpenFileName(self, 'Load catalog', './catalogs/',"Text files (*.txt)")
        if len(path[0]) == 0: return
        self.lineEdit_catalog_path.setText(path[0])
        self.comboBox_Sources.setEnabled(True)
        proj_name, soft_name, band_name, self.catalog = src_reader(path[0])
        self.catalog_list = [str(x) for x in self.catalog]
        try: 
            index = self.system_list.index(band_name)
            self.comboBox_Receiver.setCurrentIndex(index)
        except ValueError:
            print("No such receiving system:", band_name)
        self.lineEdit_destination_directory.setText(proj_name)
        self.comboBox_Sources.addItems(self.catalog_list)
        self.source_from_cat = None
    
    def CMBO_SelectOneSource(self):
        """ Signal when only one source from catalog is needed. """
        self.source_from_cat = self.catalog[self.comboBox_Sources.currentIndex() - 1]
        print("One source from catalog has been selected: ", self.source_from_cat )
        self.lineEdit_source_name.setText(           self.source_from_cat.name      )
        self.lineEdit_script_name.setText(           self.source_from_cat.script    )
        self.lineEdit_RA.setText(                    self.source_from_cat.ra_str()  )
        self.lineEdit_DEC.setText(                   self.source_from_cat.dec_str() ) 
        self.doubleSpinBox_velocity.setValue(        self.source_from_cat.v_sys     )
        self.spinBox_numberofscanpairs.setValue( int(self.source_from_cat.cycles/2) )
        
    def CMBO_MoleculeSelect(self):
        molecule = self.molecules[self.comboBox_Molecule.currentIndex()]
        print("Molecule has been selected:", molecule)
        try: 
            index = self.system_list.index(molecule.rt4_sys.lstrip())
            self.comboBox_Receiver.setCurrentIndex(index) 
            self.comboBox_Molecule_palette.setColor(QPalette.Button, QColor("green"))
            self.comboBox_Molecule.setPalette(self.comboBox_Molecule_palette)
        except ValueError:
            print("No such receiving system:", molecule.rt4_sys)
        except AttributeError:
            print("Select proper molecule!")
            self.comboBox_Molecule_palette.setColor(QPalette.Button, QColor("red"))
            self.comboBox_Molecule.setPalette(self.comboBox_Molecule_palette)
            
    def BTN_GenerateScripts(self):
        if self.comboBox_Molecule.currentIndex() == 0:
            QMessageBox.critical(self, "Molecule", "Select proper molecule!")
            return
        generateSpectralScripts(self)
        
    def Author(self):
        QMessageBox.information(self, "About author", "Rafał Sarniak, kain@astro.umk.pl")
        return
    #
    # ------ CL part
    #
    def BTN_GenerateCLScript(self):
        if   self.comboBox_CL_FieldSystem.currentText() == "fs"  :
            maker = cl_AnalogScript(self)
        elif self.comboBox_CL_FieldSystem.currentText() == "fs6" :
            maker = cl_DigitalScript(self)
        else:
            QMessageBox.critical(self, "Field System", "Select Field System!")
            return
        maker.generate()
        
    def CMBO_CL_FieldSystemSelect(self):
        if   self.comboBox_CL_FieldSystem.currentText() == "fs"  :
            self.comboBox_CL_ContCal.setCurrentIndex(0)
            self.comboBox_CL_ContCal.setDisabled(True)
            self.comboBox_CL_DFBBC.setCurrentIndex(0)
        elif self.comboBox_CL_FieldSystem.currentText() == "fs6" :
            self.comboBox_CL_ContCal.setDisabled(False)
            self.comboBox_CL_DFBBC.setCurrentIndex(4)
        else:
            self.comboBox_CL_ContCal.setDisabled(True)
        self.CL_message()
        
    def CMBO_CL_Receiver(self):
        self.block_textupdate = True
        rec = self.comboBox_CL_Receiver.currentText()
        if   rec == "K band":
            self.comboBox_CL_LO_SC.setDisabled(False)
            self.comboBox_CL_LO_SL.setDisabled(False)
            self.comboBox_CL_LO_SX.setDisabled(True )
            self.CL_K_presets()
        elif rec == "X band":
            self.comboBox_CL_LO_SC.setDisabled(True )
            self.comboBox_CL_LO_SL.setDisabled(True )
            self.comboBox_CL_LO_SX.setDisabled(False)
            self.CL_X_presets()
        elif rec == "M band":
            self.comboBox_CL_LO_SC.setDisabled(False)
            self.comboBox_CL_LO_SL.setDisabled(True )
            self.comboBox_CL_LO_SX.setDisabled(True )
            self.CL_M_presets()
        elif rec == "C band":
            self.comboBox_CL_LO_SC.setDisabled(False)
            self.comboBox_CL_LO_SL.setDisabled(True )
            self.comboBox_CL_LO_SX.setDisabled(True )
            self.CL_C_presets()
        elif rec == "L band":
            self.comboBox_CL_LO_SC.setDisabled(False)
            self.comboBox_CL_LO_SL.setDisabled(True )
            self.comboBox_CL_LO_SX.setDisabled(True )
            self.CL_L_presets()
        else:
            self.comboBox_CL_LO_SC.setDisabled(True )
            self.comboBox_CL_LO_SL.setDisabled(True )
            self.comboBox_CL_LO_SX.setDisabled(True )
        self.block_textupdate = False
        self.CL_message()
            
    def CL_K_presets(self):
        self.comboBox_CL_LO_SL.clear() 
        self.comboBox_CL_LO_SL.addItems(["17150"])
        self.comboBox_CL_LO_SC.clear() 
        self.comboBox_CL_LO_SC.addItems(["4350"])
        self.comboBox_CL_LO_SX.clear() 
    
    def CL_X_presets(self):
        self.comboBox_CL_LO_SX.clear() 
        self.comboBox_CL_LO_SX.addItems(["11460", "7650"])
        self.comboBox_CL_LO_SL.clear()
        self.comboBox_CL_LO_SC.clear()
    
    def CL_M_presets(self):
        self.comboBox_CL_LO_SC.clear()
        self.comboBox_CL_LO_SC.addItems(["5900", "5300"])
        self.comboBox_CL_LO_SX.clear() 
        self.comboBox_CL_LO_SL.clear()
    
    def CL_C_presets(self):
        self.comboBox_CL_LO_SC.clear()
        self.comboBox_CL_LO_SC.addItems(["4200", "4000"])
        self.comboBox_CL_LO_SX.clear() 
        self.comboBox_CL_LO_SL.clear()
    
    def CL_L_presets(self):
        self.comboBox_CL_LO_SC.clear()
        self.comboBox_CL_LO_SC.addItems(["2300", "2100"])
        self.comboBox_CL_LO_SX.clear() 
        self.comboBox_CL_LO_SL.clear()
        
    def CL_message(self):
        #
        if self.block_textupdate == True: return
        #
        message = ""
        fs  = self.comboBox_CL_FieldSystem.currentText()
        if fs == "fs":
            message += '" Old fieldsystem - calibration for analog spectroscopy\n'
        elif fs == "fs6":
            message += '" New fieldsystem - DBBC\n'
        else:
            message += '" Choose fieldsystem!\n'
        #
        rec   = self.comboBox_CL_Receiver.currentText()
        start = self.spinBox_CL_BBC_Start.value()
        end   = self.spinBox_CL_BBC_End.value()
        if   rec == "K band":
            lo = int(self.comboBox_CL_LO_SC.currentText()) + int(self.comboBox_CL_LO_SL.currentText())
            message += '" K band: from %d to %d (lo = %d + (%d do %d)\n' %(lo+start, lo+end, lo, start, end)
        elif rec == "X band":
            lo = int(self.comboBox_CL_LO_SX.currentText())
            message += '" X band: from %d to %d (lo = %d + (%d do %d)\n' %(lo+start, lo+end, lo, start, end)
        elif rec == "M band":
            lo = int(self.comboBox_CL_LO_SC.currentText())
            message += '" M band: from %d to %d (lo = %d + (%d do %d)\n' %(lo+start, lo+end, lo, start, end)
        elif rec == "C band":
            lo = int(self.comboBox_CL_LO_SC.currentText())
            message += '" C band: from %d to %d (lo = %d + (%d do %d)\n' %(lo+start, lo+end, lo, start, end)
        elif rec == "L band":
            lo = int(self.comboBox_CL_LO_SC.currentText())
            message += '" L band: from %d to %d (lo = %d - (%d do %d)\n' %(lo-end, lo-start, lo, end, start)
        else:
            message += '" Choose receiver!\n'
        message += '" Bandwidth coverage every %d MHz on successive BBCs\n' % int(self.comboBox_CL_DFBBC.currentText())
        message += '" Number of iterations: %d \n' % self.spinBox_CL_NumIter.value() 
        if self.comboBox_CL_ContCal.currentText() == "off":
            message += '" No cont cal - set rec 80Hz 0\n'
        else:
            message += '" With cont cal 80Hz - set rec 80Hz 1\n'
        self.textEdit_CL_message.setPlainText(message)



if __name__ == '__main__':
    app    = QApplication(sys.argv)
    w = Script_maker()
    w.show()
    sys.exit(app.exec_())

