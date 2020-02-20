''' 
Sensitivity curve generator for GW detectors.
Gergely Dálya, 2020.
dalyag@caesar.elte.hu
'''
import numpy as np

import sys
import argparse
import os
import glob


parser = argparse.ArgumentParser(description='GW detector sensitivity curve generator')
parser.add_argument('-g','--pygwinc', type = os.path.abspath,
                    help='absolute path of your pygwinc directory, e.g. /home/.../gwinc/pygwinc')
parser.add_argument('-i','--ifo', type = str,
                    help='name of your detector')
parser.add_argument('-l','--length', type = int,
                    help='arm length of your detector [m], default value: 4000',
                    default=4000)
parser.add_argument('-w','--wavelength', type = float,
                    help='laser wavelength [micrometer], default value: 1.064',
                    default=1.064)
parser.add_argument('-p','--power', type = int,
                    help='laser power [W], default value: 125',
                    default=125)
parser.add_argument('-t','--transmittance', type = float,
                    help='ITM transmittance, default value: 0.014',
                    default=0.014)
                    
parser.add_argument('--f0', type = float,
                    help='start frequency [Hz], default value: 1',
                    default=1)
parser.add_argument('--f1', type = float,
                    help='end frequency [Hz], default value: 10000',
                    default=10000)
parser.add_argument('-n','--numberofbins', type = int,
                    help='number of frequency bins, default value: 10000',
                    default=10000)
parser.add_argument('-L', '--linlog', type = str,
                    help='linear or logarithmic frequency spacing? \
                     Possible values: lin, log. Default value: lin',
                    default='lin')
                    
parser.add_argument('-o', '--outputdir', type=os.path.abspath,
                    default=os.curdir,
                    help='output directory for analysis, default: %(default)s')
args = parser.parse_args()


pygwincpath = args.pygwinc
ifoname = args.ifo
length = args.length
wavelength = args.wavelength
power = args.power
trans = args.transmittance
f0 = args.f0
f1 = args.f1
numberofbins = args.numberofbins
linlog = args.linlog
outputdir = args.outputdir

#sys.path.insert(1, '/home/dalyag/Documents/Research/GW/High-frequency/gwinc/pygwinc')
sys.path.insert(1, '%s' % pygwincpath)
import gwinc

if linlog not in ["lin", "log"]:
    raise ValueError("Please specify either lin or log for frequency spacing.")

# Set up data

if linlog == "log":
    freq = np.logspace(f0, np.log10(f1), numberofbins)
if linlog == "lin":
    freq = np.linspace(f0, f1, numberofbins)

# Generate the gwinc directory for the new detector
if not os.path.isdir('%s/gwinc/ifo/%s' % (pygwincpath, ifoname)):
    os.makedirs('%s/gwinc/ifo/%s' % (pygwincpath, ifoname))

os.system('cp -r %s/gwinc/ifo/aLIGO/* %s/gwinc/ifo/%s' % (pygwincpath, pygwincpath, ifoname))
os.system('sed -i "s@^class.*@class %s(nb.Budget):@" %s/gwinc/ifo/%s/__init__.py' % (ifoname, pygwincpath, ifoname))
os.system('sed -i "s@Advanced LIGO@%s@" %s/gwinc/ifo/%s/__init__.py' % (ifoname, pygwincpath, ifoname))

# Change the parameters in the ifo.yaml file to the user-specified ones
os.chdir('%s/gwinc/ifo/%s' % (pygwincpath, ifoname))
os.system("sed -i '0,/Length/{s/Length: [0-9]*/Length: %d/}' ifo.yaml" % length)
os.system("sed -i '0,/Wavelength/{s/Wavelength: [0-9]*\.[0-9]*/Wavelength: %f/}' ifo.yaml" % wavelength)
os.system("sed -i '0,/Power/{s/Power: [0-9]*/Power: %d/}' ifo.yaml" % power)
os.system("sed -i 's/Transmittance: [0-9]\.[0-9]* #ITM/Transmittance: %f #ITM/' ifo.yaml" % trans)


Budget, ifo, freq_, plot_style = gwinc.load_ifo(ifoname)
ifo = gwinc.precompIFO(freq, ifo)
traces = Budget(freq, ifo=ifo).calc_trace()

# Save the spectrum
os.chdir(outputdir)
filename = 'sensitivity_curve_' + str(length) + '_' + str(wavelength) + '_' + str(power) + '_' + str(trans)
with open(filename, 'a') as f:
    for i, j in zip(freq, np.sqrt(traces["Total"][0])):
        f.write('%f %e\n' % (i, j))

