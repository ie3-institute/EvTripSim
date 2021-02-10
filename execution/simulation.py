#
# @ 2021. TU Dortmund University,
# Institute of Energy Systems, Energy Efficiency and Energy Economics,
# Research group Distribution grid planning and operation
#

from execution.ev import ElectricVehicle
from execution.trip import init_trip
from utilities import format_simresults, evaluate_save_simresults


class Simulation(object):
    """
    Simulationparameters:
        ev_total: int
            => number of cars to be simulated
        type_day: int
            => type of the day
                1: weekday
                2: saturday
                3: sunday
        charge_scen: int
            => charging scenario
                1: cars will only charge at home
                2: cars will charge at home and at work
                3: cars can charge anywhere
                4: fuzzy charging scenario
        file_name: str
            => filename of the result file
        var_power: bool
            => enable charging with variable charging power (warning: not extensively tested)
        is_regio: bool
            => enable regionalisation of trips
    """

    def __init__(self, ev_total: int, type_day: int, charge_scen: int,
                 filename: str, is_regio: bool, var_power: bool = False):
        self.ev_total = ev_total
        self.type_day = type_day
        self.charge_scen = charge_scen
        self.filename = filename
        self.var_power = var_power
        self.is_regio = is_regio
        self.config_ev(is_regio, charge_scen)
        print("_____________________\n")
        print("New simulation has been initialized.")
        days = ["weekday", "saturday", "sunday"]
        print("I'm simulating trips for {} cars on a perfectly average {}.".format(ev_total, days[type_day-1]))

    @classmethod
    def config_ev(cls, regio: bool, charge_scen: int):
        ElectricVehicle.set_regio(regio)
        ElectricVehicle.CHARGE_SCEN = charge_scen

    def simulate_day(self, day: int = 0) -> list:
        simulated_evs = []
        for car in range(self.ev_total):
            ev = ElectricVehicle()
            time = 0
            self.simulate_car(car, day, ev, time)
            simulated_evs.append(ev)
        return simulated_evs

    def simulate_car(self, car, day, ev, time):
        last_trip = False
        # Fahrten bis Tagesende (24:00)
        while time < 1440:
            if ev.is_first_trip():
                # erster Trip startet Zuhause
                trip = init_trip(type_day=self.type_day, whyfrom=0)
                # Abfahrtszeit = samplen der initialen Abfahrtszeit
                trip.sample_departure()
            else:
                # Ursprungszustand des nächsten Trips = Zielzustand des letzten Trips
                whyfrom = trip.whyto
                # initialisieren des anknüpfenden Trips
                trip = init_trip(type_day=self.type_day, whyfrom=whyfrom, departure=time)

            trip.sample_whyto()
            trip.sample_stayduration(ev.trips, time)
            trip.sample_distance()
            if ev.check_charge(trip.distance, last_trip):
                ev.charge(self.var_power)
            # Speichen des SOC zu Beginn des Trips
            trip.SOC_start = round(ev.SOC, 1)
            # Was tun wenn Energie des Trips die Restenergie der Batterie übersteigt
            if not ev.check_distance(trip.distance):
                # Distanz wird beschränkt auf maximal zurücklegbare Distanz mit aktuellem SOC
                trip.distance = max(0.05, ev.max_distance())
            # Fahrvorgang -> update SOC
            ev.drive(trip.distance)
            # Speichern des SOC des Fahrzeugs bei Ankunft
            trip.SOC_end = round(ev.SOC, 1)
            trip.av_speed = ev.speed(trip.distance, trip.departure_t)
            # Fahrtdauer über Weglänge und durchschnittliche Geschwindigkeit in Abhängigkeit der Trip Distanz
            trip.trip_duration = max(1, round((trip.distance / trip.av_speed) * 60))
            trip.arrival = trip.departure + trip.trip_duration
            trip.arrival_t = int(trip.arrival / 15)
            # Im Falle einer regionalisierten Simulation bestimme kategorischen Aufenthaltsort und POI
            if self.is_regio:
                trip.categ_location = trip.sample_categ_location(trip.whyto)
                poi = trip.sample_poi(ev.home)
                trip.poi_id = poi["osm_id"]
                trip.pp_id = trip.pick_nearest_pp(poi)
            # markieren der Trips die erst am nächsten Tag am Ziel ankommen
            if trip.arrival >= 1440:
                trip.overnight = 1
            else:
                trip.overnight = 0
            trip.id = car
            trip.day = day
            trip.type_day = self.type_day
            ev.trips.append(trip)
            ev.trip_no += 1
            trip.trip_no = ev.trip_no
            time = round(trip.arrival + trip.stay_duration)

        last_trip = True
        # Ladevorgang bei Ankunft vom letzten Trip
        if ev.check_charge(last_trip):
            ev.charge(self.var_power)
        ev.trips[-1].final_soc = ev.SOC

    def save_results(self, simulated_evs):
        data = format_simresults(simulated_evs)
        # Berechnung EBZ / Aufenthaltsverteilung und abspeichern aller Ergebnisse
        evaluate_save_simresults(data, type_day=self.type_day, filename=self.filename, var_power=self.var_power)


