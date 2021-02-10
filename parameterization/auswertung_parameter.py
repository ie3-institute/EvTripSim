#
# @ 2021. TU Dortmund University,
# Institute of Energy Systems, Energy Efficiency and Energy Economics,
# Research group Distribution grid planning and operation
#
from parameterization.abfahrtszeit import get_departure
from parameterization.zustandsverteilung import calc_zustandsverteilung
from parameterization.zwischenstopp import get_stopoverprobs
from parameterization.übergang import get_transition_probs
from parameterization.geschwindigkeit import get_speed
from parameterization.wegstrecken import get_distances
from parameterization.aufenthaltsdauer import get_stayduration

# 1 = Werktag ; 2 = Samstag ; 3 = Sonntag
from utilities import get_mid_data, save_params


# Auswertung der Parameter der Fahrtensimulation aus den MiD-Fahrten
def update_all():
    for type_day in range(1, 4):

        data = get_mid_data(type_day)

        get_stayduration(type_day)

        get_speed(type_day)

        get_departure(type_day)

        get_transition_probs(type_day)

        get_distances(type_day)

        states = calc_zustandsverteilung(data)

        save_params(type_day, "Zustandsverteilung", states)

        get_stopoverprobs(type_day)


