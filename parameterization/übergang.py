#
# @ 2021. TU Dortmund University,
# Institute of Energy Systems, Energy Efficiency and Energy Economics,
# Research group Distribution grid planning and operation
#
import numpy as np
import matplotlib.pyplot as plt
from utilities import get_mid_data, save_params


# Berechnen und speichern der Übergangswahrscheinlichkeiten
def get_transition_probs(type_day):
    data = get_mid_data(type_day)

    states_grpd = [None for i in range(5)]
    for i in range(5):
        # filtern nach Ausgangszustand
        state = data[data["Whyfrom"] == i]
        # gruppieren nach Abfahrtszeitschritt
        states_grpd[i] = state.groupby(["Departure_t"])

    tp_itj = [[[0 for j in range(5)] for t in range(96)] for i in range(5)]
    for i in range(5):
        for t, group in states_grpd[i]:
            # ermittle relative Häufigkeiten der Übergänge zu den anderen Zuständen
            # von Ausgangszustand i in Zeitschritt t
            counts = group["Whyto"].value_counts(normalize=True)
            # zuordnen der relativen Übergangshäufigkeiten zu entsprechenden Einträgen
            if counts.get(0):
                tp_itj[i][t][0] = counts.get(0)
            if counts.get(1):
                tp_itj[i][t][1] = counts.get(1)
            if counts.get(2):
                tp_itj[i][t][2] = counts.get(2)
            if counts.get(3):
                tp_itj[i][t][3] = counts.get(3)
            if counts.get(4):
                tp_itj[i][t][4] = counts.get(4)

    # ersetze fehlende Übergangswahrscheinlichkeiten durch Gleichverteilung (0.2)
    def replace_missing_probs(tp_itj):
        for t in range(96):
            for i in range(5):
                total = sum([tp_itj[i][t][j] for j in range(5)])
                if total == 0:
                    for j in range(5):
                        tp_itj[i][t][j] = 0.2

    replace_missing_probs(tp_itj)
    # speichern der Daten
    save_params(type_day, "Übergangswahrscheinlichkeiten", tp_itj)


def plot_transition_probs(tp_ijt):
    fig, axs = plt.subplots(5, figsize=(20, 40), sharey=True)
    x = np.linspace(0, 95, 96)
    states = ["Zuhause", "Arbeit", "Freizeit", "Einkaufen", "Sonstiges"]
    for i in range(5):
        axs[i].bar(x, tp_ijt[i][0], label="Zuhause", color='#FFCA3A');
        axs[i].bar(x, tp_ijt[i][1], bottom=tp_ijt[i][0], label="Arbeit", color='#FF595E');
        axs[i].bar(x, tp_ijt[i][2], bottom=[i + j for i, j in zip(tp_ijt[i][0], tp_ijt[i][1])], label="Einkaufen",
                color='#8AC926')
        axs[i].bar(x, tp_ijt[i][3], bottom=[i + j + k for i, j, k in zip(tp_ijt[i][0], tp_ijt[i][1], tp_ijt[i][2])],
                label="Freizeit", color='#1982C4')
        axs[i].bar(x, tp_ijt[i][4], bottom=[i + j + k + l for i, j, k, l in
                                         zip(tp_ijt[i][0], tp_ijt[i][1], tp_ijt[i][2], tp_ijt[i][3])],
                label="Sonstiges", color='#6A4C93')
        axs[i].set_title("Ausgangszustand: {}".format(states[i]))
        axs[i].legend()






