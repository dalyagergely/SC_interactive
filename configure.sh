#!/bin/bash

sqztext="
## Squeezer Parameters------------------------------------------------------ 
# Define the squeezing you want: 
#   None: ignore the squeezer settings
#   Freq Independent: nothing special (no filter cavities)
#   Freq Dependent = applies the specified filter cavities
#   Optimal = find the best squeeze angle, assuming no output filtering
#   OptimalOptimal = optimal squeeze angle, assuming optimal readout phase
Squeezer:
  Type: 'Freq Dependent'
  AmplitudedB: 10                 # SQZ amplitude [dB]
  InjectionLoss: 0.05             # power loss to sqz
  SQZAngle: 0.000000              # SQZ phase [radians]
  LOAngleRMS: 30e-3               # quadrature noise [radians]

  # Parameters for frequency dependent squeezing
  FilterCavity:
    L: 300                        # cavity length
    Te: 1e-6                      # end mirror transmission
    Lrt: 60e-6                    # round-trip loss in the cavity
    Rot: 0.000000                 # phase rotation after cavity
    fdetune: -45.780000           # detuning [Hz]
    Ti: 1.2e-3                    # input mirror transmission [Power]"



echo "Configuration file for SC_interactive.py"
echo "You only have to do this process once for a new detector"
echo "Please enter where is your pygwinc installation located"
echo "e.g. /home/.../gwinc/pygwinc"
echo ""

read pygwinc

echo "Please enter the name of your new detector"

read name


if grep -q $name $pygwinc/gwinc/ifo/__init__.py
then
    echo "Detector already exists."
else
    cp -r $pygwinc/gwinc/ifo/aLIGO $pygwinc/gwinc/ifo/$name
    sed -i "s@^]@\\t\'$name\',\\n]@" $pygwinc/gwinc/ifo/__init__.py
    echo "${sqztext}" >> $pygwinc/gwinc/ifo/$name/ifo.yaml
fi


sed -i "s@^sys.path.insert(.*)@sys.path.insert(1, '$pygwinc')@" SC_interactive.py
sed -i "s@^ifodir = .*@ifodir = '$pygwinc/gwinc/ifo/$name'@" SC_interactive.py
sed -i "s@Budget = .*@Budget = gwinc.load_budget('$name')@" SC_interactive.py

sed -i "s@^class.*@class $name(nb.Budget):@" $pygwinc/gwinc/ifo/$name/__init__.py
sed -i "s@Advanced LIGO@$name@" $pygwinc/gwinc/ifo/$name/__init__.py


echo "Done!"

