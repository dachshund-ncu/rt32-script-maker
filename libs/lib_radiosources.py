#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" @package lib_radiosources
  \brief     Ogólna biblioteka dla działań na źródłach. Inne moje twory powinny po niej dziedziczyć.
  
  \author    Rafał Sarniak
  \date      utworzenie:  2018.08.28   
             modyfikacja: 2021.05.14
             
""" 
from __future__ import print_function
#mport wx
import numpy as np
import collections
import time
import sys
import matplotlib
import matplotlib.pyplot as plt
#matplotlib.use('wxagg')

#import threadtools

try:
    import ephem
except ImportError:
    print("--!! Uwaga !!--")
    print("Brak ephem, należy korzystać tylko z funkcji astropy, bądź zainstalować pyephem.")

try:
    import astropy.units as u
    from astropy.time import Time
    from astropy.coordinates import SkyCoord, EarthLocation, AltAz, Galactic, Angle
    import astropy.coordinates as coordinates
except ImportError:
    print("--!! Uwaga !!--")
    print("Brak astropy, należy korzystać tylko z funkcji ephem, bądź zainstalować astropy.")

try:
    import pandas as pd
except:
    print("--!! Uwaga !!--")
    print("Brak pandas. Zainstaluj pandas, jeśli chcesz korzystać z metod wykorzystujących ją.")



# Klasa podstawowa do jakichkolwiek programów wykorzystujących źródła na niebie.
# Inne powinny dziedziczyć po niej z ewentualnym nadpisywaniem pojedynczych metod.
# 
class RadioSource(object):
    #
    # Oszacowane zgrubnie na podstawie skanów z pozycjonowania:
    Bezp_odl_K  = 0.05 # deg czyli  3 arcmin, czyli  180 arcsec
    Bezp_odl_C2 = 0.3  # ded czyli 18 arcmin, czyli 1080 arcsec
    def __init__(self, name):
        self.name        = name
        self.other_names = []
        self.coord       = None
        self.coord_ref   = None
        self.coord_ephem = None
        self.distance    = None
        self.v_sys       = None
        self.L_bol       = None
        self.odpowiednik = None
        
    def ra_str(self):
        return self.coord.ra.to_string(u.hour, pad=True, sep='')
    def dec_str(self):
        return self.coord.dec.to_string(u.degree, alwayssign=True, pad=True, sep='')
    
    def make_ephem_Observer():
        obs = ephem.Observer()
        obs.lon  = "18.564057404305977"
        obs.lat  = "53.095461865467264"
        obs.elev = 133.60693397274653
        obs.date = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        return obs
    
    ephem_obs     = make_ephem_Observer()
    astropy_obs   = EarthLocation(x = 3638558.51*u.m,     y = 1221969.72*u.m,    z = 5077036.76*u.m)
    
    def set_coord_hms_ephem(self, coords, epoch = "2000"):
        # Wczytywanie tylko w hmsdms na razie.
        epoch = str(epoch)
        if len(coords) == 6:
            ra_h, ra_m, ra_s, dec_d, dec_m, dec_s = coords
            ra_h, ra_m, ra_s, dec_d, dec_m, dec_s = int(ra_h), int(ra_m), float(ra_s), int(dec_d), int(dec_m), float(dec_s) 
            self.coord_ephem = ephem.readdb(self.name + ",f|M|F7,%02d:%02d:%02g,%02d:%02d:%02g,1.0," % (int(ra_h), int(ra_m), float(ra_s), int(dec_d), int(dec_m), float(dec_s)) + epoch)
            self.coord_ephem.compute(RadioSource.ephem_obs)
            return self.coord_ephem
        elif len(coords) == 2:
            ra, dec = coords
            self.coord_ephem = ephem.readdb(self.name + ",f|M|F7,%s,%s,1.0," % (ra, dec) + epoch)
        else:
            raise Exception("Źle zdefiniowane współrzędne.", len(coords))
        
    def set_coord_hms_astropy(self, coords):
        # Wczytywanie tylko w hmsdms na razie.
        if len(coords) == 6:
            ra_h, ra_m, ra_s, dec_d, dec_m, dec_s = coords
            ra_h, ra_m, ra_s, dec_d, dec_m, dec_s = int(ra_h), int(ra_m), float(ra_s), int(dec_d), int(dec_m), float(dec_s) 
            self.coord = SkyCoord("%02d:%02d:%02f %02d:%02d:%02f" % (ra_h, ra_m, ra_s, dec_d, dec_m, dec_s),  unit=(u.hourangle, u.deg) )
            return self.coord
        elif len(coords) == 2:
            ra, dec = coords
            self.coord = SkyCoord("%s %s" % (ra, dec),  unit=(u.hourangle, u.deg) )
            return self.coord
        else:
            raise Exception("Źle zdefiniowane współrzędne.", len(coords))
    
    def set_act_time_ephem(self):
        RadioSource.ephem_obs.date = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        return RadioSource.ephem_obs.date
    
    def set_act_time_astropy(self):
        return Time(time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()), format='isot', scale='utc')
    
    def astropy2ephem(self, epoch = 2000):
        name = str(self.name)
        h, m, s = self.coord.ra.hms
        dd, mm, ss = self.coord.dec.dms
        ra    = "%d:%02d:%g" % (int(h), abs(int(m)), abs(s))
        #dec   = Angle.to_string(self.coord.dec, sep = ":" )
        dec   = "%d:%02d:%g" % (int(dd), abs(int(mm)), abs(ss))
        epoch = str(epoch)
        converted = ephem.readdb(name + ",f|M|F7," + ra + "," + dec +",1.0," + epoch)
        self.coord_ephem = converted
        return converted
    
    def ephem2astropy(self):
        self.coord_ephem.compute(RadioSource.ephem_obs)
        self.coord = SkyCoord("%s %s" % (str(self.coord_ephem.a_ra), str(self.coord_ephem.a_dec)),  unit=(u.hourangle, u.deg) )
        return self.coord
    
    def position_alt_az_astropy(self, time = None):
        if time == None:
            time = RadioSource.set_act_time_astropy(self)
        position_alt_az =  self.coord.transform_to(AltAz(obstime=time,location = RadioSource.astropy_obs))
        return position_alt_az
    
    def position_alt_az_ephem(self, time = None):
        if time == None:
            time = RadioSource.set_act_time_ephem(self)
        else:
            RadioSource.ephem_obs.date = time
        self.coord_ephem.compute(RadioSource.ephem_obs)
        position_alt_az = (self.coord_ephem.az, self.coord_ephem.alt)
        return position_alt_az
        
    def __str__(self):
        return self.name
        
    def __repr__(self):
        return self.name
    
    # Dla naszej anteny (z podr. obserwatora)
    def HPBW_lbda(lbda): # w arcmin
        return 1.23*lbda # lbda w cm

    def HPBW_nu(nu):     # w arcmin
        return 37./nu    # nu w GHz
    '''
    @threadtools.callafter
    def wykres_widocznosci(self, fig=None, date=None, linestyle='-', f_astropy=False):
        "Tworzy wykres widoczności źródeł w katalogu. Może to robić ephem albo astropy."
        def on_fig_close(event):
            event.canvas.figure.has_been_closed = True
            #print('Closed Figure')            
        source = self
        flaga_robsam = False
        daypart = np.linspace(0, 1, 100)
        if fig.has_been_closed == True or fig == None:
            flaga_robsam = True
            fig = plt.figure()
            ax = fig.add_subplot(111)
            ax.set_ylim(0, 90)
            ax.set_xlim(0, 24)
            ax.set_title("Widoczność źródeł nad horyzontem.")
            ax.set_xlabel('Czas UT [h]')
            ax.set_ylabel('Wysokość nad horyzontem [deg]')
            ax.fill_between([0, 24], [0, 0], [15, 15], color="black", facecolor="grey", alpha=0.05) 
            ax.fill_between([0, 24], [90, 90], [75, 75], color="black", facecolor="grey", alpha=0.05)
            fig.canvas.mpl_connect('close_event', on_fig_close)
        else:
            ax = fig.axes[0]
            ax.set_ylim(0, 90)
            ax.set_xlim(0, 24)
            plt.draw()
        if f_astropy  == False:
            if date == None:
                today = time.strftime("%Y/%m/%d", time.gmtime())
                date  = today
            alt = [source.position_alt_az_ephem(date + str(part)[1:])[1] for part in daypart]
            ax.plot(daypart*24, np.rad2deg(alt), linestyle = linestyle, label = source.name)
        else:
            if date == None:
                today = Time(time.strftime("%Y-%m-%dT00:00:00", time.gmtime()), format='isot', scale='utc')
                date  = today
            daypart = daypart*24*u.hour
            source_altaz = source.position_alt_az_astropy(date+daypart)
            ax.plot(daypart, source_altaz.alt, linestyle = linestyle, label=source.name)
        if flaga_robsam:
            ax.grid(True)
            plt.legend(loc="best")
            plt.show()
        return ax
    '''


# ---------------------------------------------------------------------------------------    
# Podklasa domyślnie dla maserów.
class MaserSource(RadioSource):
    def __init__(self, name):
        super(MaserSource, self).__init__(name)
        self.Si = None 
        


# ---------------------------------------------------------------------------------------   
# Klasa katalogów maserów w postaci listy.
class MaserCatalogue(list):
    
    def open_catalogue(self, path, f_ephem = True, f_astropy=False):
        """Wczytuje katalog z pliku. Skombinować inne właściwości jak ładnie wczytać do słownika czy coś."""
        plik = open(path)
        for line in plik:
            if line[0] == '#': continue
            p = line.split()
            zrodlo = MaserSource(p[0])
            if f_ephem:
                zrodlo.set_coord_hms_ephem(p[1:7])
            if f_astropy:
                zrodlo.set_coord_hms_astropy(p[1:7])
            self.append(zrodlo)
            
    def wykres_widocznosci(self, ax=None, date=None, f_astropy=False):
        "Tworzy wykres widoczności źródeł w katalogu. Może to robić ephem albo astropy."
        linestyles = ['-', '--', '-.', ':']
        daypart = np.linspace(0, 1, 100)
        if ax == None:
            ax = plt.axes()
            
        if f_astropy  == False:
            if date == None:
                today = time.strftime("%Y/%m/%d", time.gmtime())
                date  = today
            i=0
            for source in self:
                alt = [source.position_alt_az_ephem(date + str(part)[1:])[1] for part in daypart]
                ax.plot(daypart*24, np.rad2deg(alt), linestyle = linestyles[i], label = source.name)
                i+=1;
                if i == 4: i = 0
        else:
            if date == None:
                today = Time(time.strftime("%Y-%m-%dT00:00:00", time.gmtime()), format='isot', scale='utc')
                date  = today
            i = 0
            daypart = daypart*24*u.hour
            for source in self:
                source_altaz = source.position_alt_az_astropy(date+daypart)
                ax.plot(daypart, source_altaz.alt, linestyle = linestyles[i], label=source.name)
                i+=1
                if i == 4: i = 0
        ax.set_ylim(0, 90)
        ax.set_xlim(0, 24)
        ax.set_title("Widoczność źródeł nad horyzontem.")
        ax.set_xlabel('Czas UT [h]')
        ax.set_ylabel('Wysokość nad horyzontem [deg]')
        return ax

    def make_pandas(self):
        zbior = set()
        for item in self:
            zbior.update(item.__dict__.keys())
        df = pd.DataFrame(columns=zbior)
        for item in self:
            df.loc[len(df)] = item.__dict__
        naglowek = ["name", "other_names", "coord", "v_sys"]
        naglowek.extend( list( zbior - set(naglowek) ) )
        df = df.reindex_axis(naglowek, axis=1)
        if self[0].coord == None:
            try:
                coords = [str(x.coord_ephem) for x in self ]
            except:
                print("Nie ma koordynatów dla obiektu ", x.name)
                return
        else:
            coords = [(x.coord.to_string('hmsdms')) for x in self ]
        df["coord"] = coords
        return df
    
    def macz_katalogs_astropy(self, inny_katalog, separacja_arcsec = 2*60*60):
        for obiekt in self:
            for porownanie in inny_katalog:
                dec  = obiekt.coord.dec.deg
                dec2 = porownanie.coord.dec.deg
                if abs(dec - dec2) > 2: continue  # Jeśli odległość jest większa niż 2 stopnie w dec, to nie zawracam tyłka.
                odleglosc = obiekt.coord.separation(porownanie.coord)
                if odleglosc.arcsec > separacja_arcsec: 
                    continue
                if odleglosc.arcsec <= separacja_arcsec and not obiekt.odpowiednik:
                    obiekt.odpowiednik = ( porownanie, odleglosc.arcsec )
                elif obiekt.odpowiednik[1] > odleglosc.arcsec:            # Jeśli znalazł się bliższy obiekt.
                    obiekt.odpowiednik = ( porownanie, odleglosc.arcsec )
                print(obiekt, porownanie, "%.2f" % odleglosc.arcsec)
                
    def wspolna_wiazka_astropy(self, inny_katalog, freq=22.2):
        for obiekt in self:
            for porownanie in inny_katalog:
                dec  = obiekt.coord.dec.deg
                dec2 = porownanie.coord.dec.deg
                if abs(dec - dec2) > 2: continue  # Jeśli odległość jest większa niż 2 stopnie w dec, to nie zawracam tyłka.
                odleglosc = obiekt.coord.separation(porownanie.coord)
                if odleglosc.arcmin < RadioSource.HPBW_nu(freq):
                    print(obiekt, porownanie, "Wspolna wiazka na f = %g GHz" % freq)
                elif freq > 22.0 and freq < 23.0 and odleglosc.arcmin < RadioSource.Bezp_odl_K:
                    print(obiekt, porownanie, "Może być w listku bocznym na f = %g GHz" % freq)
                elif freq > 4.4 and freq < 5.1 and odleglosc.arcmin < RadioSource.Bezp_odl_C2:
                    print(obiekt, porownanie, "Może być w listku bocznym na f = %g GHz" % freq)
                    
    def przypisz_other_names_odpowiednikow(self):
        for obiekt in self:
            if obiekt.odpowiednik:
                obiekt.other_names.append(obiekt.odpowiednik[0].name)
    
    def pokaz_odpowiedniki(self):
        for obiekt in self:
            if obiekt.odpowiednik:
                print(obiekt.name, obiekt.odpowiednik)
                
    def macz_katalogs_ephem(self, inny_katalog, separacja_arcsec = 2*60*60):
        arcdeg = np.pi/180.
        arcsec = arcdeg/60./60
        for obiekt in self:
            for porownanie in inny_katalog:
                
                try:
                    dec  = obiekt.coord_ephem.a_dec
                    dec2 = porownanie.coord_ephem.a_dec
                except:
                    print("Obiekty nie mają koordynatów wyliczonych przez ephem.")
                    return
                if abs(dec - dec2) > 2*arcdeg: continue  # Jeśli odległość jest większa niż 2 stopnie w dec, to nie zawracam tyłka.
                odleglosc = ephem.separation(obiekt.coord_ephem, porownanie.coord_ephem)
                odleglosc = odleglosc/arcsec
                if odleglosc > separacja_arcsec: 
                    continue
                if odleglosc <= separacja_arcsec and obiekt.odpowiednik == None:
                    obiekt.odpowiednik = ( porownanie, odleglosc )
                elif obiekt.odpowiednik[1] > odleglosc:            # Jeśli znalazł się bliższy obiekt.
                    obiekt.odpowiednik = ( porownanie, odleglosc )
                print(obiekt, porownanie, odleglosc)

    def wspolna_wiazka_ephem(self, inny_katalog, freq=22.2):
        arcdeg = np.pi/180.
        arcmin = arcdeg/60.
        arcsec = arcdeg/60./60
        for obiekt in self:
            for porownanie in inny_katalog:
                dec  = obiekt.coord_ephem.a_dec
                dec2 = porownanie.coord_ephem.a_dec
                if abs(dec - dec2) > 2*arcdeg: continue  # Jeśli odległość jest większa niż 2 stopnie w dec, to nie zawracam tyłka.
                odleglosc = ephem.separation(obiekt.coord_ephem, porownanie.coord_ephem)
                
                if odleglosc/arcmin < RadioSource.HPBW_nu(freq):
                    print(obiekt, porownanie, "Wspolna wiazka na f = %g GHz" % freq)
                elif freq > 22.0 and freq < 23.0 and odleglosc/arcmin < RadioSource.Bezp_odl_K:
                    print(obiekt, porownanie, "Może być w listku bocznym na f = %g GHz" % freq)
                elif freq > 4.4 and freq < 5.1 and odleglosc/arcmin < RadioSource.Bezp_odl_C2:
                    print(obiekt, porownanie, "Może być w listku bocznym na f = %g GHz" % freq)
                    
    def element_by_name(self, name):
        for obiekt in self:
            if obiekt.name in name:
                return obiekt
        else:
            print("Nie znalazłem")
            return None

if __name__ == '__main__':
    pass
