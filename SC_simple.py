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

sqztext = "\n\
## Squeezer Parameters------------------------------------------------------\n\
# Define the squeezing you want:\n\
#   None: ignore the squeezer settings\n\
#   Freq Independent: nothing special (no filter cavities)\n\
#   Freq Dependent = applies the specified filter cavities\n\
#   Optimal = find the best squeeze angle, assuming no output filtering\n\
#   OptimalOptimal = optimal squeeze angle, assuming optimal readout phase\n\
Squeezer:\n\
  Type: 'Freq Dependent'\n\
  AmplitudedB: 10                 # SQZ amplitude [dB]\n\
  InjectionLoss: 0.05             # power loss to sqz\n\
  SQZAngle: 0.000000              # SQZ phase [radians]\n\
  LOAngleRMS: 30e-3               # quadrature noise [radians]\n\
\n\
  # Parameters for frequency dependent squeezing\n\
  FilterCavity:\n\
    L: 300                        # cavity length\n\
    Te: 1e-6                      # end mirror transmission\n\
    Lrt: 60e-6                    # round-trip loss in the cavity\n\
    Rot: 0.000000                 # phase rotation after cavity\n\
    fdetune: -45.000000           # detuning [Hz]\n\
    Ti: 1.2e-3                    # input mirror transmission [Power]"
    



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
parser.add_argument('--sa', type = int,
                    help='squeezing amplitude [dB], default value: 10',
                    default=10)
parser.add_argument('--sp', type = float,
                    help='squeezing phase [rad], default value: 0',
                    default=0.0)
parser.add_argument('--sl', type = int,
                    help='squeezing cavity length [m], default value: 300',
                    default=300)
parser.add_argument('--sd', type = float,
                    help='squeezer detuning [Hz], default value: -45',
                    default=-45.0)
                                       
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
sqzamp = args.sa
sqzang = args.sp
sqzlength = args.sl
sqzdet = args.sd

f0 = args.f0
f1 = args.f1
numberofbins = args.numberofbins
linlog = args.linlog
outputdir = args.outputdir

# If you don't have this IFO in the list of IFOS at __init__.py, add it
if os.system("grep -q %s %s/gwinc/ifo/__init__.py" % (ifoname, pygwincpath)) != 0:
    os.system('sed -i "s@^]@\\t\'%s\',\\n]@" %s/gwinc/ifo/__init__.py' % (ifoname, pygwincpath))

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

# Generate the gwinc directory for the new detector and add the squeezer
if not os.path.isdir('%s/gwinc/ifo/%s' % (pygwincpath, ifoname)):
    os.makedirs('%s/gwinc/ifo/%s' % (pygwincpath, ifoname))
    os.system('cp -r %s/gwinc/ifo/aLIGO/* %s/gwinc/ifo/%s' % (pygwincpath, pygwincpath, ifoname))
    yamlname = pygwincpath + "/gwinc/ifo/" + ifoname + "/ifo.yaml"
    with open(yamlname, "a") as yamlfile:
        yamlfile.write(sqztext)

os.system('sed -i "s@^class.*@class %s(nb.Budget):@" %s/gwinc/ifo/%s/__init__.py' % (ifoname, pygwincpath, ifoname))
os.system('sed -i "s@Advanced LIGO@%s@" %s/gwinc/ifo/%s/__init__.py' % (ifoname, pygwincpath, ifoname))

# Change the parameters in the ifo.yaml file to the user-specified ones
os.chdir('%s/gwinc/ifo/%s' % (pygwincpath, ifoname))
os.system("sed -i '0,/Length/{s/Length: [0-9]*/Length: %d/}' ifo.yaml" % length)
os.system("sed -i '0,/Wavelength/{s/Wavelength: [0-9]*\.[0-9]*/Wavelength: %f/}' ifo.yaml" % wavelength)
os.system("sed -i '0,/Power/{s/Power: [0-9]*/Power: %d/}' ifo.yaml" % power)
os.system("sed -i '252s/Transmittance: [0-9]\.[0-9]*/Transmittance: %f/' ifo.yaml" % trans)
os.system("sed -i '0,/AmplitudedB/{s/AmplitudedB: [0-9]*/AmplitudedB: %d/}' ifo.yaml" % sqzamp)
os.system("sed -i '283s/SQZAngle: [0-9]\.[0-9]*/SQZAngle: %f/' ifo.yaml" % sqzang)
os.system("sed -i '288s/L: [0-9]*/L: %d/' ifo.yaml" % sqzlength)
os.system("sed -i '292s/fdetune: -*[0-9]*\.[0-9]*/fdetune: %f/' ifo.yaml" % sqzdet)


#Budget, ifo, freq_, plot_style = gwinc.load_ifo(ifoname)
#ifo = gwinc.precompIFO(freq, ifo)
#traces = Budget(freq, ifo=ifo).calc_trace()

Budget = gwinc.load_budget(ifoname)
traces = Budget(freq).run()


# Save the spectrum
os.chdir(outputdir)
filename = 'sensitivity_curve_' + str(length) + '_' + str(wavelength) + '_' + str(power) + '_' + str(trans) + '_' + str(sqzamp) + '_' + str(sqzang) + '_' + str(sqzlength) + '_' + str(sqzdet)
with open(filename, 'a') as f:
    for i, j in zip(freq, np.sqrt(traces["Total"][0])):
        f.write('%f %e\n' % (i, j))

