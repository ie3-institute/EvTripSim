#
# @ 2021. TU Dortmund University,
# Institute of Energy Systems, Energy Efficiency and Energy Economics,
# Research group Distribution grid planning and operation
#

import pickle
import numpy as np
import utilities
import random
from execution.evmodel import ElectricVehicleModel


class ElectricVehicle(ElectricVehicleModel):
    PCHARGE_SLOW = 3.7
    PCHARGE_FAST = 22
    # laden möglicher Wohnorte
    locs_path = utilities.get_param_dir() / "POIs" / "Aufenthaltsorte.pickle"
    home_locs = pickle.load(open(locs_path, "rb"))["Wohnort"]
    home_ids = [i for i in range(len(home_locs))]
    home_ids_copy = home_ids.copy()
    CHARGE_SCEN = None
    # Fuzzy Control System laden
    fuzzy_ctrl = pickle.load(open(utilities.get_param_dir() / "fuzzy_ctrl.pickle", "rb"))
    is_regio = False

    def __init__(self):
        super().__init__()
        if ElectricVehicle.is_regio:
            self.home = ElectricVehicle.choose_home()
        self.SOC = 100
        self.trip_no = 0
        self.trips = []

    @classmethod
    def set_regio(cls, regio: bool):
        cls.is_regio = regio

    @staticmethod
    def choose_home():
        """
        Choose the home POI of the car. When all possible POIs have been chosen start from the beginning and assign
        more than one car to a single POI
        """
        if ElectricVehicle.home_ids_copy:
            idx = ElectricVehicle.home_ids_copy.pop()
            return ElectricVehicle.home_locs.iloc[idx]
        else:
            ElectricVehicle.home_ids_copy = ElectricVehicle.home_ids.copy()
            idx = ElectricVehicle.home_ids_copy.pop()
            print("Refilled List")
            return ElectricVehicle.home_locs.iloc[idx]

    @classmethod
    def set_speedparams(cls, root):
        cls.ev_speed_params = pickle.load(open(root / "Zeitabhängige Geschwindigkeit.pickle", "rb"))

    def is_first_trip(self) -> bool:
        return len(self.trips) == 0

    def drive(self, distance):
        trip_consumption = distance * (self.consumption / 100)
        self.SOC = self.SOC - (trip_consumption / self.capacity) * 100

    def check_distance(self, distance):
        """ check if SOC of the car is sufficitent for the given distance """
        trip_consumption = distance * (self.consumption / 100)
        if trip_consumption < (self.SOC / 100) * self.capacity:
            return True
        else:
            return False

    def max_distance(self):
        """ Calculates max distance that can be driven with current SOC """
        max_dist = round(((self.SOC / 100) * self.capacity / self.consumption) * 100, 2)
        return max_dist

    def check_charge(self, last_trip, distance=None):
        """ Checks whether to charge the car or not depending on the charging scenario """
        if self.SOC == 100:
            return False

        location = self.trips[len(self.trips) - 1].whyto
        # obere Schranke der Ladezeit, tatsächliche wird in self.charge() bestimmt
        duration = self.trips[len(self.trips) - 1].stay_duration
        if ElectricVehicle.CHARGE_SCEN < 4:
            if ElectricVehicle.CHARGE_SCEN == 1:
                # geladen wird nur wenn sich das Fahrzeug sich Zuhause befindet und sich dort länger als 15 Minuten
                # aufhält
                if location == 0 and duration > 15:
                    return True
            elif ElectricVehicle.CHARGE_SCEN == 2:
                # geladen wird nur wenn sich das Fahrzeug Zuhause oder auf der Arbeit befindet und sich dort länger
                # als 15 Minuten aufhält
                if (location == 0 or location == 1) and duration > 15:
                    return True

            elif ElectricVehicle.CHARGE_SCEN == 3:
                # geladen wird in jedem Zustand, sofern die Parkdauer 15 Minuten übersteigt
                if duration > 15:
                    return True
        # Fuzzy Ladeszenario
        else:
            # Wenn über Nacht am Wohnort dann laden
            if location == 0 and last_trip:
                return True
            # bei letztem Trip keine nächste Distanz
                # dann nächste Distanz = Tagesfahrleistung
            if not distance:
                distance = sum([trip.distance for trip in self.trips])
            fuzzy_ctrl = ElectricVehicle.fuzzy_ctrl
            fuzzy_ctrl.input['SOC'] = self.SOC
            fuzzy_ctrl.input['Entfernung nächster Fahrt'] = distance
            # Zustand Wohnort und Arbeitsplatz in Fuzzy Regelung = 1, 2 anstatt 0, 1
            if location == 0 or location == 1:
                fuzzy_ctrl.input['Zustand'] = location + 1
            # Übrige Zustände = Sonstwo (3)
            else:
                fuzzy_ctrl.input['Zustand'] = 3
            fuzzy_ctrl.input['Aufenthaltsdauer'] = duration
            # Berechne Wahrscheinlichkeit
            fuzzy_ctrl.compute()
            p = fuzzy_ctrl.output['Ladewahrscheinlichkeit']
            choice = random.random()
            if choice <= (p / 100):
                return True
            else:
                return False

    @staticmethod
    def get_charge_power(loc):
        """
        Returns the charging power when using [[var_power]] within the simulation. Values for the charging powers and
        their respective probabilities have been manually calculated based on evaluation of accessible data.
        """
        # Laden Zuhause
        if loc == 0:
            c_vals = [2.3, 3.7, 11, 22]
            probs = [0.6702, 0.2021, 0.0639, 0.0638]
        # Laden öffentlich / Arbeitsplatz
        else:
            c_vals = [3.7, 11, 22, 43, 50, 150, 350]
            probs = [0.0099, 0.0827, 0.7819, 0.0423, 0.0445, 0.0117, 0.027]
        power = np.random.choice(c_vals, p=probs)
        return power

    def charge(self, var_power):
        """ Calculation of charging times, as well as updating of the SOC of the ev """
        # Fahrzeug befindet sich im Zielzustand des letzten Trips
        trip = self.trips[len(self.trips) - 1]

        if var_power:
            loc = trip.whyto
            pcharge = self.get_charge_power(loc)
        # wenn Regionalisierung Ladeleistung = 3.7 kw am Wohnort an anderen Orten 22 kW
        elif ElectricVehicle.is_regio:
            if trip.whyto == 0:
                pcharge = ElectricVehicle.PCHARGE_SLOW
            else:
                pcharge = ElectricVehicle.PCHARGE_FAST
        else:
            pcharge = ElectricVehicle.PCHARGE_SLOW
        trip.p_charge = pcharge
        # nötige Zeit zum vollständigen Aufladen in Minuten
        t_charge_full = (((100 - self.SOC) / 100 * self.capacity) / pcharge) * 60
        # Ladezeit beschränkt durch Zeit zum vollständigen Aufladen und Länge des Aufenthalts
        t_charge = min(t_charge_full, trip.stay_duration)
        # update SOC über Ladedauer und Ladeleistung
        self.SOC = self.SOC + ((t_charge / 60 * pcharge) / self.capacity) * 100
        trip.charge_start = int(trip.arrival)
        trip.charge_end = int(trip.charge_start + t_charge)

    def speed(self, dist, departure_t):
        """ Calculate the average speed of the car based on the distance and the time intervall of departure """
        # Anzahl an Zeitintervallen für welche Geschwindigkeitsfunktion parametriert wurde
        speed_intervals = len(self.ev_speed_params)
        # Faktor zum Zuordnen des 15-minütigen Intervalls zu entsprechender Geschwindigkeitsfunktion
        interval_divisor = speed_intervals / 96
        func_no = int(departure_t * interval_divisor)
        speed = ElectricVehicle.ev_speed_params[func_no][0] + ElectricVehicle.ev_speed_params[func_no][
            1] * np.log(dist)
        lower_bound = ElectricVehicle.ev_speed_params[func_no][2]
        return max(lower_bound, speed)
