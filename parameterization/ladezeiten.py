#
# @ 2021. TU Dortmund University,
# Institute of Energy Systems, Energy Efficiency and Energy Economics,
# Research group Distribution grid planning and operation
#
from execution.ev import ElectricVehicle
from execution.trip import init_trip
from utilities import get_mid_data, format_simresults, MID_DIR

# Simulieren von Ladezeiten für die MiD-Fahrten
def charging_times(var_power):
    for type_day in range(1, 4):
        for cs in range(1, 4):
            ElectricVehicle.CHARGE_SCEN = cs
            df = get_mid_data(type_day)
            total_evs = []
            ev = None
            for row in range(len(df)):
                # wenn aktueller Eintrag zu neuem Fahrzeug gehört
                if (df.at[row, "Trip_no"]) == 1 or (df.at[row, "ID"] != df.at[row - 1, "ID"] or (row == len(df)-1)):
                    if ev:
                        # lade zuletzt simuliertes Fahrzeug am finalen Aufenthaltsort
                        if ev.check_charge():
                            ev.charge(var_power)
                        # ablegen des Fahrzeugs in Liste
                        total_evs.append(ev)
                    # initialisiere neues Fahrzeug
                    ev = ElectricVehicle()
                # Trip initialisieren und entsprechende Variablen aus Datensatz übernehmen
                trip = init_trip(type_day, df.at[row, "Whyfrom"], df.at[row, "Departure"])
                trip.id = df.at[row, "ID"]
                trip.trip_no = df.at[row, "Trip_no"]
                trip.whyto = df.at[row, "Whyto"]
                trip.arrival = df.at[row, "Arrival"]
                trip.trip_duration = df.at[row, "Trip_duration"]
                trip.distance = df.at[row, "Distance"]
                trip.stay_duration = df.at[row, "Stay_duration"]
                trip.RegioStaR4 = df.at[row, "RegioStaR4"]
                if ev.check_charge():
                    ev.charge(var_power)
                trip.SOC_start = round(ev.SOC, 1)
                # Fahrvorgang -> update SOC
                ev.drive(trip.distance)
                trip.SOC_end = round(ev.SOC, 1)
                ev.trips.append(trip)

            data = format_simresults(total_evs)
            days = ["we", "sa", "so"]
            charge_scen = ["CS1", "CS2", "CS3"]
            path = MID_DIR + r"\Aufbereitete Daten\Ladezeiten"
            if var_power:
                filename = "Trips_{}_{}_Ladezeiten_vp.csv".format(days[type_day-1], charge_scen[cs-1])
            else:
                filename = "Trips_{}_{}_Ladezeiten.csv".format(days[type_day - 1], charge_scen[cs - 1])
            data.to_csv(path+"\\"+filename)


charging_times(var_power=False)
