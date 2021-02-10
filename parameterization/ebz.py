#
# @ 2021. TU Dortmund University,
# Institute of Energy Systems, Energy Efficiency and Energy Economics,
# Research group Distribution grid planning and operation
#
import pickle
import utilities
import numpy as np
import matplotlib.pyplot as plt


# berechnet auf Basis der Ladezeiten die Anzahl der ladenden Fahrezuege über den Tagesverlauf
def calc_ebz(df, var_power: bool):
    """
    Calculate the relative number of cars charging throughout the day for every single state and for all states combined

    :param df: DataFrame with all trips and their parameters
    :param var_power: use variable charging powers
    :return: List[List] with number of cars charging for every state and aggregated for every 1440 minutes of the day
    """
    no_cars = len(df[df["Trip_no"] == 1])

    def calc_cars_charging(df_filt):
        cars_charging = [0 for _ in range(1440)]
        for i in range(len(df_filt)):
            start = int(df_filt.at[i, "Charge_start"])
            end = int(df_filt.at[i, "Charge_end"])
            if var_power:
                power = df_filt.at[i, "P_charge"]
            # inkrementiere cars_charging während Ladezeit des Fahrzeugs
            if start <= end:
                for j in range(start, end):
                    if var_power:
                        cars_charging[j] += power
                    else:
                        cars_charging[j] += 1
            # Vorgehen für den Fall das Ladevorgang in den nächsten Tag hineinreicht
            else:
                for j in range(start, 1440):
                    if var_power:
                        cars_charging[j] += power
                    else:
                        cars_charging[j] += 1
                for j in range(0, end):
                    if var_power:
                        cars_charging[j] += power
                    else:
                        cars_charging[j] += 1
        return [x / no_cars for x in cars_charging]

    df = df[df["Charge_start"].notnull()]
    relative_cars_charging = [[] for i in range(6)]
    # durchführen für jeweils einzelne Zustände, als auch für alle Zustände gemeinsam
    for i in range(6):
        if i < 5:
            filt = df["Whyto"] == i
            df_filt = df[filt].reset_index(drop=True)
        else:
            df_filt = df.reset_index(drop=True)
        relative_cars_charging[i] = calc_cars_charging(df_filt)
    return relative_cars_charging


def save_midebz(cars_charging, type_day, cs, var_power):
    days = ["Werktag", "Samstag", "Sonn - Feiertag"]
    root = utilities.ROOT_DIR / "parameterization" / "parameters" / days[type_day-1]
    if var_power:
        filename = "Ladende_Fahrzeuge_CS{}_vp.pickle".format(cs)
    else:
        filename = "Ladende_Fahrzeuge_CS{}.pickle".format(cs)
    path = root / filename
    pickle.dump(cars_charging, open(path, "wb"))


def plot_ebz(relative_cars_charging):
    plt.figure(figsize=(20, 8))
    x = np.linspace(0, 1439, 1440)
    plt.title("Anteil der ladenden Fahrzeuge im Tagesverlauf")
    plt.xlabel("Tageszeit in Minuten")
    plt.plot(x, relative_cars_charging[5], label="Gesamtanzahl ladender Fahrzeuge")
    plt.plot(x, relative_cars_charging[0], label="Fahrzeuge die Zuhause laden.")
    plt.plot(x, relative_cars_charging[1], label="Fahrzeuge die auf der Arbeit laden.")
    plt.plot(x, relative_cars_charging[2], label="Fahrzeuge die während des Einkaufens laden.")
    plt.plot(x, relative_cars_charging[3], label="Fahrzeuge die während Freizeitaktivitäten laden.")
    plt.plot(x, relative_cars_charging[4], label="Fahrzeuge die während anderen Aktivitäten laden.")
    plt.legend()


def compare_ebz(sim, mid):
    fig, ((ax1, ax2), (ax3, ax4), (ax5, ax6)) = plt.subplots(3, 2, figsize=(20, 10))
    plt.subplots_adjust(hspace=0.5)
    x = np.linspace(0, 1439, 1440)

    ax1.plot(x, sim[0], label="Simulation")
    ax1.plot(x, mid[0], label="MID Trips")
    ax1.set_title("Anteil der ladenden Fahrzeuge im Tagesverlauf (Zustand: Zuhause)")
    ax1.set_xlabel("Tageszeit in Minuten")
    ax1.legend()

    ax2.plot(x, sim[1], label="Simulation")
    ax2.plot(x, mid[1], label="MID Trips")
    ax2.set_title("Anteil der ladenden Fahrzeuge im Tagesverlauf (Zustand: Arbeit)")
    ax2.set_xlabel("Tageszeit in Minuten")
    ax2.legend()

    ax3.plot(x, sim[2], label="Simulation")
    ax3.plot(x, mid[2], label="MID Trips")
    ax3.set_title("Anteil der ladenden Fahrzeuge im Tagesverlauf (Zustand: Einkaufen)")
    ax3.set_xlabel("Tageszeit in Minuten")
    ax3.legend()

    ax4.plot(x, sim[3], label="Simulation")
    ax4.plot(x, mid[3], label="MID Trips")
    ax4.set_title("Anteil der ladenden Fahrzeuge im Tagesverlauf (Zustand: Freizeit)")
    ax4.set_xlabel("Tageszeit in Minuten")
    ax4.legend()

    ax5.plot(x, sim[4], label="Simulation")
    ax5.plot(x, mid[4], label="MID Trips")
    ax5.set_title("Anteil der ladenden Fahrzeuge im Tagesverlauf (Zustand: Sonstiges)")
    ax5.set_xlabel("Tageszeit in Minuten")

    ax6.plot(x, sim[5], label="Simulation")
    ax6.plot(x, mid[5], label="MID Trips")
    ax6.set_title("Anteil der ladenden Fahrzeuge im Tagesverlauf")
    ax6.set_xlabel("Tageszeit in Minuten")
    ax6.legend()

    ax6.legend()
