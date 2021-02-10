#
# @ 2021. TU Dortmund University,
# Institute of Energy Systems, Energy Efficiency and Energy Economics,
# Research group Distribution grid planning and operation
#
from simulation import Simulation

for regio in [True, False]:
    for type_day in [1, 2, 3]:
        for cs in [1, 2, 3, 4]:
            if regio:
                filename = "SimulationTestingRegioCs{}".format(cs)
            else:
                filename = "SimulationTestingCs{}".format(cs)
            sim = Simulation(ev_total=1000,
                             type_day=type_day,
                             charge_scen=cs,
                             filename=filename,
                             var_power=False,
                             is_regio=regio)
            simulated_evs = sim.simulate_day()

            sim.save_results(simulated_evs)

