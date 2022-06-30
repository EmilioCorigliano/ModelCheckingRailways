from os import system
import subprocess
import re
from model import model

t = """Options for the verification:
  Generating no trace
  Search order is breadth first
  Using conservative space optimisation
  Seed is 1656502343
  State space representation uses minimal constraint systems
←[2K
Verifying formula 1 at /nta/queries/query[1]/formula
←[2K -- Formula is satisfied.
←[2K
Verifying formula 2 at /nta/queries/query[2]/formula
←[2K -- Formula is satisfied.c, Load: 87 states←[K
←[2K
Verifying formula 3 at /nta/queries/query[3]/formula
←[2K -- Formula is satisfied.c, Load: 87 states←[K
←[2K
Verifying formula 4 at /nta/queries/query[4]/formula
←[2K -- Formula is satisfied., Load: 87 states←[K"""

# t0.SOC0 >= t0.Cdis*t0.estimatedTimeTravelling() #
# t0.SOCmax >= (maxDistance*t0.Cdis*60/t0.V)
distance0 = 8
distance4 = 10
maxDistance = 17
SOC0 = 60
SOCmax = 100

findTestsResults = r"Verifying formula (\d*)(?:.*?)Formula is(.*?)satisfied"

pathVerifyta = "verifyta.exe"
pathModelToVerify = "C:\\Users\\emili\\OneDrive - Politecnico di Milano\\Desktop\\Backup\\POLITECNICO\\4ANNO\\2-FORMAL METHODS FOR REAL-TIME SYSTEMS\\Homework\\modelToVerify.xml"


# pathHomework = "C:\\Users\\emili\\OneDrive - Politecnico di Milano\\Desktop\\Backup\\POLITECNICO\\4ANNO\\2-FORMAL METHODS FOR REAL-TIME SYSTEMS\\Homework\\Homework.xml"

def checkValidityInScript(Cdis, V):
    # t0.Init imply (t0.SOC >= t0.Cdis*t0.estimatedTimeTravelling())  # int estimatedTimeTravelling(){return nextDistance() * 60 / V}
    # t0.SOCmax >= (maxDistance*t0.Cdis*60/t0.V)
    if (SOC0 >= Cdis * (distance4 * 60 / V)) and (SOCmax >= maxDistance * Cdis * 60 / V):
        return True

    return False


def parseResults(res):
    asserts = []
    regResults = re.findall(findTestsResults, res, re.DOTALL)
    for a in regResults:
        if (a[1] == ' NOT '):
            asserts.append(0)
        elif (a[1] == ' '):
            asserts.append(1)
        else:
            print(a)
            asserts.append(2)

    return asserts


def checkProperties(asserts, i, f):
    for a in asserts[i:f]:
        if (a != 1):
            return False

    return True


# def checkValidity(asserts):
#    return checkProperties(asserts, 0, 2)


def checkEnoughSOC(asserts):
    return checkProperties(asserts, 0, 1)


def checkInTime(asserts):
    return checkProperties(asserts, 1, 2)


# def checkDeadlock(asserts):
#    return checkProperties(asserts, 4, 5)


# def checkLivelock(asserts):
#    return checkProperties(asserts, 9, 19)


def generateModel(strategy, minTimeInStation, Crec, Cdis, V):
    with open(pathModelToVerify, "w") as modelToCheck:
        modelToCheck.write(model.format(strategy=strategy,
                                        minTimeInStation=minTimeInStation,
                                        Crec=Crec,
                                        Cdis=Cdis,
                                        V=V)
                           )
    print(f"\nCreated model for str={strategy}, timeInStation={minTimeInStation}, Crec={Crec}, Cdis={Cdis}, V={V}")


def plot(x, y, z, status):
    pass


def restartFromLastChecked(lastChecked, minTimeInStation, strategy, Crec, Cdis, V):
    if (lastChecked[0] < minTimeInStation):
        return True
    elif (lastChecked[0] > minTimeInStation):
        return False
    else:
        if (lastChecked[1] < strategy):
            return True
        elif (lastChecked[1] > strategy):
            return False
        else:
            if (lastChecked[2] < Crec):
                return True
            elif (lastChecked[2] > Crec):
                return False
            else:
                if (lastChecked[3] < Cdis):
                    return True
                elif (lastChecked[3] > Cdis):
                    return False
                else:
                    if (lastChecked[4] < V):
                        return True
                    elif (lastChecked[4] >= V):
                        return False


# retryTime = [1]  # R -> fixed to 1
chargingStrategies = [1, 2]
minTimeInStations = [1] # [1, 2, 3, 4]
Crecs = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
Cdiss = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
Vs = [120, 150, 180, 210, 240]

lastChecked = [0, 0, 0, 0, 0]  # [1, 2, 3, 10, 150]
timeout = 7 * 60  # seconds: 10 minutes

with open("dataModels5-spedUp.csv", "a") as csv:
    csv.write("strategy,minTimeInStation,Crec,Cdis,V,status\n")
    for minTimeInStation in minTimeInStations:
        for strategy in chargingStrategies:
            # create a new graph
            axisCrec = []
            axisCdis = []
            axisV = []
            status = []  # 0 = failed both; 1 = not enough SOC; 2 = exceeded max delay; 3 = passed both

            # make all the checks for the specific model
            for Crec in Crecs:
                for Cdis in Cdiss:
                    for V in Vs:
                        if not restartFromLastChecked(lastChecked, minTimeInStation, strategy, Crec, Cdis, V):
                            continue

                        # for time constraints we check the validity in the script
                        if checkValidityInScript(Cdis, V):
                            # generate the file for the model
                            generateModel(strategy, minTimeInStation, Crec, Cdis, V)

                            verified = 0
                            asserts = [0, 0, 0, 0, 0, 0, 0, 0]
                            # executing the verification of the model with UPPAAL
                            try:
                                output = subprocess.run([pathVerifyta, pathModelToVerify], stdout=subprocess.PIPE,
                                                        stderr=subprocess.DEVNULL, timeout=timeout)
                                asserts = parseResults(output.stdout.decode('utf-8'))
                                verified = (checkInTime(asserts) << 1) + checkEnoughSOC(asserts)
                            except subprocess.TimeoutExpired:
                                verified = -1
                                print(f"\tSKIPPED: verification took more than {timeout} seconds: terminated")

                            # parsing the result of the checks
                            print("\tENOUGH SOC: " + str(checkEnoughSOC(asserts)) +
                                  "\tMAX DELAY: " + str(checkInTime(asserts)) + " " +
                                  "\tResult: " + str(verified))
                            csv.write(f"{strategy},{minTimeInStation},{Crec},{Cdis},{V},{verified}\n")
                            axisCrec.append(Crec)
                            axisCdis.append(Cdis)
                            axisV.append(V)
                            status.append(verified)
                        else:
                            print("\nNOT CORRECT!")
                            # print("\tCORRECT: " + str(checkValidity(asserts)))  # "\tDEADLOCK: " + str(
                            # checkDeadlock(asserts)) + "\tLIVELOCK: " + str(checkLivelock(asserts)))

            plot(axisCrec, axisCdis, axisV, status)

# print(re.findall(findTestsResults, output.stdout.decode('utf-8'), re.DOTALL))
# print(re.findall(findTestsResults, t, re.DOTALL))
