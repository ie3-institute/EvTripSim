#
# @ 2021. TU Dortmund University,
# Institute of Energy Systems, Energy Efficiency and Energy Economics,
# Research group Distribution grid planning and operation
#
from collections import Counter
from utilities import get_mid_data, save_params


# empirische Wahrscheinlichkeiten der initialen Abfahrtszeiten berechnen und speichern
def get_departure(type_day):
    data = get_mid_data(type_day)
    filt = data["Trip_no"] == 1
    # Alle Abfahrtszeiten der ersten Trips des Tages
    first_trip = data[filt]["Departure"]
    # Dictionary mit "Zeitpunkt : Häufigkeit"
    first_trip_count = Counter(first_trip)
    # neues Dictionary mit "Zeitpunkt : rel. Häufigkeit"
    time_prob_dict = {}
    total = sum(first_trip_count.values())
    for key in first_trip_count:
        time_prob_dict[key] = first_trip_count[key] / total
    # speichern des Ergebnisses
    save_params(type_day, "Abfahrtszeit", time_prob_dict)