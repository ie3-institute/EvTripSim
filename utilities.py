#
# @ 2021. TU Dortmund University,
# Institute of Energy Systems, Energy Efficiency and Energy Economics,
# Research group Distribution grid planning and operation
#
import pandas as pd
import os
import pickle
from pathlib import Path


ROOT_DIR = Path(__file__).parent

MID_DIR = r"C:\Users\user\Desktop\MiD"


# Laden der MiD-Daten
def get_mid_data(type_day, cs=None, var_power=False):
    days = ["we", "sa", "so"]
    # Datensatz mit simulierten Ladezeiten
    if cs:
        charge_scen = ["CS1", "CS2", "CS3"]
        path = MID_DIR + r"\Aufbereitete Daten\Ladezeiten"
        if var_power:
            filename = "\\Trips_{}_{}_Ladezeiten_vp.csv".format(days[type_day - 1], charge_scen[cs - 1])
        else:
            filename = "\\Trips_{}_{}_Ladezeiten.csv".format(days[type_day - 1], charge_scen[cs - 1])
        data = pd.read_csv(path + filename)
    # Datensatz ohne simulierte Ladezeiten
    else:
        data = pd.read_csv(MID_DIR + r"\Aufbereitete Daten\Trips_processed_{}.csv".
                           format(days[type_day - 1]))
    return data


# Laden der MiD-EBZ
def get_mid_ebz(type_day, cs):
    day = ["Werktag", "Samstag", "Sonn - Feiertag"]
    root = ROOT_DIR / "parameterization" / "parameters" / "{}".format(day[type_day-1])
    filename = "Ladende_Fahrzeuge_CS{}.pickle".format(cs)
    return pickle.load(open(root+filename, "rb"))


def get_param_dir():
    """ Directory where paramters for the simulation are located """
    return ROOT_DIR / "parameterization" / "parameters"


def save_params(type_day, filename, file):
    type_path = ["Werktag", "Samstag", "Sonn - Feiertag"]
    path = get_param_dir() / type_path[type_day - 1] / filename / ".pickle"
    pickle.dump(file, open(path, "wb"))


def format_simresults(simulated_evs):
    """ Return DataFrame of all simulated trips """
    from collections import defaultdict

    # erzeugen Dictionary "Key : List"
    total_trips_dict = defaultdict(list)

    # speichern der Trips jedes einzelnen Fahrzeugs im dict
    for ev in simulated_evs:
        for trip in ev.trips:
            # .__dict__.items() returns Dictionary mit allen Member Variablen und dazugehörigen Werten des Objekts
            for key, val in trip.__dict__.items():
                total_trips_dict[key].append(val)

    # umwandeln in DataFrame
    data = pd.DataFrame(total_trips_dict)
    # Spaltennamen umformatieren
    data.rename(str.capitalize, axis='columns', inplace=True)
    data.rename(columns={"Id": "ID"}, inplace=True)
    # Anpassen der Daten wenn Zeiten in nächsten Tag hineinreichen
    data["Arrival"] = data["Arrival"].apply(lambda x: x - 1440 if x > 1439 else x)
    data["Charge_start"] = data["Charge_start"].apply(lambda x: x - 1439 if x > 1439 else x)
    data["Charge_end"] = data["Charge_end"].apply(lambda x: x - 1439 if x > 1439 else x)
    data["Charge_end"] = data["Charge_end"].apply(lambda x: x - 1439 if x > 1439 else x)
    return data


def evaluate_save_simresults(data, type_day, filename, var_power):
    # Ordner erstellen in denen Ergebnisse abgelegt werden
    days = ["Werktag", "Samstag", "Sonn - Feiertag"]
    path = ROOT_DIR / "results" / "tripseval" / days[type_day-1] / filename
    path.mkdir(parents=True, exist_ok=True)
    # Auswertung Zustandsverteilung und EBZ
    from parameterization.zustandsverteilung import calc_zustandsverteilung
    states = calc_zustandsverteilung(data)
    from parameterization.ebz import calc_ebz
    ebz = calc_ebz(data, var_power)
    # Speichern der Ergebnisse im Ordner
    pickle.dump(states, open(path / "states.pickle", "wb"))
    pickle.dump(ebz, open(path / "ebz.pickle", "wb"))
    path_res = ROOT_DIR / "results" / "trips" / days[type_day-1]
    Path(path_res).mkdir(parents=True, exist_ok=True)
    data.to_csv(path_res / "{}.csv".format(filename), index=False)
    print("I wrote everything to know about the simulated trips to \"{}\".".format(path_res / (filename+".csv")))
    print("Find some initial evaluations at {}\nYou're welcome!".format(path))


def load_eval_data(kw, cs=None):
    root = os.getcwd()
    cwd = root.split('\\')
    filename, day = cwd[-1], cwd[-2]
    if kw == "sim":
        path_sim = ROOT_DIR / "execution" / "Ergebnisse" / day / "{}.csv".format(day, filename)
        sim = pd.read_csv(path_sim)
        sim_states = pickle.load(open(root / "states.pickle", "rb"))
        sim_ebz = pickle.load(open(root / "ebz.pickle", "rb"))
        return sim, sim_states, sim_ebz
    if kw == "mid":
        days = ["Werktag", "Samstag", "Sonn - Feiertag"]
        type_day = days.index(day) + 1
        mid = get_mid_data(type_day)
        from parameterization.zustandsverteilung import get_mid_states
        mid_states = get_mid_states(type_day)
        mid_ebz = get_mid_ebz(type_day, cs)
        return mid, mid_states, mid_ebz


def compare_curves(sim, mid):

    from sklearn.metrics import mean_squared_error
    from scipy.integrate import simps
    from numpy import trapz

    abs_dev = [[] for i in range(6)]
    mad = [None for i in range(6)]
    max_ad = [None for i in range(6)]
    mse = [None for i in range(6)]
    for i in range(6):
        abs_dev[i] = [abs(sim[i][x] - mid[i][x]) for x in range(1440)]
        max_ad[i] = max(abs_dev[i])
        mad[i] = sum(abs_dev[i]) / len(abs_dev[i])
        mse[i] = mean_squared_error(sim[i], mid[i])
    print("Die mittlere absolute Abweichung der Graphen beträgt:")
    print(mad)
    print("\n")
    print("Die mittlere quadratische Abweichung beträgt:")
    print(mse)
    print("\n")
    print("Die maximal auftretende Abweichung beträgt:")
    print(max_ad)
    print("\n")

    area_sim_tr = [None for i in range(6)]
    area_mid_tr = [None for i in range(6)]

    area_sim_si = [None for i in range(6)]
    area_mid_si = [None for i in range(6)]

    for i in range(6):
        area_sim_tr[i] = trapz(sim[i], dx=1)
        area_mid_tr[i] = trapz(mid[i], dx=1)

        area_sim_si[i] = simps(sim[i], dx = 1)
        area_mid_si[i] = simps(mid[i], dx = 1)

    delt_area_tr = [(area_sim_tr[i] - area_mid_tr[i]) / area_mid_tr[i] for i in range(6)]
    delt_area_si = [(area_sim_si[i] - area_mid_si[i]) / area_mid_si[i] for i in range(6)]

    print("Fläche über Berechnung mit Trapezregel (Simulation):")
    print(area_sim_tr)
    print("\n")
    print("Fläche über Berechnung mit Trapezregel (MID):")
    print(area_mid_tr)
    print("\n")
    print("Relative Abweichung der Flächen:")
    print(delt_area_tr)
    print("\n")
    print("Fläche über Berechnung mit Simpsonregel (Simulation):")
    print(area_sim_si)
    print("\n")
    print("Fläche über Berechnung mit Simpsonregel (MID):")
    print(area_mid_si)
    print("\n")
    print("Relative Abweichung der Flächen:")
    print(delt_area_si)



