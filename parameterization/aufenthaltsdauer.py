#
# @ 2021. TU Dortmund University,
# Institute of Energy Systems, Energy Efficiency and Energy Economics,
# Research group Distribution grid planning and operation
#
import pandas as pd
from collections import Counter
from utilities import get_mid_data, save_params

pd.set_option('max_columns', None)


# empirische Wahrscheinlichkeiten der Aufenthaltsdauern berechnen und speichern
def get_stayduration(type_day):
    data = get_mid_data(type_day)
    aufenthalt_it = [[[] for i in range(96)] for i in range(5)]
    # speichern der Aufenthaltsdauern der einzelnen Zustände in den unterschiedlichen Zeitschritten
    for i in range(1, 5):
        for t in range(96):
            filt = (data["Whyto"] == i) & (data["Arrival_t"] == t)
            aufenthalt_it[i][t] = data[filt]["Stay_duration"]
    # für den Zustand Zuhause nur Aufenthaltsdauern der Zwischenstopps speichern
    index_stopover = []
    for i in data[data["Whyto"] == 0].index:
        if (i + 1 not in data.index) or (data.at[i + 1, "ID"] != data.at[i, "ID"]):
            pass
        # nur Trips mit Ziel Zuhause abspeichern, worauf weitere Trips der Person folgen (Zwischenstopp)
        else:
            index_stopover.append(i)
    trips_stopover = data.iloc[index_stopover]
    for t in range(96):
        filt = trips_stopover["Arrival_t"] == t
        aufenthalt_it[0][t] = trips_stopover[filt]["Stay_duration"]
    # ermitteln der unterschiedlichen Aufenthaltsdauen und deren absoluten Häufigkeiten
    aufenthalt_counts = [[{} for i in range(96)] for i in range(5)]
    aufenthalt_val_prob = [[{} for i in range(96)] for i in range(5)]
    for i in range(5):
        for t in range(96):
            aufenthalt_counts[i][t] = Counter(aufenthalt_it[i][t])
    # umrechnen in relative Häufigkeiten
    for i in range(5):
        for t in range(96):
            total = sum(aufenthalt_counts[i][t].values())
            for key in aufenthalt_counts[i][t]:
                aufenthalt_val_prob[i][t][key] = aufenthalt_counts[i][t][key] / total
    # ersetze leere Dictionaries mit Mittelwerten aus den zwei umliegenden Dictionaries
    for i in range(5):
        for t in range(96):
            if not aufenthalt_val_prob[i][t]:
                new = {}
                t_prior, t_next = t, t
                # Wenn vorheriges oder nachfolgendes Dictionary auch leer, wähle das darauffolgende
                while True:
                    t_prior = t_prior - 1 if t_prior != 0 else 95
                    preceding = aufenthalt_val_prob[i][t_prior]
                    if preceding:
                        break
                while True:
                    t_next = t_next + 1 if t_next != 95 else 0
                    succeeding = aufenthalt_val_prob[i][t_next]
                    if succeeding:
                        break
                for key in preceding:
                    new[key] = preceding[key] / 2
                for key in succeeding:
                    if key in new:
                        new[key] = new[key] + succeeding[key] / 2
                    else:
                        new[key] = succeeding[key] / 2
                aufenthalt_val_prob[i][t] = new
    # speichern des Ergebnisses
    save_params(type_day, "Zeitabhängige Aufenthaltsdauern", aufenthalt_val_prob)
