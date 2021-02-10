#
# @ 2021. TU Dortmund University,
# Institute of Energy Systems, Energy Efficiency and Energy Economics,
# Research group Distribution grid planning and operation
#
from utilities import get_mid_data, save_params


# Berechne Wahrscheinlichkeit das Trip zum Wohnort Zwischenstopp vs Endaufenthalt ist
def get_stopoverprobs(type_day):
    df = get_mid_data(type_day)
    filt = df["Whyto"] == 0
    df_filt = df[filt]
    index_stopover = []
    index_final = []
    # Home-Trips aufteilen in Endstopps und Zwischenstopps
    for i in df_filt.index:
        if (i + 1 not in df.index) or (df.at[i + 1, "ID"] != df.at[i, "ID"]):
            index_final.append(i)
        else:
            index_stopover.append(i)
    df_final = df.iloc[index_final]
    df_stopover = df.iloc[index_stopover]
    # aufteilen der Trips nach den unterschiedlichen Zeitschritten
    trips_t_final = [0 for i in range(96)]
    trips_t_stopover = [0 for i in range(96)]
    # Wenn Fahrt mit Index i Endaufenthalt ist
    for i in df_final.index:
        # Abfahrtszeitintervall des Trips
        t = df_final.at[i, "Departure_t"]
        # erhöhe Zähler der Trips mit Endaufenthalt zum entsprechenden Zeitintervall
        trips_t_final[t] += 1
    # Wenn Fahrt mit Index i Endaufenthalt ist
    for i in df_stopover.index:
        # Abfahrtszeitintervall des Trips
        t = df_stopover.at[i, "Departure_t"]
        # erhöhe Zähler der Trips mit Zwischenstopp zum entsprechenden Zeitintervall
        trips_t_stopover[t] += 1
    for t in range(96):
        total = trips_t_final[t] + trips_t_stopover[t]
        if total:
            trips_t_final[t] = trips_t_final[t] / total
            trips_t_stopover[t] = trips_t_stopover[t] / total
        # Für den Fall, dass keine Trips in Zeitperiode vorhanden sind:
        # ermittle W'keiten über das Mittel aus vorherigen und kommenden Period
        else:
            total = trips_t_final[t - 1] + trips_t_stopover[t - 1] + \
                    trips_t_final[t + 1] + trips_t_stopover[t + 1]
            trips_t_final[t] = (trips_t_final[t - 1] + trips_t_final[t + 1]) / total
            trips_t_stopover[t] = (trips_t_stopover[t - 1] + trips_t_stopover[t + 1]) / total
    # speichern der Ergebnisse
    save_params(type_day, "Zwischenstoppwk", trips_t_final)


def plot_stopoverprobs(trips_t_final, trips_t_stopover):
    import matplotlib.pyplot as plt
    import numpy as np

    plt.figure(figsize=(20, 10))
    x = np.linspace(0, 95, 96)
    plt.bar(x, trips_t_final, label="Endzustand")
    plt.bar(x, trips_t_stopover, bottom=trips_t_final, label="Zwischenstopp")
    plt.legend();