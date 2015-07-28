import logging
import numpy as np
import pysynphot
import os
import glob
from astropy.io import fits
from astropy.table import Table
from thesis import atmos_comp
import time
import pdb

log = logging.getLogger('atmospheres')

def get_kurucz_atmosphere(metallicity=0, temperature=20000, gravity=4):
    """
    metallicity in [Fe/H] (def = +0.0): 
          +1.0, +0.5, +0.3, +0.2, +0.1, +0.0, -0.1, -0.2, -0.3, -0.5, -1.0, 
          -1.5, -2.0, -2.5, -3.0, -3.5, -4.0, -4.5, -5.0.

    temperatures (def = 20,000 Kelvin):
                Temperature Range      Grid Step
                       K                   K

                  3000 - 10000            250 
                 10000 - 13000            500
                 13000 - 35000           1000
                 35000 - 50000           2500

    log gravity (def = 0.0) in the range of 0.0 - 5.0 in 0.5 increments
    """
    sp = pysynphot.Icat('k93models', temperature, metallicity, gravity)

    # Do some error checking
    idx = np.where(sp.flux != 0)[0]
    if len(idx) == 0:
        print 'Could not find Kurucz 1993 atmosphere model for'
        print '  temperature = %d' % temperature
        print '  metallicity = %.1f' % metallicity
        print '  log gravity = %.1f' % gravity

    return sp

def get_castelli_atmosphere(metallicity=0, temperature=20000, gravity=4):
    """
    metallicity in [Fe/H] (def = +0.0): 
          0.0, -0.5, -1.0, -1.5, -2.0, -2.5.

    temperatures (def = 20,000 Kelvin):
                Temperature Range      Grid Step
                       K                   K

                  3000 -  13000            250 
                  13000 - 50000            1000

    log gravity (def = 4.0) in the range of 2.0 - 5.0 in 0.5 increments
    """
    # Round given temp, gravity to closest model that exists
    # No models below 3000 K
    if temperature < 3000:
        print 'No ck04 model below 3000 K'
        return

    t1 = np.arange(3000, 13000+1, 250)
    t2 = np.arange(13000,50000+1, 1000)
    temp_arr = np.append(t1, t2)
    grav_arr = np.arange(2.0, 5.0+0.1, 0.5)

    temp_ind = np.where( abs(temp_arr - temperature) == min(abs(temp_arr - temperature)) )[0]
    grav_ind = np.where( abs(grav_arr - gravity) == min(abs(grav_arr - gravity)) )[0]

    # Error checking: stop if temp/grav difference is too high
    #if ((abs(temperature - temp_arr[temp_ind[0]]) > 250) | (abs(gravity - grav_arr[grav_ind[0]]) > 0.5) ):
    #    print 'BAD TEMP/GRAV MATCH'
    #    return
        
    # Define new temp based on closest match
    temperature = temp_arr[temp_ind[0]]
    gravity = grav_arr[grav_ind[0]]

    # Pysynphot crashes if gravity is less than 2.5; change gravity to 2.5
    # if this is the case
    if gravity < 2.5:
        gravity = 2.5
    
    sp = pysynphot.Icat('ck04models', temperature, metallicity, gravity)

    # Do some error checking
    idx = np.where(sp.flux != 0)[0]
    if len(idx) == 0:
        print 'Could not find Castelli and Kurucz 2004 atmosphere model for'
        print '  temperature = %d' % temperature
        print '  metallicity = %.1f' % metallicity
        print '  log gravity = %.1f' % gravity

    return sp

def get_nextgen_atmosphere(metallicity=0, temperature=5000, gravity=4):
    """
    metallicity = [M/H] (def = 0)
    temperature = Kelvin (def = 5000)
    gravity = log gravity (def = 4.0)
    """
    sp = pysynphot.Icat('nextgen', temperature, metallicity, gravity)

    # Do some error checking
    idx = np.where(sp.flux != 0)[0]
    if len(idx) == 0:
        print 'Could not find NextGen atmosphere model for'
        print '  temperature = %d' % temperature
        print '  metallicity = %.1f' % metallicity
        print '  log gravity = %.1f' % gravity

    return sp

def get_amesdusty_atmosphere(metallicity=0, temperature=5000, gravity=4):
    """
    metallicity = [M/H] (def = 0)
    temperature = Kelvin (def = 5000)
    gravity = log gravity (def = 4.0)
    """
    sp = pysynphot.Icat('AMESdusty', temperature, metallicity, gravity)

    # Do some error checking
    idx = np.where(sp.flux != 0)[0]
    if len(idx) == 0:
        print 'Could not find AMESdusty Allard+ 2000 atmosphere model for'
        print '  temperature = %d' % temperature
        print '  metallicity = %.1f' % metallicity
        print '  log gravity = %.1f' % gravity

    return sp

def get_phoenix_atmosphere(metallicity=0, temperature=5000, gravity=4):
    """
    metallicity = [M/H] (def = 0)
    temperature = Kelvin (def = 5000)
    gravity = log gravity (def = 4.0)
    """
    sp = pysynphot.Icat('phoenix', temperature, metallicity, gravity)

    # Do some error checking
    idx = np.where(sp.flux != 0)[0]
    if len(idx) == 0:
        print 'Could not find PHOENIX BT-Settl (Allard+ 2011 atmosphere model for'
        print '  temperature = %d' % temperature
        print '  metallicity = %.1f' % metallicity
        print '  log gravity = %.1f' % gravity

    return sp

def get_cmfgenRot_atmosphere(metallicity=0, temperature=30000, gravity=4.14):
    """
    metallicity = [M/H] (def = 0)
    temperature = Kelvin (def = 30000)
    gravity = log gravity (def = 4.14)
    """
    sp = pysynphot.Icat('cmfgenF15_rot', temperature, metallicity, gravity)

    # Do some error checking
    idx = np.where(sp.flux != 0)[0]
    if len(idx) == 0:
        print 'Could not find CMFGEN rotating atmosphere model (Fierro+15) for'
        print '  temperature = %d' % temperature
        print '  metallicity = %.1f' % metallicity
        print '  log gravity = %.1f' % gravity

    return sp

def get_cmfgenNoRot_atmosphere(metallicity=0, temperature=30000, gravity=4.14):
    """
    metallicity = [M/H] (def = 0)
    temperature = Kelvin (def = 30000)
    gravity = log gravity (def = 4.14)
    """
    sp = pysynphot.Icat('cmfgenF15_noRot', temperature, metallicity, gravity)

    # Do some error checking
    idx = np.where(sp.flux != 0)[0]
    if len(idx) == 0:
        print 'Could not find CMFGEN non-rotating atmosphere model (Fierro+15) for'
        print '  temperature = %d' % temperature
        print '  metallicity = %.1f' % metallicity
        print '  log gravity = %.1f' % gravity

    return sp

def get_phoenixv16_atmosphere(metallicity=0, temperature=4000, gravity=4, rebin=True):
    """
    metallicity = [M/H] (def = 0)
    temperature = Kelvin (def = 5000)
    gravity = log gravity (def = 4.0)

    temp: 2300 - 7000 steps of 100 K; 7000 - 12000 in steps of 200 K
    grav: 2.0 - 6.0, steps of 0.5 (gaurenteed over all temps)

    If rebin = True, pull from spectra that have been rebinned to ck04model resolution;
    this is important for spectrophotometry, otherwise it takes forever
    """
    # Round given temp, gravity to closest model that exists
    if (temperature < 2300) | (temperature > 12000) | (gravity < 2.0):
        print 'No phoenixV16 model below 2300 K or above 12000 K, or grav < 2.0'
        return
    
    t1 = np.arange(2300, 7000+1, 100)
    t2 = np.arange(7000,12000+1, 200)
    temp_arr = np.append(t1, t2)
    grav_arr = np.arange(2.0, 6.0+0.1, 0.5)

    temp_ind = np.where( abs(temp_arr - temperature) == min(abs(temp_arr - temperature)) )[0]
    grav_ind = np.where( abs(grav_arr - gravity) == min(abs(grav_arr - gravity)) )[0]

    # Error checking: stop if temp/grav difference is too high
    if ((abs(temperature - temp_arr[temp_ind][0]) > 100) | (abs(gravity - grav_arr[grav_ind[0]]) > 0.5) ):
        print 'BAD TEMP/GRAV MATCH'
        return    
        
    # Define new temp based on closest match
    temperature = temp_arr[temp_ind[0]]
    gravity = grav_arr[grav_ind[0]]
    
    if rebin == True:
        sp = pysynphot.Icat('phoenix_v16_rebin', temperature, metallicity, gravity)
    else:
        sp = pysynphot.Icat('phoenix_v16', temperature, metallicity, gravity)
    
    # Do some error checking
    idx = np.where(sp.flux != 0)[0]
    if len(idx) == 0:
        print 'Could not find PHOENIXv16 (Husser+13) atmosphere model for'
        print '  temperature = %d' % temperature
        print '  metallicity = %.1f' % metallicity
        print '  log gravity = %.1f' % gravity

    return sp

def get_atlas_phoenix_atmosphere(metallicity=0, temperature=4000, gravity=4):
    """
    Return atmosphere that is a linear merge of atlas ck04 model and phoenixV16.

    Only valid for temp of 5250 K, gravity from 0 = 5.0 in steps of 0.5
    """
    # Round given temp, gravity to closest model that exists
    if (temperature < 5000) | (temperature > 5500):
        print 'No ATLAS-PHOENIX merge model outside 5000 - 5500'
        return

    temp_arr = np.array([5250])
    grav_arr = np.arange(0.0, 5.0+0.1, 0.5)

    temp_ind = np.where( abs(temp_arr - temperature) == min(abs(temp_arr - temperature)) )[0]
    grav_ind = np.where( abs(grav_arr - gravity) == min(abs(grav_arr - gravity)) )[0]

    # Error checking: stop if temp/grav difference is too high
    if ((abs(temperature - temp_arr[temp_ind[0]]) > 250) | (abs(gravity - grav_arr[grav_ind[0]]) > 0.5) ):
        print 'BAD TEMP/GRAV MATCH'
        return
        
    # Define new temp based on closest match
    temperature = temp_arr[temp_ind[0]]
    gravity = grav_arr[grav_ind[0]]
    
    sp = pysynphot.Icat('merged', temperature, metallicity, gravity)

    # Do some error checking
    idx = np.where(sp.flux != 0)[0]
    if len(idx) == 0:
        print 'Could not find ATLAS-PHOENIX merge atmosphere model for'
        print '  temperature = %d' % temperature
        print '  metallicity = %.1f' % metallicity
        print '  log gravity = %.1f' % gravity

    return sp


#---------OLD MERGED ATMOSPHERES------------#
#def test_merged_atmospheres(metallicity=0, gravity=4):
#    """
#    Compare spectra from Castelli and NextGen at the boundary
#    temperature of 8000 K.
#
#    Compare spectra from NextGen and Phoenix at the boundary
#    temperature of 4000 K.
#    """
#    cast = get_castelli_atmosphere(temperature=8000, 
#                                   metallicity=metallicity, gravity=gravity)
#
#    ngen = get_nextgen_atmosphere(temperature=8000,
#                                  metallicity=metallicity, gravity=gravity)
#
#    # Now Plot the spectra
#    py.figure(1)
#    py.clf()
#    py.loglog(cast.wave, cast.flux, 'r-', label='Castelli')
#    py.plot(ngen.wave, ngen.flux, 'b-', label='NextGen')
#    py.xlabel('Wavelength')
#    py.ylabel('Flux')
#    py.legend()
#    py.xlim(3000, 50000)
#    py.ylim(1e3, 1e8)
#
#
#    ngen = get_nextgen_atmosphere(temperature=4000,
#                                  metallicity=metallicity, gravity=gravity)
#
#    phoe = get_phoenix_atmosphere(temperature=4000,
#                                  metallicity=metallicity, gravity=gravity)
#    # Now Plot the spectra
#    py.figure(2)
#    py.clf()
#    py.loglog(phoe.wave, phoe.flux, 'r-', label='Phoenix')
#    py.plot(ngen.wave, ngen.flux, 'b-', label='NextGen')
#    py.xlabel('Wavelength')
#    py.ylabel('Flux')
#    py.legend()
#    py.xlim(3000, 50000)
#    py.ylim(1, 1e8)
#
#    
#def get_merged_atmosphere(metallicity=0, temperature=20000, gravity=4):
#    if temperature < 4000 or (temperature < 7000 and gravity < 4.0):
#        print 'Phoenix Model Atmosphere Used'
#        return get_phoenix_atmosphere(metallicity=metallicity,
#                                      temperature=temperature,
#                                      gravity=gravity)
#
#    # if temperature < 4000:
#    #     return get_amesdusty_atmosphere(metallicity=metallicity,
#    #                                     temperature=temperature,
#    #                                     gravity=gravity)
#
#    if temperature >= 4000 and temperature < 7000 and gravity >= 4.0:
#        print 'Nextgen atmosphere used'
#        return get_nextgen_atmosphere(metallicity=metallicity,
#                                      temperature=temperature,
#                                      gravity=gravity)
#
#    if temperature >= 7000: 
#        return get_castelli_atmosphere(metallicity=metallicity,
#                                       temperature=temperature,
#                                       gravity=gravity)
#
#---------------------------------------------------------------------#
def get_merged_atmosphere(metallicity=0, temperature=20000, gravity=4):
    """
    If T > 20,000 K : CMFGEN
    20,000 > T > 5500: ATLAS (ck04)
    5500 > T > 5000: ATLAS/PHOENIX merge
    T < 5000: PHEONIXv16 (Husser+13) 
    """
    if temperature < 5000:
        print 'Phoenix Model Atmosphere Used'
        return get_phoenixv16_atmosphere(metallicity=metallicity,
                                      temperature=temperature,
                                      gravity=gravity)

    if (temperature > 5000) & (temperature < 5500):
        print 'ATLAS and PHOENIX merged atmosphere used'
        return get_atlas_phoenix_atmosphere(metallicity=metallicity,
                                         temperature=temperature,
                                         gravity=gravity)

    if temperature > 5500:
        print 'ATLAS atmosphere used'
        return get_castelli_atmosphere(metallicity=metallicity,
                                      temperature=temperature,
                                      gravity=gravity)

    if temperature > 20000:
        print 'Warning: ATLAS still used at high temps'
        return get_castelli_atmosphere(metallicity=metallicity,
                                       temperature=temperature,
                                       gravity=gravity)

        print 'CMFGEN model with rotation used'
        #return get_cmfgenrot_atmosphere(metallicity=metallicity,
        #                               temperature=temperature,
        #                               gravity=gravity)    

#--------------------------------------#
# Atmosphere formatting functions
#--------------------------------------#

def download_CMFGEN_atmospheres(Table_rot, Table_norot):
    """
    Downloads CMFGEN models from
    https://sites.google.com/site/fluxesandcontinuum/home;
    these contain continuum as well as lines.

    Table_rot, Table_norot are tables with the file prefixes
    and model atmosphere parameters, taken by hand from the
    Fierro+15 paper

    Website addresses are hardcoded
    
    Puts downloaded models in the current working directory.
    """
    print 'WARNING: THIS DOES NOT COMPLETELY WORK'
    print '**********************'
    t_rot = Table.read(Table_rot, format='ascii')
    t_norot = Table.read(Table_norot, format='ascii')

    tables = [t_rot, t_norot]
    filenames = [t_rot['col1'], t_norot['col1']]

    # Hardcoded list of webiste addresses
    web_base1 = 'https://sites.google.com/site/fluxesandcontinuum/home/'
    web_base2 = 'https://sites.google.com/site/modelsobmassivestars/'
    web = [web_base1+'009-solar-masses/',web_base1+'012-solar-masses/',
           web_base1+'015-solar-masses/',web_base1+'020-solar-masses/',
           web_base1+'025-solar-masses/',web_base2+'009-solar-masses-tracks/',
           web_base2+'040-solar-masses/',web_base2+'060-solar-masses/',
           web_base1+'085-solar-masses/',web_base1+'120-solar-masses/']
    # Array of masses that matches the website addresses
    mass_arr = np.array([9.,12.,15.,20.,25.,32.,40.,60.,85.,120.])

    # Loop through rotating and unrotating case. First loop is rot, second unrot
    for i in range(2):
        # Extract masses from filenames
        masses = []
        for j in filenames[i]:
            tmp = j.split('m')
            mass = float(tmp[1][:-1])
            masses.append(mass)

        # Download the models webpage by webpage. A bit tricky because masses
        # change slightly within a particular website. THIS IS WHAT FAILS
        for j in range(len(web)):
            if j == 0:
                good = np.where( (masses <= mass_arr[j]) )
            else:
                g = j - 1
                good = np.where( (masses <= mass_arr[j]) &
                                (masses > mass_arr[g]) )
            # Use wget command to pull down the files, and unzip them
            for k in good[0]:
                full = web[j]+'{1:s}.flx.zip'.format(mass_arr[j],filenames[i][k])
                os.system('wget ' + full)
                os.system('unzip '+ filenames[i][k] + '.flx.zip')


    return

def organize_CMFGEN_atmospheres(path_to_dir):
    """
    Change CMFGEN grid from Fierro+15
    (http://www.astroscu.unam.mx/atlas/index.html)
    into cdbs format. THIS IS STEP 1

    path_to_dir is from current working directory to directory
    containing the downloaded models. Assumed that models
    and tables describing parameters are in this directory.

    Tables describing parameters MUST be named Table_rot.txt,
    Table_noRot.txt. Made by hand from Tables 3, 4 in Fierro+15.
    These are located in same original directory as atmosphere files

    Will separate files into 2 subdirectories, one rotating and
    the other non-rotating

    *Can't have any other files starting with "t" in model directory to start!*
    """
    # First, record current working directory to return to later
    start_dir = os.getcwd()
    
    # Enter atmosphere directory, collect rotating and non-rotating
    # file names (assumed to all start with "t")
    os.chdir(path_to_dir)
    rot_models = glob.glob("t*r.flx*")
    noRot_models = glob.glob("t*n.flx*")

    # Separate into different subdirectories
    if os.path.exists('cmfgenF15_rot'):
        pass
    else:
        os.mkdir('cmfgenF15_rot')
        os.mkdir('cmfgenF15_noRot')

    for mod in rot_models:
        cmd = 'mv {0:s} cmfgenF15_rot'.format(mod)
        os.system(cmd)

    for mod in noRot_models:
        cmd = 'mv {0:s} cmfgenF15_noRot'.format(mod)
        os.system(cmd)

    # Also move Tables with model parameters into correct directory
    os.system('mv Table_rot.txt cmfgenF15_rot')
    os.system('mv Table_noRot.txt cmfgenF15_noRot')
    
    # Return to original directory
    os.chdir(start_dir)
        
    return

def make_CMFGEN_catalog(path_to_dir):
    """
    Change CMFGEN grid from Fierro+15
    (http://www.astroscu.unam.mx/atlas/index.html)
    into cdbs format. THIS IS STEP 2, after separate_atmospheres has
    been run.

    path_to_dir is from current working directory to directory
    containing the rotating or non-rotating models (i.e. cmfgenF15_rot). Also,
    needs to be a Table*.txt file which contains the parameters for all of the
    original models, since params in filename are not precise enough

    Will create catalog.fits file in atmosphere directory with
    description of each model

    *Can't have any other files starting with "t" in model directory to start!*
    """
    # Record current working directory for later
    start_dir = os.getcwd()
    
    # Enter atmosphere directory
    os.chdir(path_to_dir)
   
    # Extract parameters for each atmosphere
    # Note: can't rely on filename for this because not precise enough!!

    #---------OLD: GETTING PARAMS FROM FILENAME-------#
    # Collect file names (assumed to all start with "t")
    #files = glob.glob("t*")
    #for name in files:
    #    tmp = name.split('l')
    #    temp = float(tmp[0][1:]) * 100.0 # In kelvin

    #    lumtmp = tmp[1].split('_')
    #    lum = float(lumtmp[0][:-5]) * 1000.0 # In L_sun

    #    mass = float(lumtmp[0][5:-1]) # In M_sun
        
        # Need to calculate log g from T and L (cgs)
    #    lum_sun = 3.846 * 10**33 # erg/s
    #    M_sun = 2 * 10**33 # g
    #    G_si = 6.67 * 10**(-8) # cgs
    #    sigma_si = 5.67 * 10**(-5) # cgs

    #    g = (G_si * mass * M_sun * 4 * np.pi * sigma_si * temp**4) / \
    #      (lum * lum_sun)
    #    logg = np.log10(g)
    #---------------------------------------------------#

    # Read table with atmosphere params
    table = glob.glob('Table_*')
    t = Table.read(table[0], format = 'ascii')
    names = t['col1']
    temps = t['col2']
    logg = t['col4']

    # Create catalog.fits file
    index_str = []
    name_str = []
    for i in range(len(names)):
        index = '{0:5.0f},0.0,{1:3.2f}'.format(temps[i], logg[i])

        #---NOTE: THE FOLLOWING DEPENDS ON FINAL LOCATION OF CATALOG FILE---#
        #path = path_to_dir + '/' + names[i]
        path = names[i]
        
        index_str.append(index)
        name_str.append(path)
    
    catalog = Table([index_str, name_str], names = ('INDEX', 'FILENAME'))

    # Create catalog.fits file in directory with the models
    catalog.write('catalog.fits', format = 'fits')
    
    # Move back to original directory, create the catalog.fits file
    os.chdir(start_dir)
    
    return

def orgnaize_PHOENIXv16_atmospheres(path_to_dir):
    """
    Construct the Phoenix Husser+13 atmopsheres for each model. Combines the
    fluxes from the *HiRES.fits files and the wavelengths of the
    WAVE_PHONEIX-ACES-AGSS-COND-2011.fits file.

    path_to_dir is the path to the directory containing all of the downloaded
    files

    Creates new fits files for each atmosphere: phoenix_mm00_<temp>.fits,
    which contains columns for the log g (column header = g#.#). Puts
    atmospheres in new directory phoenixm00
    """
    # Save current directory for return later, move into working dir
    start_dir = os.getcwd()
    os.chdir(path_to_dir)

    # If it doesn't already exist, create the phoenixm00 subdirectory
    if os.path.exists('phoenixm00'):
        pass
    else:
        os.mkdir('phoenixm00')
    
    # Extract wavelength array, make column for later
    wavefile = fits.open('WAVE_PHOENIX-ACES-AGSS-COND-2011.fits')
    wave = wavefile[0].data
    wavefile.close()
    wave_col = Column(wave, name = 'WAVELENGTH')

    # Create temp array for Husser+13 grid (given in paper)
    temp_arr = np.arange(2300, 7001, 100)
    temp_arr = np.append(temp_arr, np.arange(7000, 12001, 200))

    print 'Looping though all temps'
    # For each temp, build file containing the flux for all gravities
    i = 0
    for temp in temp_arr:
        files = glob.glob('lte{0:05d}-*-HiRes.fits'.format(temp))
        # Start the table with the wavelength column
        t = Table()
        t.add_column(wave_col)
        for f in files:
            # Extract the logg out of filename
            tmp = f.split('-')
            logg = tmp[1]
            
            # Extract fluxes from file
            spectrum = fits.open(f)
            flux = spectrum[0].data
            spectrum.close()

            # Make Column object with fluxes, add to table
            col = Column(flux, name = 'g{0:2.1f}'.format(float(logg)))
            t.add_column(col)
            
        # Now, construct final fits file for the given temp
        outname = 'phoenixm00_{0:05d}.fits'.format(temp)
        t.write('phoenixm00/' + outname, format = 'fits', overwrite = True) 
        
        # Progress counter for user
        i += 1
        print 'Done {0:d} of {1:d}'.format(i, len(temp_arr))

    # Return to original directory
    os.chdir(start_dir)
    return

def make_PHOENIXv16_catalog(path_to_dir):
    """
    Makes catalog.fits file for Husser+13 phoenix models. Assumes that
    construct_atmospheres has been run already, and that the models lie
    in subdirectory phoenixm00.

    path_to_directory is the path to the directory with the reformatted
    models (i.e. the output from construct_atmospheres, phoenixm00)
    
    Puts catalog.fits file in directory the user starts in
    """
    # Save starting directory for later, move into working directory
    start_dir = os.getcwd()
    os.chdir(path_to_dir)

    # Collect the filenames. Each is a unique temp with many different log g's
    files = glob.glob('*.fits')

    # Get log g values from the column header of one of the files
    t = Table.read(files[0], format='fits')
    keys = t.keys()
    logg_vals = keys[1:]

    # Create the catalog.fits file, row by row
    index_arr = []
    filename_arr = []
    for i in files:
        # Extract temp from filename
        name = i.split('_')
        temp = float(name[1][:-5])
        for j in logg_vals:
            logg = float(j[1:])
            index = '{0:5.0f},0.0,{1:2.1f}'.format(temp, logg)
            filename = path_to_dir + i + '[' + j + ']'
            # Add row to table
            index_arr.append(index)
            filename_arr.append(filename)

    catalog = Table([index_arr, filename_arr], names=('INDEX', 'FILENAME'))
    
    # Return to starting directory, write catalog
    os.chdir(start_dir)
    catalog.write('catalog.fits', format='fits')
    
    return

def cdbs_PHOENIXv16(path_to_cdbs_dir):
    """
    Put the PHOENIXv16 (Husser+13) fits files into cdbs format. This primarily
    consists of adjusting the flux units from [erg/s/cm^2/cm] to [erg/s/cm^2/A]
    and adding the appropriate keywords to the fits header.

    path_to_cdbs_dir goes from current working directory to phoenixm00 directory
    in cdbs/grids/phoenix_v16. Note that these files have already been organized
    using orgnaize_PHOENIXv16_atmospheres code.
    """
    # Save starting directory for later, move into working directory
    start_dir = os.getcwd()
    os.chdir(path_to_cdbs_dir)

    # Collect the filenames, make necessary changes to each one
    files = glob.glob('*.fits')

    # Need to make brand-new fits tables with data we want.
    counter = 0
    for i in files:
        counter += 1
        # Open file, extract useful info
        hdu = fits.open(i)
        header_0 = hdu[0].header
        header_1 = hdu[1].header
        sci = hdu[1].data

        # Remake fits table from individual columns, multiplying each flux
        # column by 10^-8 for conversion
        # This gets messy due to changing number of columns
        c0 = fits.Column(name='Wavelength', format='D', array=sci.field(0))
        # This particular column only exists for lower temp models
        if counter <= 34:
            c1 = fits.Column(name='g0.0', format='E', array=sci.field(1)*10**-8)
            c2 = fits.Column(name='g0.5', format='E', array=sci.field(2)*10**-8)
            c3 = fits.Column(name='g1.0', format='E', array=sci.field(3)*10**-8)
            c4 = fits.Column(name='g1.5', format='E', array=sci.field(4)*10**-8)
            c5 = fits.Column(name='g2.0', format='E', array=sci.field(5)*10**-8)
            c6 = fits.Column(name='g2.5', format='E', array=sci.field(6)*10**-8)
            c7 = fits.Column(name='g3.0', format='E', array=sci.field(7)*10**-8)
            c8 = fits.Column(name='g3.5', format='E', array=sci.field(8)*10**-8)
            c9 = fits.Column(name='g4.0', format='E', array=sci.field(9)*10**-8)
            c10 = fits.Column(name='g4.5', format='E', array=sci.field(10)*10**-8)
            c11 = fits.Column(name='g5.0', format='E', array=sci.field(11)*10**-8)
            c12 = fits.Column(name='g5.5', format='E', array=sci.field(12)*10**-8)
            c13 = fits.Column(name='g6.0', format='E', array=sci.field(13)*10**-8)
        elif counter <= 37:
            c2 = fits.Column(name='g0.5', format='E', array=sci.field(1)*10**-8)
            c3 = fits.Column(name='g1.0', format='E', array=sci.field(2)*10**-8)
            c4 = fits.Column(name='g1.5', format='E', array=sci.field(3)*10**-8)
            c5 = fits.Column(name='g2.0', format='E', array=sci.field(4)*10**-8)
            c6 = fits.Column(name='g2.5', format='E', array=sci.field(5)*10**-8)
            c7 = fits.Column(name='g3.0', format='E', array=sci.field(6)*10**-8)
            c8 = fits.Column(name='g3.5', format='E', array=sci.field(7)*10**-8)
            c9 = fits.Column(name='g4.0', format='E', array=sci.field(8)*10**-8)
            c10 = fits.Column(name='g4.5', format='E', array=sci.field(9)*10**-8)
            c11 = fits.Column(name='g5.0', format='E', array=sci.field(10)*10**-8)
            c12 = fits.Column(name='g5.5', format='E', array=sci.field(11)*10**-8)
            c13 = fits.Column(name='g6.0', format='E', array=sci.field(12)*10**-8)
        elif counter <= 54:
            c3 = fits.Column(name='g1.0', format='E', array=sci.field(1)*10**-8)
            c4 = fits.Column(name='g1.5', format='E', array=sci.field(2)*10**-8)
            c5 = fits.Column(name='g2.0', format='E', array=sci.field(3)*10**-8)
            c6 = fits.Column(name='g2.5', format='E', array=sci.field(4)*10**-8)
            c7 = fits.Column(name='g3.0', format='E', array=sci.field(5)*10**-8)
            c8 = fits.Column(name='g3.5', format='E', array=sci.field(6)*10**-8)
            c9 = fits.Column(name='g4.0', format='E', array=sci.field(7)*10**-8)
            c10 = fits.Column(name='g4.5', format='E', array=sci.field(8)*10**-8)
            c11 = fits.Column(name='g5.0', format='E', array=sci.field(9)*10**-8)
            c12 = fits.Column(name='g5.5', format='E', array=sci.field(10)*10**-8)
            c13 = fits.Column(name='g6.0', format='E', array=sci.field(11)*10**-8)
        elif counter <= 59:
            c4 = fits.Column(name='g1.5', format='E', array=sci.field(1)*10**-8)
            c5 = fits.Column(name='g2.0', format='E', array=sci.field(2)*10**-8)
            c6 = fits.Column(name='g2.5', format='E', array=sci.field(3)*10**-8)
            c7 = fits.Column(name='g3.0', format='E', array=sci.field(4)*10**-8)
            c8 = fits.Column(name='g3.5', format='E', array=sci.field(5)*10**-8)
            c9 = fits.Column(name='g4.0', format='E', array=sci.field(6)*10**-8)
            c10 = fits.Column(name='g4.5', format='E', array=sci.field(7)*10**-8)
            c11 = fits.Column(name='g5.0', format='E', array=sci.field(8)*10**-8)
            c12 = fits.Column(name='g5.5', format='E', array=sci.field(9)*10**-8)
            c13 = fits.Column(name='g6.0', format='E', array=sci.field(10)*10**-8)
        else:
            c5 = fits.Column(name='g2.0', format='E', array=sci.field(1)*10**-8)
            c6 = fits.Column(name='g2.5', format='E', array=sci.field(2)*10**-8)
            c7 = fits.Column(name='g3.0', format='E', array=sci.field(3)*10**-8)
            c8 = fits.Column(name='g3.5', format='E', array=sci.field(4)*10**-8)
            c9 = fits.Column(name='g4.0', format='E', array=sci.field(5)*10**-8)
            c10 = fits.Column(name='g4.5', format='E', array=sci.field(6)*10**-8)
            c11 = fits.Column(name='g5.0', format='E', array=sci.field(7)*10**-8)
            c12 = fits.Column(name='g5.5', format='E', array=sci.field(8)*10**-8)
            c13 = fits.Column(name='g6.0', format='E', array=sci.field(9)*10**-8)
            
            
        if counter <= 35:
            cols = fits.ColDefs([c0,c1,c2,c3,c4,c5,c6,c7,c8,c9,c10,c11,c12,c13])
        elif counter <= 37:
            cols = fits.ColDefs([c0,c2,c3,c4,c5,c6,c7,c8,c9,c10,c11,c12,c13])
        elif counter <= 54:
            cols = fits.ColDefs([c0,c3,c4,c5,c6,c7,c8,c9,c10,c11,c12,c13])
        elif counter <= 59:
            cols = fits.ColDefs([c0,c4,c5,c6,c7,c8,c9,c10,c11,c12,c13])
        else:
            cols = fits.ColDefs([c0,c5,c6,c7,c8,c9,c10,c11,c12,c13])
        tbhdu = fits.BinTableHDU.from_columns(cols)

        # Copying over the older headers, adding unit keywords
        prihdu = fits.PrimaryHDU(header=header_0)
        tbhdu.header['TUNIT1'] = 'ANGSTROM'
        tbhdu.header['TUNIT2'] = 'FLAM'
        tbhdu.header['TUNIT3'] = 'FLAM'
        tbhdu.header['TUNIT4'] = 'FLAM'
        tbhdu.header['TUNIT5'] = 'FLAM'
        tbhdu.header['TUNIT6'] = 'FLAM'
        tbhdu.header['TUNIT7'] = 'FLAM'
        tbhdu.header['TUNIT8'] = 'FLAM'
        tbhdu.header['TUNIT9'] = 'FLAM'
        tbhdu.header['TUNIT10'] = 'FLAM'
        tbhdu.header['TUNIT11'] = 'FLAM'
        tbhdu.header['TUNIT12'] = 'FLAM'
        tbhdu.header['TUNIT13'] = 'FLAM'
        tbhdu.header['TUNIT14'] = 'FLAM'
    
        finalhdu = fits.HDUList([prihdu, tbhdu])

        finalhdu.writeto(i, clobber=True)

        hdu.close()
        print 'Done {0:2.0f} of {1:2.0f}'.format(counter, len(files))

    return


def rebin_phoenixV16(cdbs_path):
    """
    Rebin phoenixV16 models to atlas ck04 resolution; this makes
    spectrophotometry MUST faster

    makes new directory in cdbs/grid: phoenix_v16_rebin

    cdbs_path: path to cdbs directory
    """
    # Get an atlas ck04 model, we will use this to set wavelength grid
    sp_atlas = get_castelli_atmosphere()

    # Open a fits table for an existing phoenix model; we will steal the header
    tmp = cdbs_path+'/grid/phoenix_v16/phoenixm00/phoenixm00_02400.fits'
    phoenix_hdu = fits.open(tmp)
    header0 = phoenix_hdu[0].header

    # Create cdbs/grid directory for rebinned models
    path = cdbs_path+'/grid/phoenix_v16_rebin/'
    if not os.path.exists(path):
        os.mkdir(path)
        os.mkdir(path+'phoenixm00')
        
    # Want to go through all phoenixV16 models and rebin. See get_phoenix_v16
    # code comment for ranges.
    t1 = np.arange(2300, 7000+1, 100)
    t2 = np.arange(7000,12000+1, 200)
    temp_arr = np.append(t1, t2)
    grav_arr = np.arange(2.0, 6.0+0.1, 0.5)

    count=0
    for t in temp_arr:
        count += 1
        outfile = 'phoenixm00_{0:05.0f}.fits'.format(t)
        # Loop through gravities
        flux_arr = []
        for g in grav_arr:
            sp_phoenix = get_phoenixv16_atmosphere(temperature=t, gravity=g)
            flux_rebin = atmos_comp.rebin_spec(sp_phoenix.wave, sp_phoenix.flux,
                                               sp_atlas.wave)
            flux_arr.append(flux_rebin)

        # Build the columns fo the new cdbs table
        c0 = fits.Column(name='Wavelength', format='D', array=sp_atlas.wave)
        c1 = fits.Column(name='g2.0', format='E', array=flux_arr[0])
        c2 = fits.Column(name='g2.5', format='E', array=flux_arr[1])
        c3 = fits.Column(name='g3.0', format='E', array=flux_arr[2])
        c4 = fits.Column(name='g3.5', format='E', array=flux_arr[3])
        c5 = fits.Column(name='g4.0', format='E', array=flux_arr[4])
        c6 = fits.Column(name='g4.5', format='E', array=flux_arr[5])
        c7 = fits.Column(name='g5.0', format='E', array=flux_arr[6])
        c8 = fits.Column(name='g5.5', format='E', array=flux_arr[7])
        c9 = fits.Column(name='g6.0', format='E', array=flux_arr[8])

        cols = fits.ColDefs([c0,c1,c2,c3,c4,c5,c6,c7,c8,c9])
        tbhdu = fits.BinTableHDU.from_columns(cols)
        prihdu = fits.PrimaryHDU(header=header0)
        # Gotta add a keyword to the table hdu
        tbhdu.header['TUNIT1'] = 'ANGSTROM'
        tbhdu.header['TUNIT2'] = 'FLAM'
        tbhdu.header['TUNIT3'] = 'FLAM'
        tbhdu.header['TUNIT4'] = 'FLAM'
        tbhdu.header['TUNIT5'] = 'FLAM'
        tbhdu.header['TUNIT6'] = 'FLAM'
        tbhdu.header['TUNIT7'] = 'FLAM'
        tbhdu.header['TUNIT8'] = 'FLAM'
        tbhdu.header['TUNIT9'] = 'FLAM'
        tbhdu.header['TUNIT10'] = 'FLAM'

        # Write hdu
        finalhdu = fits.HDUList([prihdu, tbhdu])
        finalhdu.writeto(path+'phoenixm00/'+outfile, clobber=True)

        print 'Done file {0:1f} of {1:1f}'.format(count, len(temp_arr))           

    return