#
# @ 2021. TU Dortmund University,
# Institute of Energy Systems, Energy Efficiency and Energy Economics,
# Research group Distribution grid planning and operation
#
import pickle
import os
import random
import numpy as np
from execution.ev import ElectricVehicle
from utilities import get_param_dir


def init_trip(type_day, whyfrom, departure=None):
    if type_day == 1:
        return TripWe(whyfrom, departure)
    elif type_day == 2:
        return TripSa(whyfrom, departure)
    elif type_day == 3:
        return TripSo(whyfrom, departure)


# TODO Change to abstract class
class Trip(object):
    type_day = None

    def __init__(self, whyfrom=None, departure=None):
        self.id = None
        self.trip_no = None
        self.whyfrom = whyfrom
        self.whyto = None
        self.departure = departure
        if departure is not None:
            departure = int(departure)
            self.departure = departure
            self.departure_t = int(departure / 15)
        self.arrival = None
        self.trip_duration = None
        self.distance = None
        self.stay_duration = None
        self.SOC_start = None
        self.SOC_end = None
        self.charge_start = None
        self.charge_end = None
        self.av_speed = None
        self.categ_location = None
        self.poi_id = None
        self.pp_id = None
        self.final_soc = None
        self.charge_prob = None
        self.p_charge = None

    @classmethod
    # Methode zum Laden der Wert:Wahrscheinlichkeit Dictionaries
    def load_val_prob(cls, root, size_dim_1, file_name, size_dim_2=None, size_dim_3=None):
        val_prob = pickle.load(open(os.path.join(root, file_name), "rb"))

        if size_dim_3:
            val = [[[[] for _ in range(size_dim_3)] for _ in range(size_dim_2)] for _ in range(size_dim_1)]
            prob = [[[[] for _ in range(size_dim_3)] for _ in range(size_dim_2)] for _ in range(size_dim_1)]

            for i in range(5):
                for j in range(5):
                    for t in range(size_dim_3):
                        val[i][j][t], prob[i][j][t] = zip(*val_prob[i][j][t].items())

        elif size_dim_2:
            val = [[[] for _ in range(size_dim_2)] for _ in range(size_dim_1)]
            prob = [[[] for _ in range(size_dim_2)] for _ in range(size_dim_1)]

            for i in range(size_dim_1):
                for j in range(size_dim_2):
                    val[i][j], prob[i][j] = zip(*val_prob[i][j].items())

        else:
            val = [[] for _ in range(size_dim_1)]
            prob = [[] for _ in range(size_dim_1)]

            for i in range(size_dim_1):
                val[i], prob[i] = zip(*val_prob[i].items())

        return val, prob

    @classmethod
    def load_variables(cls):
        days = ["Werktag", "Samstag", "Sonn - Feiertag"]
        data_dir = get_param_dir()
        root = data_dir / days[cls.type_day - 1]

        # Wert : W'keit Dictionary Abfahrtszeit
        initial_departure_val_prob = pickle.load(open(root / "Abfahrtszeit.pickle", "rb"))
        # Entpacken in Werte und Wahrscheinlichkeitsliste
        cls.initial_dep_val, cls.initial_dep_prob = zip(*initial_departure_val_prob.items())
        # Übergangswkeit von i -> j im Zeitschritt t = transition_prob[j][i][t]
        cls.transition_prob = pickle.load(open(root / "Übergangswahrscheinlichkeiten.pickle", "rb"))
        # Wegstrecken und zugehörige W'keiten
        cls.wege_ij_val, cls.wege_ij_prob = cls.load_val_prob(root, 5, "Zeitabhängige Wegstrecken.pickle", size_dim_2=5,
                                                              size_dim_3=96)
        # Aufenthaltsdauern und zugehörige W'keiten
        cls.aufenthalt_val, cls.aufenthalt_prob = cls.load_val_prob(root, 5, "Zeitabhängige Aufenthaltsdauern.pickle",
                                                                    size_dim_2=96)
        # W'keit das Trip die finale Fahrt ist
        cls.home_prob_final = pickle.load(open(root / "Zwischenstoppwk.pickle", "rb"))
        # Dictionary mit den Listen aller POIs
        cls.aufenthaltsort = pickle.load(open(data_dir / "POIs" / "Aufenthaltsorte.pickle", "rb"))

        # Einkaufen / Freizeit Dictionarys mit W'keiten der Zugehörigkeit zu kategorischen Orten im Tagesverlauf
        cls.einkaufen_categ_loc_weights, cls.freizeit_categ_loc_weights = pickle.load(
            open(root / "Unterteilung_Einkaufen_Freizeit.pickle", "rb"))

        # laden der Parameter der EV Geschwindigkeitsfunktion in EV Klasse
        ElectricVehicle.set_speedparams(root)

    def sample_departure(self):
        departure = np.random.choice(self.initial_dep_val, p=self.initial_dep_prob)
        self.departure = int(departure)
        self.departure_t = int(departure / 15)

    def sample_whyto(self):
        probs = self.transition_prob[self.whyfrom][self.departure_t]
        self.whyto = np.random.choice([0, 1, 2, 3, 4], p=probs)

    # Ermittle kategorische Tageszeit
    @staticmethod
    def calc_time_period(time):
        # Zeiten nach 24:00 formatieren
        time = time if time < 1440 else time - 1440
        t = int(time / 60)
        # Morgen
        if 5 <= t < 10:
            return 0
        # Vormittag
        elif 10 <= t < 12:
            return 1
        # Mittag
        elif 12 <= t < 14:
            return 2
        # Nachmittag
        elif 14 <= t < 18:
            return 3
        # Abend
        elif 18 <= t < 23:
            return 4
        # Nacht
        elif 23 <= t < 24 or 0 <= t < 5:
            return 5

    def sample_categ_location(self, whyto):
        if whyto in {0, 1}:
            return self.get_valid_categ_locations(whyto)
        elif whyto in {2, 3, 4}:
            return self.make_weighted_choice(whyto)
        else:
            raise ValueError("whyto has to be in range: 0 <= whyto <=4")

    def make_weighted_choice(self, whyto):
        valid_categ_locations = self.get_valid_categ_locations(self.whyto)
        if whyto == 4:
            return random.choices(valid_categ_locations, k=1)[0]
        elif whyto in {2, 3}:
            time_period = Trip.calc_time_period(self.arrival)
            weights = self.get_categ_location_weights(self.whyto)
            weights_at_time_period = [weights[loc][time_period] for loc in valid_categ_locations]
            return random.choices(valid_categ_locations, weights=weights_at_time_period, k=1)[0]
        else:
            raise ValueError("weighted choice only for 2 <= whyto <= 4")

    @staticmethod
    def get_valid_categ_locations(whyto):
        if whyto == 0:
            return "Wohnort"
        elif whyto == 1:
            return "Arbeitsplatz"
        elif whyto == 2:
            return ["Supermarkt", "Sonstiges Geschäft", "Medizinisch", "Wohnort", "Dienstleistung",
                    "BBPG", "Kirche, Friedhof", "Gastronomie"]
        elif whyto == 3:
            return ["Sportstätten", "Wohnort", "Gastronomie", "Kulturell", "Kirche, Friedhof",
                    "Supermarkt"]
        elif whyto == 4:
            return ["Sportstätten", "Wohnort", "Gastronomie", "Kulturell", "Kirche, Friedhof",
                    "Supermarkt", "BBPG", "Dienstleistung", "Medizinisch"]

    def get_categ_location_weights(self, whyto):
        if whyto == 2:
            return self.einkaufen_categ_loc_weights
        elif whyto == 3:
            return self.freizeit_categ_loc_weights
        else:
            raise ValueError("location weighted only for whyto in {2, 3}")

    def sample_poi(self, home):
        # wenn Fahrzeug nach Hause fährt entspricht POI dem Wohnort des Fahrzeugs
        if self.whyto == 0 or self.categ_location == "Wohnort":
            return home
        else:
            # erhalte Liste der passenden POIs
            pois = self.get_all_pois(self.categ_location)
            # Wahl eines zufälligen POI aus Liste
            idx = random.randint(0, len(pois) - 1)
            # speichern des Orts in Tripinformationen
            poi = pois.iloc[idx]
            return poi

    def get_all_pois(self, categ_location):
        return self.aufenthaltsort[categ_location]

    def pick_nearest_pp(self, poi):
        if self.categ_location == "Wohnort":
            return poi["osm_id"]
        else:
            return poi["pp_nearby"][0][1]

    def sample_stayduration(self, trips, time):
        if self.whyto == 0:

            # Wenn Zielzustand = Zuhause, unterscheide zwischen Zwischenstopp und Endaufenthalt
            is_final = np.random.choice([True, False], p=[self.home_prob_final[self.departure_t],
                                                          1 - self.home_prob_final[self.departure_t]])
            # Wenn Endaufenthalt, Aufenthaltsdauer berechnen bis zum Zeitpunkt des ersten Trips des Tages
            if is_final:
                # wenn aktueller Trip nicht der erste:
                if trips:
                    stay_duration = 1440 - time + trips[0].departure
                # falls einziger Trip des Tages Rundtrip mit Ursprung und Ziel Zuhause ist:
                else:
                    stay_duration = 1440 - time + self.departure
            # Andernfalls samplen der Aufenthaltswerte
            else:
                stay_duration = np.random.choice(self.aufenthalt_val[self.whyto][self.departure_t],
                                                 p=self.aufenthalt_prob[self.whyto][self.departure_t])
        else:
            stay_duration = np.random.choice(self.aufenthalt_val[self.whyto][self.departure_t],
                                             p=self.aufenthalt_prob[self.whyto][self.departure_t])
        self.stay_duration = int(stay_duration)

    def sample_distance(self):
        distances = self.wege_ij_val[self.whyfrom][self.whyto][self.departure_t]
        probs = self.wege_ij_prob[self.whyfrom][self.whyto][self.departure_t]
        self.distance = np.random.choice(distances, p=probs)


class TripWe(Trip):
    initiated = False
    type_day = 1

    def __init__(self, whyfrom=None, departure=None):
        super().__init__(whyfrom, departure)
        if not TripWe.initiated:
            TripWe.load_variables()
            TripWe.initiated = True


class TripSa(Trip):
    initiated = False
    type_day = 2

    def __init__(self, whyfrom=None, departure=None):
        super().__init__(whyfrom, departure)
        if not TripSa.initiated:
            TripSa.load_variables()
            TripSa.initiated = True


class TripSo(Trip):
    initiated = False
    type_day = 3

    def __init__(self, whyfrom=None, departure=None):
        super().__init__(whyfrom, departure)
        if not TripSo.initiated:
            TripSo.load_variables()
            TripSo.initiated = True
