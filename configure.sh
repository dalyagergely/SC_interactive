#!/bin/bash

echo "Configuration file for SC_interactive.py"
echo "You only have to do this process once for a new detector"
echo "Please enter where is your pygwinc installation located"
echo "e.g. /home/.../gwinc/pygwinc"
echo ""

read pygwinc

echo "Please enter the name of your new detector"

read name

cp -r $pygwinc/gwinc/ifo/aLIGO $pygwinc/gwinc/ifo/$name


sed -i "s@^sys.path.insert(.*)@sys.path.insert(1, '$pygwinc')@" SC_interactive.py
sed -i "s@^ifodir = .*@ifodir = '$pygwinc/gwinc/ifo/$name'@" SC_interactive.py
sed -i "s@Budget, ifo,.*@Budget, ifo, freq_, plot_style = gwinc.load_ifo('$name')@" SC_interactive.py

sed -i "s@^class.*@class $name(nb.Budget):@" $pygwinc/gwinc/ifo/$name/__init__.py
sed -i "s@Advanced LIGO@$name@" $pygwinc/gwinc/ifo/$name/__init__.py

sed -i "s@^]@\\t\'$name\',\\n]@" $pygwinc/gwinc/ifo/__init__.py"

echo "Done!"
