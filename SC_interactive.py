''' 
Sensitivity curve generator for GW detectors.
Gergely Dálya, 2020.
dalyag@caesar.elte.hu

Use the ``bokeh serve`` command to run the interactive simulation by executing:
    bokeh serve sliders.py
at your command prompt. Then navigate to the URL
    http://localhost:5006/sliders
in your browser.
'''
import numpy as np

from bokeh.io import curdoc
from bokeh.layouts import row, column
from bokeh.palettes import Pastel1_4, Dark2_5
from bokeh.models import ColumnDataSource, CustomJS
from bokeh.models.widgets import Slider, CheckboxGroup, Toggle
from bokeh.plotting import figure

import sys
#sys.path.insert(1, '/home/dalyag/Documents/Research/GW/High-frequency/gwinc/pygwinc')
sys.path.insert(1, '/home/dalyag/Documents/Research/GW/High-frequency/gwinc/pygwinc')
import gwinc
import os
import glob

# Set up data

freq = np.logspace(1, 4, 10000)

#Budget_aL, ifo_aL, freq_, plot_style = gwinc.load_ifo('aLIGO')
#ifo_aL = gwinc.precompIFO(freq, ifo_aL)
#traces_aL = Budget_aL(freq, ifo=ifo_aL).calc_trace()
Budget_aL = gwinc.load_budget('aLIGO')
traces_aL = Budget_aL(freq).run()

#Budget, ifo, freq_, plot_style = gwinc.load_ifo('Eotvos')
#ifo = gwinc.precompIFO(freq, ifo)
#traces = Budget(freq, ifo=ifo).calc_trace()
Budget = gwinc.load_budget('UjDetektor')
traces = Budget(freq).run()

# ifodir = "/home/dalyag/Documents/Research/GW/High-frequency/gwinc/pygwinc/gwinc/ifo/Eotvos"
ifodir = '/home/dalyag/Documents/Research/GW/High-frequency/gwinc/pygwinc/gwinc/ifo/UjDetektor'

x = np.logspace(1, 4, 10000)
y_tot = np.sqrt(traces["Total"][0])
y_qua = np.sqrt(traces["QuantumVacuum"][0])
y_sei = np.sqrt(traces["Seismic"][0])
y_new = np.sqrt(traces["Newtonian"][0])
y_sth = np.sqrt(traces["SuspensionThermal"][0])
y_cbr = np.sqrt(traces["CoatingBrownian"][0])
y_cto = np.sqrt(traces["CoatingThermoOptic"][0])
y_sbr = np.sqrt(traces["SubstrateBrownian"][0])
y_ste = np.sqrt(traces["SubstrateThermoElastic"][0])
y_exg = np.sqrt(traces["ExcessGas"][0])
y_aL = np.sqrt(traces_aL["Total"][0])

source = ColumnDataSource(data=dict(x=x, y_tot=y_tot, y_qua=y_qua, y_sei=y_sei, y_new=y_new, y_sth=y_sth, y_cbr=y_cbr, y_cto=y_cto, y_sbr=y_sbr, y_ste=y_ste, y_exg=y_exg, y_aL=y_aL))


# JS code for checkboxes

code = """
    if (checkbox.active.indexOf(0) > -1) {
        l_qua.visible = true
    } else {
        l_qua.visible = false
    }
    if (checkbox.active.indexOf(1) > -1) {
        l_sei.visible = true
    } else {
        l_sei.visible = false
    }
    if (checkbox.active.indexOf(2) > -1) {
        l_new.visible = true
    } else {
        l_new.visible = false
    }
    if (checkbox.active.indexOf(3) > -1) {
        l_sth.visible = true
    } else {
        l_sth.visible = false
    }
    if (checkbox.active.indexOf(4) > -1) {
        l_cbr.visible = true
    } else {
        l_cbr.visible = false
    }
    if (checkbox.active.indexOf(5) > -1) {
        l_cto.visible = true
    } else {
        l_cto.visible = false
    }
    if (checkbox.active.indexOf(6) > -1) {
        l_sbr.visible = true
    } else {
        l_sbr.visible = false
    }
    if (checkbox.active.indexOf(7) > -1) {
        l_ste.visible = true
    } else {
        l_ste.visible = false
    }
    if (checkbox.active.indexOf(8) > -1) {
        l_exg.visible = true
    } else {
        l_exg.visible = false
    }
"""

code2 = """
    if (l_tot.visible = true) {
        l_tot.visible = false
    } else {
        l_tot.visible = true
    }
"""

# Set up plot
plot = figure(plot_height=600, plot_width=800, title="GW IFO noise budget",
              tools="crosshair,pan,reset,save,wheel_zoom",
               x_range=(10, 10000), y_range=(1e-25, 8e-21),
               x_axis_type="log", y_axis_type="log")
              #x_range=[10, 1000], y_range=[1e-45, 1e-40])
              
plot.xaxis.axis_label = 'Frequency (Hz)'
plot.yaxis.axis_label = 'Strain (Hz^-1/2)'

l_tot = plot.line("x", "y_tot", source=source, line_width=3, color="black", legend="Total noise")
l_aL = plot.line("x", "y_aL", source=source, line_width=3, color="black", line_alpha=0.6, line_dash='dashed', legend="aLIGO")
l_qua = plot.line("x", "y_qua", source=source, line_width=2, color=Dark2_5[0], line_alpha=0.6, legend="Quantum")
l_sei = plot.line("x", "y_sei", source=source, line_width=2, color=Dark2_5[1], line_alpha=0.6, legend="Seismic")
l_new = plot.line("x", "y_new", source=source, line_width=2, color=Dark2_5[2], line_alpha=0.6, legend="Newtonian")
l_sth = plot.line("x", "y_sth", source=source, line_width=2, color=Dark2_5[3], line_alpha=0.6, legend="Suspension thermal")
l_cbr = plot.line("x", "y_cbr", source=source, line_width=2, color=Dark2_5[4], line_alpha=0.6, legend="Coating Brownian")

l_cto = plot.line("x", "y_cto", source=source, line_width=2, color=Pastel1_4[0], line_alpha=1, legend="Coating thermo-optic", line_dash='dotted', visible=False)
l_sbr = plot.line("x", "y_sbr", source=source, line_width=2, color=Pastel1_4[1], line_alpha=1, legend="Substrate Brownian", line_dash='dotted', visible=False)
l_ste = plot.line("x", "y_ste", source=source, line_width=2, color=Pastel1_4[2], line_alpha=1, legend="Substrate thermo-elastic", line_dash='dotted', visible=False)
l_exg = plot.line("x", "y_exg", source=source, line_width=2, color=Pastel1_4[3], line_alpha=1, legend="Excess gas", line_dash='dotted', visible=False)

# Set up widgets
armlength = Slider(title="Arm length (m)", value=4000, start=100, end=5000, step=100, callback_policy="mouseup")
wavelength = Slider(title="Laser wavelength (micrometer)", value=1.064, start=0.1, end=10, step=0.5, callback_policy="mouseup")
power = Slider(title="Laser power (W)", value=125, start=100, end=2000, step=100, callback_policy="mouseup")
trans = Slider(title="ITM transmittance", value=0.014, start=0, end=1, step=0.05, callback_policy="mouseup")
sqzamp = Slider(title="Squeezing amplitude (dB)", value=12, start=0, end=100, step=5, callback_policy="mouseup")
sqzang = Slider(title="Squeeze phase (rad)", value=0.00, start=-6.28, end=6.28, step=0.5, callback_policy="mouseup")
sqzlength = Slider(title="Squeezing cavity length (m)", value=300, start=0, end=1000, step=100, callback_policy="mouseup")
sqzdet = Slider(title="Detuning (Hz)", value=-45.78, start=-100.78, end=100.78, step=5, callback_policy="mouseup")

callback = CustomJS(code=code, args={})        

checkbox = CheckboxGroup(
        labels=["Quantum", "Seismic", "Newtonian", "Suspension thermal", "Coating Brownian", "Coating thermo-optic", "Substrate Brownian", "Substrate thermo-elastic", "Excess gas"], active=[0, 1, 2, 3, 4], callback=callback)        
callback.args = dict(l_qua=l_qua, l_sei=l_sei, l_new=l_new, l_sth=l_sth, l_cbr=l_cbr, l_cto=l_cto, l_sbr=l_sbr, l_ste=l_ste, l_exg=l_exg, checkbox=checkbox)


def totalnoise_handler(self):
    if (l_tot.visible == True):
        l_tot.visible = False
    else:
        l_tot.visible = True
        
def totalnoise_handler_aL(self):
    if (l_aL.visible == True):
        l_aL.visible = False
    else:
        l_aL.visible = True
        
def save(self):
    filename = 'sensitivity_curve_' + str(armlength.value) + '_' + str(wavelength.value) + '_' + str(power.value) + '_' + str(trans.value) + '_' + str(sqzamp.value) + '_' + str(sqzang.value) + '_' + str(sqzlength.value) + '_' + str(sqzdet.value)
    with open(filename, 'a') as f:
        for i, j in zip(np.logspace(1, 4, 10000), np.sqrt(traces["Total"][0])):
            #print(i, j)
            f.write('%f %e\n' % (i, j))

        
toggle = Toggle(label="Total noise", button_type="warning")
toggle.on_click(totalnoise_handler)

toggle_aL = Toggle(label="aLIGO", button_type="warning")
toggle_aL.on_click(totalnoise_handler_aL)

toggle_save = Toggle(label="Save sensitivity curve", button_type="success")
toggle_save.on_click(save)

#if (toggle=active)

# Set up callbacks
def update_data(attrname, old, new):

    # Get the current slider values
    L = armlength.value
    lam = wavelength.value
    P = power.value
    t = trans.value
    sa = sqzamp.value
    sphi = sqzang.value
    sl = sqzlength.value
    sd = sqzdet.value

    # Generate the new curve
    x = np.logspace(1, 4, 10000)
    os.chdir(ifodir)
    os.system("sed -i '0,/Length/{s/Length: [0-9]*/Length: %d/}' ifo.yaml" % L)
    os.system("sed -i '0,/Wavelength/{s/Wavelength: [0-9]*\.[0-9]*/Wavelength: %f/}' ifo.yaml" % lam)
    os.system("sed -i '0,/Power/{s/Power: [0-9]*/Power: %d/}' ifo.yaml" % P)
    os.system("sed -i '252s/Transmittance: [0-9]\.[0-9]*/Transmittance: %f/' ifo.yaml" % t)
    os.system("sed -i '0,/AmplitudedB/{s/AmplitudedB: [0-9]*/AmplitudedB: %d/}' ifo.yaml" % sa)
    os.system("sed -i '283s/SQZAngle: [0-9]\.[0-9]*/SQZAngle: %f/' ifo.yaml" % sphi)
    os.system("sed -i '288s/L: [0-9]*/L: %d/' ifo.yaml" % sl)
    os.system("sed -i '292s/fdetune: -*[0-9]*\.[0-9]*/fdetune: %f/' ifo.yaml" % sd)
    
    #Budget, ifo, freq_, plot_style = gwinc.load_ifo('Eotvos')
    #ifo = gwinc.precompIFO(freq, ifo)
    #traces = Budget(freq, ifo=ifo).calc_trace()
    Budget = gwinc.load_budget('UjDetektor')
    traces = Budget(freq).run()
    y_tot = np.sqrt(traces["Total"][0])
    y_qua = np.sqrt(traces["QuantumVacuum"][0])
    y_sei = np.sqrt(traces["Seismic"][0])
    y_new = np.sqrt(traces["Newtonian"][0])
    y_sth = np.sqrt(traces["SuspensionThermal"][0])
    y_cbr = np.sqrt(traces["CoatingBrownian"][0])
    y_cto = np.sqrt(traces["CoatingThermoOptic"][0])
    y_sbr = np.sqrt(traces["SubstrateBrownian"][0])
    y_ste = np.sqrt(traces["SubstrateThermoElastic"][0])
    y_exg = np.sqrt(traces["ExcessGas"][0])

    source.data = dict(x=x, y_tot=y_tot, y_qua=y_qua, y_sei=y_sei, y_new=y_new, y_sth=y_sth, y_cbr=y_cbr, y_cto=y_cto, y_sbr=y_sbr, y_ste=y_ste, y_exg=y_exg, y_aL=y_aL)

for w in [armlength, wavelength, power, trans, sqzamp, sqzang, sqzlength, sqzdet]:
    w.on_change('value', update_data)


# Set up layouts and add to document
inputs = column(armlength, wavelength, power, trans, sqzamp, sqzang, sqzlength, sqzdet, toggle, toggle_aL, toggle_save, checkbox)

curdoc().add_root(row(inputs, plot, width=800))
curdoc().title = "GW IFO noise budget"
