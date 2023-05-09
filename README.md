# README #

Script_maker creates field system scripts for spectroscopy and calibration  for radio telescope RT32 in Torun Institute of Astronomy, Nicolaus Copernicus University.

### How do I get set up? ###

#### Libraries ####

##### Needed #####
* pyqt
* numpy
* matplotlib
* ephem
* astropy

##### Suggested #####
* pandas

#### Installation with anaconda ####
If You use anaconda, life is beautifull and simple. In tools there is explicit list with libraries in a working configuration.
Go to script_maker directory and do one from below:

* To create new environment for this program:  
conda create --name script_maker_env --file tools/anaconda.env

* To install needed packages to existing environment: 
conda install --name myenv --file tools/anaconda.env

#### Running with anaconda ####
* conda activate your_environment_name
* python script_maker

#### Usage ####
* Find more on wiki: https://bitbucket.org/LordKhayyin/script_maker/wiki/Home

### Who do I talk to? ###
* Rafał Sarniak
* kain at astro.umk.pl
