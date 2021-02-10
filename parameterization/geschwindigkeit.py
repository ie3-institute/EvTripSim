#
# @ 2021. TU Dortmund University,
# Institute of Energy Systems, Energy Efficiency and Energy Economics,
# Research group Distribution grid planning and operation
#
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from utilities import get_mid_data, save_params


# Berechnen und speichern durchschnittlicher Geschwindigkeiten der MiD-Fahrten
def get_speed(type_day, zeitabhängig=True):
    if zeitabhängig:
        data = get_mid_data(type_day)
        pd.set_option('display.max_columns', None)
        data_grpd = [[] for i in range(12)]

        # 8 periodige Schritte -> parametrieren der Funktion in 2 stündigen Zeitintervallen
        steps = np.arange(0, 97, 8)
        for i in range(len(steps)-1):
            filt = (data["Departure_t"] < steps[i+1]) & (data["Departure_t"] >= steps[i])
            data_grpd[i] = data[filt]

        def func(x, a, b):
            return a + b*np.log(x)

        def fit_plot_curve (data, start, end):
            av_speeds = []
            for i in range(1, 150):
                # filtere auf alle i.xx Werte
                filt = (data["Distance"] - i > 0) & (data["Distance"] - i < 1)
                # ermittle den Median aller Geschwindigkeiten für das Distanzintervall
                av_speed = data[filt]["Av_speed"].median()
                if not np.isnan(av_speed):
                    av_speeds.append((i, av_speed))
            # x = Distanz, y = Geschwindigkeit
            x, y = zip(*av_speeds)
            # anpassen der Kurve an Funktionswerte
            popt, pcov = curve_fit(func, x, y)
            x_func = np.linspace(1, 150, 149)
            fitted_curve = [func(x_val, *popt) for x_val in np.linspace(1, 150, 149)]
            # plotten der Kurve
            plt.plot(x_func, fitted_curve, label="Intervall von {}, bis {} Uhr".format(start, end))
            plt.xlabel("Distanz in km")
            plt.ylabel("Gewschwindigkeit in km/h")
            # untere Schranke der Geschwindigkeiten bestimmen
            lower_bound = data["Av_speed"].quantile(0.05)
            popt = np.append(popt, lower_bound)
            return popt

        plt.figure(figsize=(30, 20))
        params = [[] for i in range(len(data_grpd))]
        for i, group in enumerate(data_grpd):
            params[i] = fit_plot_curve(group, i * 2, i * 2 + 2)
        plt.legend()
        # speichern der Ergebnisse
        save_params(type_day, "Zeitabhängige Geschwindigkeit", params)

    else:
        print("Noch nicht ergänzt")

