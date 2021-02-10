#
# @ 2021. TU Dortmund University,
# Institute of Energy Systems, Energy Efficiency and Energy Economics,
# Research group Distribution grid planning and operation
#
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import pickle
import os

soc = ctrl.Antecedent(np.arange(0, 101, 1), 'SOC')
next_dist = ctrl.Antecedent(np.arange(0, 301, 1), 'Entfernung nächster Fahrt')
state = ctrl.Antecedent(np.arange(1, 4, 1), 'Zustand')
stay_dur = ctrl.Antecedent(np.arange(0, 1440, 1), 'Aufenthaltsdauer')

prob = ctrl.Consequent(np.arange(0, 101, 1), 'Ladewahrscheinlichkeit')

# Membership functions
# SOC
soc["gering"] = fuzz.trimf(soc.universe, [0, 0, 50])
soc["mittel"] = fuzz.trimf(soc.universe, [0, 50, 100])
soc["hoch"] = fuzz.trimf(soc.universe, [50, 100, 100])

# Entfernung nachfolgender Strecke
next_dist["gering"] = fuzz.trimf(next_dist.universe, [0, 0, 20])
next_dist["mittel"] = fuzz.trimf(next_dist.universe, [10, 30, 50])
next_dist["hoch"] = fuzz.trapmf(next_dist.universe, [30, 50, 300, 300])

# Aufenthaltsdauer
stay_dur["sehr gering"] = fuzz.trapmf(stay_dur.universe, [0, 0, 15, 30])
stay_dur["gering"] = fuzz.trimf(stay_dur.universe, [0, 0, 60])
stay_dur["mittel"] = fuzz.trimf(stay_dur.universe, [0, 60, 120])
stay_dur["hoch"] = fuzz.trapmf(stay_dur.universe, [60, 120, 1440, 1440])

# aktueller Aufenthaltsort
state["zuhause"] = fuzz.trimf(state.universe, [0, 1, 2])
state["arbeit"] = fuzz.trimf(state.universe, [1, 2, 3])
state["sonstwo"] = fuzz.trimf(state.universe, [2, 3, 3,])

# Ladewahrscheinlichkeit
prob["sehr gering"] = fuzz.trimf(prob.universe, [0, 0, 10])
prob["gering"] = fuzz.trimf(prob.universe, [0, 10, 20])
prob["mittel"] = fuzz.trimf(prob.universe, [20, 50, 80])
prob["hoch"] = fuzz.trapmf(prob.universe, [50, 80, 90, 100])
prob["sehr hoch"] = fuzz.trimf(prob.universe, [90, 100, 100])

# Fuzzy Rules
rule1 = ctrl.Rule(soc['gering'], prob['sehr hoch'])
rule2 = ctrl.Rule(soc['mittel'] & next_dist['hoch'], prob['hoch'])
rule3 = ctrl.Rule(soc['hoch'] & stay_dur['gering'], prob['sehr gering'])
rule4 = ctrl.Rule(soc['mittel'] | stay_dur['mittel'], prob['mittel'])
rule5 = ctrl.Rule(state['zuhause'], prob['sehr hoch'])
rule6 = ctrl.Rule(state['arbeit'], prob['mittel'])
rule7 = ctrl.Rule(state['sonstwo'], prob['sehr gering'])
rule8 = ctrl.Rule(stay_dur['sehr gering'], prob['sehr gering'])

# System mit Regeln initialisieren
prob_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8])
charging = ctrl.ControlSystemSimulation(prob_ctrl)

# Speichern des Systems
path = os.getcwd()+"\\parameters\\fuzzy_ctrl.pickle"
pickle.dump(charging, open(path, "wb"))

