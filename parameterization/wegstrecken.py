#
# @ 2021. TU Dortmund University,
# Institute of Energy Systems, Energy Efficiency and Energy Economics,
# Research group Distribution grid planning and operation
#
from collections import Counter
from utilities import get_mid_data, save_params


def get_distances(type_day):
    data = get_mid_data(type_day)
    step = 96

    # Wegstrecken in 2-dimensionaler Liste Speichern
    # ij beschreibt Weg von Zustand i nach Zustand j
    # initialisieren 5x5 Liste
    wege_ij = [[[[] for t in range(step)] for j in range(5)] for i in range(5)]
    for i in range(0, 5):
        for j in range(0, 5):
            for t in range(step):
                # filtern des Dataframes nach Ausgangs- und Zielzustandskombinationen
                filt = (data["Whyfrom"] == i) & (data["Whyto"] == j) & (data["Departure_t"] == t)
                # speichern der Liste der Distanzen zwischen den Zuständen in entsprechendem Feld
                wege_ij[i][j][t] = list(data[filt]["Distance"])

    # ermitteln der absoluten Häufigkeiten der Wegstrecken
    wege_ij_count = [[[[] for t in range(step)] for i in range(5)] for j in range(5)]
    wege_ij_prob_dict = [[[{} for t in range(step)] for i in range(5)] for j in range(5)]
    for i in range(5):
        for j in range(5):
            for t in range(step):
                wege_ij_count[i][j][t] = Counter(wege_ij[i][j][t])

    # umwandeln in relative Häufigkeiten und speichern in Dictionary (Wert : rel. Häufigkeit)
    for i in range(5):
        for j in range(5):
            for t in range(step):
                total = sum(wege_ij_count[i][j][t].values())
                for key in wege_ij_count[i][j][t]:
                    wege_ij_prob_dict[i][j][t][key] = wege_ij_count[i][j][t][key] / total

    # ersetze leere Dictionaries mit Mittelwerten aus den zwei umliegenden Dictionaries
    for i in range(5):
        for j in range(5):
            for t in range(step):
                if not wege_ij_prob_dict[i][j][t]:
                    new = {}
                    t_prior, t_next = t, t
                    # Wenn vorheriges oder nachfolgendes Dictionary auch leer, wähle das darauffolgende
                    while True:
                        t_prior = t_prior - 1 if t_prior != 0 else step - 1
                        preceding = wege_ij_prob_dict[i][j][t_prior]
                        if preceding:
                            break
                    while True:
                        t_next = t_next + 1 if t_next != step - 1 else 0
                        succeeding = wege_ij_prob_dict[i][j][t_next]
                        if succeeding:
                            break
                    for key in preceding:
                        new[key] = preceding[key] / 2
                    for key in succeeding:
                        if key in new:
                            new[key] = new[key] + succeeding[key] / 2
                        else:
                            new[key] = succeeding[key] / 2
                    wege_ij_prob_dict[i][j][t] = new

    save_params(type_day, "Zeitabhängige Wegstrecken", wege_ij_prob_dict)


