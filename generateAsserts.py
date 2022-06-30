

trains = range(5)
stations = ["MC", "ML", "Tr", "RL", "Ch", "Ro", "Bs"]

# A[]
assertMaxSOC = "t{x}.SOC <= t{x}.SOCmax and "

# A[]
assertGoingBackwards = "(t{x}.lastStation==0 imply t{x}.goingForward==1) and (t{x}.lastStation==(N_STATIONS-1) imply t{x}.goingForward==0) and"

# A[]
assertStationsMaxCapacity = "{x}.N <= {x}.capacity and "

# A[]
assertStationsMinCapacity = "{x}.N >= 0 and "

# A[]
assertEnoughSOC0 = "(t{x}.Init imply (t{x}.SOC >= t{x}.Cdis*t{x}.estimatedTimeTravelling())) and"


# A[]
assertTimeTravelling = "(t{x}.waitToEnter imply (t{x}.timeTravelling <= t{x}.maximumTimeAvailable())) and "

# -->

for i in trains:
    print(assertTimeTravelling.format(x=i))