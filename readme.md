# EV Tripsim

EV Tripsim is a tool to simulate trips of electric vehicles in order to generate load profiles of an ev fleet. The trip generation is parameterized by the results of the extensive german mobility study "Mobilität in Deutschland 2017" (for more information on the study see [here](http://www.mobilitaet-in-deutschland.de/)). Additionally a regionalisation approach is implemented to map trips to specific points-of-interest within a given area, with the help of OpenStreetMap Data. The points-of-interest that are currently used are from the city of Dortmund.

# Getting started

Clone the project, install the neccessary requirements and you should be good to go!

# How to run a simulation

## Folder Organisation

The project is divided into three main parts:

1.  Parameterization
    
    Within resides the jupyter notebook for preprocessing the MID Data Set, to ensure a sound database for parameterizing the simulation. Other than that the actual methods to extract the distribution of the individual trip parameters are located here.
    
2.  Execution
    
    Here you can find all parts for the trip simulation itself. For generating realistic trips the simulation uses the distributions that were evaluated during the Parameterization.
    
3.  Results
    
    Generated Trips will be written as a csv file into a corresponding folder `trips` within the result folder. Evaluations of load profiles and the distribution of cars to the different states throughout the day will be automatically saved in the `tripseval` folder.

## Executing a simulation

The entry point into the simulation is the `main` module at `./exection`. For parameterizing the simulation there are different parameters that can be set in advance.

### Input Parameters

**Configuration parameter:** `ev_total: int` With `ev_total` you can specify how many cars you want to simulate. For every car all trips for a day will be calculated and their respective charging processes.

**Configuration parameter:** `type_day: int`

Configures the type of the day for which cars are simulated. Choose the number that corresponds to the desired type.

```
    1: weekday
    2: saturday
    3: sunday
```

**Configuration parameter:** `charge_scen: int`

When a car arrives at a destination it has to be decided whether or not to charge the car. For that differen charging scenarios are utilised. Choose a number between 1 and 4.

```
    1: cars will only charge at home
    2: cars will charge at home and at work
    3: cars can charge anywhere
    4: fuzzy charging scenario
```

**Configuration parameter:** `file_name: str`

When done the results are written into a csv file with the name `file_name`

**Configuration parameter:** `var_power: bool`

The default configuration mainly uses 3.7 kW slow-charging. If you want to use variable charging power choose `var_power = True`.

Warning: Has'nt been used and tested enough.

**Configuration parameter:** `is_regio: bool`

When activated for every trip a POI will be assigned to the destination of trips. For that POIs of Dortmund are used.
