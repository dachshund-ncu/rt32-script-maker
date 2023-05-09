#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" @package catalogs
  \brief     Wczytywanie katalogów itp.
  
  Częściowo funkcje pochodzą z projektu Game:
  - GAME_radio_source.py
  
  \author    Rafał Sarniak
""" 
from __future__ import print_function

import lib_radiosources as lr

class source(lr.MaserSource):
    def __init__(self, name = "Source",  ra='00h00m00s', dec='+60d00m00s', v_sys = 0):
        super(source, self).__init__(name)
        self.v_sys  = float(v_sys)
        self.coord = self.set_coord_hms_astropy([ra, dec])
        #
        self.ile_razy  = 0
        self.band_name = None
        self.soft_name = None
        self.proj_name = None


def src_reader(path):
    with open(path) as plik:
        proj_name = "Default name"
        soft_name = "Default soft"
        band_name = "Default band"
        cat       = []
        for line in plik:
            p = line.split()
            if len(p) < 1: continue
            if p[0][0] == '#': continue
            if p[0] == "Project:":  
                proj_name = line.replace("Project:", "")[:-1].strip()
            if p[0] == "Soft:":
                soft_name = p[1].strip()
            if p[0] == "System:":
                band_name = line.replace("System:", "")[:-1].strip()
            if len(p) < 4: continue
            cat.append( source(p[0], p[1], p[2], p[3]) )
            cat[-1].proj_name = proj_name
            cat[-1].soft_name = soft_name
            cat[-1].band_name = band_name
            if "FS" in soft_name:
                cat[-1].dmin   = int(p[4]) 
                cat[-1].dmax   = int(p[5]) 
                cat[-1].cycles = int(p[6]) 
                cat[-1].script = p[7] 
    return proj_name, soft_name, band_name, cat

if __name__ == '__main__':
    pass
