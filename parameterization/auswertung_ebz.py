#
# @ 2021. TU Dortmund University,
# Institute of Energy Systems, Energy Efficiency and Energy Economics,
# Research group Distribution grid planning and operation
#
from parameterization.ebz import calc_ebz, save_midebz
from utilities import get_mid_data

# Berechne EBZ auf Basis der MiD-Fahrten
def calc_all(var_power):
    # Für jeden Tagtyp
    for day in range(1, 4):
        # Für jedes Ladeszenario
        for cs in range(1, 4):
            # Laden der MiD-Fahrten mit errechneten Ladezeiten gemäß Ladeszenario und Tagtyp
            data = get_mid_data(day, cs, var_power)
            # Berechne EBZ
            ebz = calc_ebz(data, var_power)
            # Speichern der Ergebnisse
            save_midebz(ebz, day, cs, var_power)


calc_all(var_power=False)



