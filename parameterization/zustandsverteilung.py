#
# @ 2021. TU Dortmund University,
# Institute of Energy Systems, Energy Efficiency and Energy Economics,
# Research group Distribution grid planning and operation
#
from utilities import get_param_dir
import matplotlib.pyplot as plt
import numpy as np
import os
import pickle


def calc_zustandsverteilung(df):
    """
    Calculate the relative number of cars at the different states throughut the day
    :param df: DataFrame of all trips and their parameters
    :return: list of lists with one list for every state and one entry for every minute of the day
    """
    no_cars = len(df[df["Trip_no"] == 1])
    # 0 <= i <= 5 für entsprechende Zustände ; i = 6 : Fahrzustand
    states = [[0 for i in range(96)] for i in range(6)]
    # iterieren durch alle Zeilen
    rows = len(df)
    for i in range(rows):
        # ZUHAUSE BIS ERSTER TRIP
        if df.at[i, "Trip_no"] == 1:
            # Fahrzeug zuhause bis zum Zeitpunkt der ersten Abfahrt
            whyfrom = df.at[i, "Whyfrom"]
            for j in range(df.at[i, "Departure_t"]):
                states[whyfrom][j] += 1

        # FAHRZUSTAND DEPARTURE - ARRIVAL
        # Fahrzeug im Fahrzustand bis zur Ankunft am Ziel
        if df.at[i, "Overnight"] == 0:
            for j in range(df.at[i, "Departure_t"], df.at[i, "Arrival_t"]):
                states[5][j] += 1
        else:
            for j in range(df.at[i, "Departure_t"], 96):
                states[5][j] += 1

        whyto = df.at[i, "Whyto"]
        # ANKUNFT BIS NÄCHSTER TAG ODER ABFAHRT NÄCHSTER TRIP
        # wenn letzter Trip der Person: Aufenthalt bis zum nächsten Morgen am Zielzustand
        if (i == rows - 1) or (df.at[i + 1, "Trip_no"] == 1):
            # vorausgesetzt der Trip endet noch am selben Tag
            if df.at[i, "Overnight"] == 0:
                for j in range(df.at[i, "Arrival_t"], 96):
                    states[whyto][j] += 1
        else:
            for j in range(df.at[i, "Arrival_t"], df.at[i + 1, "Departure_t"]):
                states[whyto][j] += 1

    # relativieren auf Gesamtanzahl der Fahrzeuge
    for j in range(6):
        states[j] = [x / no_cars for x in states[j]]
    return states


def get_mid_states(type_day):
    type_path = ["Werktag", "Samstag", "Sonn - Feiertag"]
    path = os.path.join(get_param_dir(), type_path[type_day - 1], "Zustandsverteilung.pickle")
    return pickle.load(open(path, "rb"))


def plot_zustandsverteilung(states):
    x = np.linspace(0, 95, 96)
    plt.figure(figsize=(20, 10))
    plt.plot(x, states[0], label="Zuhause", color='#FFCA3A')
    plt.plot(x, states[1], label="Arbeit", color='#FF595E')
    plt.plot(x, states[2], label="Einkaufen", color='#8AC926')
    plt.plot(x, states[3], label="Freizeit", color='#1982C4')
    plt.plot(x, states[4], label="Sonstiges", color='#6A4C93')
    plt.plot(x, states[5], label="Fahrzustand", color="orange")
    plt.legend()


def compare_zustandsverteilung(sim, mid):
    import seaborn as sns
    sns.set()

    fig, axs = plt.subplots(3, 2, figsize=(20, 10))
    plt.subplots_adjust(hspace=0.3)
    x = np.linspace(0, 95, 96)

    axs[0][0].plot(x, sim[0], label="Simulation")
    axs[0][0].plot(x, mid[0], alpha=0.7)
    axs[0][0].legend()
    axs[0][0].set_title("Anteil der Flotte im Zustand \"Zuhause\"")

    axs[0][1].plot(x, sim[1], label="Simulation")
    axs[0][1].plot(x, mid[1], alpha=0.7, label="MID Daten")
    axs[0][1].legend()
    axs[0][1].set_title("Anteil der Flotte im Zustand \"Arbeit\"")

    axs[1][0].plot(x, sim[2], label="Simulation")
    axs[1][0].plot(x, mid[2], alpha=0.7, label="MID Daten")
    axs[1][0].legend()
    axs[1][0].set_title("Anteil der Flotte im Zustand \"Einkaufen\"")

    axs[1][1].plot(x, sim[3], label="Simulation")
    axs[1][1].plot(x, mid[3], alpha=0.7, label="MID Daten")
    axs[1][1].legend()
    axs[1][1].set_title("Anteil der Flotte im Zustand \"Freizeit\"")

    axs[2][0].plot(x, sim[4], label="Simulation")
    axs[2][0].plot(x, mid[4], alpha=0.7, label="MID Daten")
    axs[2][0].legend()
    axs[2][0].set_title("Anteil der Flotte im Zustand \"Sonstiges\"")

    axs[2][1].plot(x, sim[5], label="Simulation")
    axs[2][1].plot(x, mid[5], alpha=0.7, label="MID Daten")
    axs[2][1].legend()
    axs[2][1].set_title("Anteil der Flotte im Fahrzustand")

    savefig("Zustandsverteilung")
