 #!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" @package radio_molecule
  \brief     Definicja klasy do listy molekuł.
  
  \author    Rafał Sarniak
"""  
from __future__ import print_function


class radio_molecule(object):
    def __init__(self, name, rt4_sys, freq, nsigma_pol1, nsigma_pol2):
        self.name        = name
        self.rt4_sys     = rt4_sys
        self.freq        = float(freq)
        # nsigma only for GAME (for now).
        self.nsigma_pol1 = float(nsigma_pol1)
        self.nsigma_pol2 = float(nsigma_pol2)
        
    def __str__(self):
        return self.name
        
    def __repr__(self):
        return self.name
    
    def przypisz_nsigma(self, parent):
        # Used in GAME.
        parent.config["nsigma1"] = self.nsigma_pol1
        parent.config["nsigma2"] = self.nsigma_pol2
    
def make_molecule_list(path):
    print("Wczytuję plik z danymi molekuł:", path)
    molecules_list = ["Cząsteczka"]
    plik = open(path)
    for line in plik:
        if line[0] == '#': continue
        p = line.split(", ")
        molecules_list.append(radio_molecule(p[0], p[1], p[2], p[3], p[4]))
    print("Wczytano %d molekuł." % (len(molecules_list)-1) )
    return molecules_list



    
if __name__ == '__main__':
    molecules_list = make_molecule_list("./molecules")
    print(molecules_list)
        
