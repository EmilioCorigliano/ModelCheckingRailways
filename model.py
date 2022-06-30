model = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE nta PUBLIC '-//Uppaal Team//DTD Flat System 1.1//EN' 'http://www.it.uu.se/research/group/darts/uppaal/flat-1_2.dtd'>
<nta>
	<declaration>// Place global declarations here
/**
 * 1: Just the time necessary to arrive without exceeding the maximum delay
 * 2: filling all the battery every time
*/
const int chargingStrategy = {strategy}; 
/** resubmission time [min] */
const int R = 1;          
/** Minimum time to pass in a station [min] */      
const int minTimeInStation = {minTimeInStation}; 

const int N_STATIONS = 7; // Number of stations 

// channels
chan entry[N_STATIONS], accepted[N_STATIONS], departed[N_STATIONS];
broadcast chan rejected[N_STATIONS];

/// Railway
typedef struct {{
    int distance;     // in km
    int maxDelay;     // in min
}} Link;

const Link railway_small[N_STATIONS-1] = {{
    {{8, 5}},  // Milano Centrale - Milano Lambrate
    {{17, 5}},  // Milano Lambrate - Treviglio
    {{13, 5}},  // Treviglio - Romano
    {{13, 5}},  // Romano - Chiari
    {{10, 5}},  // Chiari - Rovato
    {{15, 5}}  // Rovato - Brescia
}};

const Link railway[N_STATIONS-1] = railway_small;

int maxTimeForStations(){{
    int maxDistance = 0;
    int i=0;
    for(i=0; i&lt;N_STATIONS-1; i++){{
        maxDistance = maxDistance &gt;? railway[i].distance;
    }}
    return maxDistance;
}}

const int maxDistance = maxTimeForStations();
</declaration>
	<template>
		<name>Train</name>
		<parameter>const int C0, const int Cmax, const int pV, const int pCdis, const int pCrec, const int station, const bool forward</parameter>
		<declaration>const int SOCmax = Cmax;           // State Of Charge [min]
const int V = pV;               // Speed [Km/h]
int SOC = C0;              // State Of Charge [min]
const int Cdis = pCdis;            // Rate of discharge [min/min_discharge]
const int Crec = pCrec;            // Rate of recharge  [min/min_recharge]
int nTimesRetried = 0;       // Times the train had to request the entering to the station
int[0,N_STATIONS-1] lastStation = station;   // index of the last station where the train has been (or is)
bool goingForward = forward; // direction of the train
clock timeInStation;         // time spent charging the battery
clock timeTravelling;        // time spent discharging the battery
clock timeForResubmission;

int maxTimeForNextStation;   // Debug info

bool isGoingForward(bool actualState){{
    return (lastStation == 0 ? 
        true : 
        (lastStation == (N_STATIONS-1) ? 
            false : 
            actualState)
    );
}}

int nextStation(){{
    return goingForward ? lastStation+1 : lastStation-1;
}}

int nextMaxDelay(){{
    return (goingForward ? railway[lastStation].maxDelay : railway[lastStation-1].maxDelay);
}}

int nextDistance(){{
    return (goingForward ? railway[lastStation].distance : railway[lastStation-1].distance);
}}
int estimatedTimeTravelling(){{
    return nextDistance() * 60 / V;
}}

int maximumTimeAvailable(){{
    return (estimatedTimeTravelling() + nextMaxDelay());
}}

int maximumTimeRequired(){{
    // selecting policy of recharging [min]
    int timeToRecharge = 0;
    if(chargingStrategy == 1){{
        // Just the time necessary to arrive without exceeding the maximum delay
        timeToRecharge = maximumTimeAvailable();
    }} else if (chargingStrategy == 2) {{
        // filling all the battery every time
        timeToRecharge = SOCmax;
    }} else {{
        // PUT SOMETHING HERE
    }}

    /// policy of recharging
    return timeToRecharge;
}}

int calculateDischargedSOC(){{
    // return SOC - (Cdis*fint(timeTravelling));
    return SOC - (Cdis*(estimatedTimeTravelling() + nTimesRetried*R));
}}

int rechargeTimeRequired(){{
    /* convert maxTimeRequired in charge required for the battery, 
        take the amount of charge needed 
    */
    return ((((maximumTimeRequired()*Cdis - SOC)/Crec)+1) &gt;? 0);
}}


/**
    - true if the train exceeded the maximum delay
    - false if the train is still in the acceptable range
*/
bool exceededMaxDelay(){{
    return fint(timeTravelling) &gt; (estimatedTimeTravelling() + nextMaxDelay());
}}

/* State functions */
/**
    - updating lastStation
    - calculate the new discharged SOC
    - resetting clock
*/
void arrivedToNextStation(){{
    SOC = calculateDischargedSOC();

    lastStation = nextStation();
    goingForward = isGoingForward(goingForward);

    timeInStation = 0;
}}

/**
    - calculate the new recharged SOC
    - resetting clock
*/
void departing(){{
    SOC = ((SOC + Crec*rechargeTimeRequired()) &lt;? SOCmax);

    timeTravelling = 0;    
    maxTimeForNextStation = maximumTimeRequired(); // debug
}}

// TODO: check link railways indexes</declaration>
		<location id="id0" x="-44115" y="-44302">
			<name x="-44183" y="-44293">charging</name>
			<label kind="invariant" x="-44353" y="-44276">timeInStation &lt;= (rechargeTimeRequired() &gt;? minTimeInStation)</label>
		</location>
		<location id="id1" x="-43691" y="-44302">
			<name x="-43673" y="-44327">travelling</name>
			<label kind="invariant" x="-43673" y="-44310">timeTravelling &lt;= estimatedTimeTravelling()</label>
		</location>
		<location id="id2" x="-44115" y="-44480">
			<name x="-44208" y="-44488">waitToEnter</name>
			<urgent/>
		</location>
		<location id="id3" x="-43690" y="-44480">
			<name x="-43673" y="-44488">ArrivedOutsideOfStation</name>
			<urgent/>
		</location>
		<location id="id4" x="-43690" y="-44149">
			<name x="-43724" y="-44157">Init</name>
			<urgent/>
		</location>
		<location id="id5" x="-44115" y="-44667">
			<name x="-44148" y="-44718">askToEnter</name>
			<label kind="invariant" x="-44191" y="-44701">timeForResubmission &lt;= R</label>
		</location>
		<init ref="id4"/>
		<transition>
			<source ref="id4"/>
			<target ref="id1"/>
			<label kind="assignment" x="-43681" y="-44259">timeInStation = 0,
timeTravelling = 0,
goingForward = isGoingForward(goingForward),
nTimesRetried = 0</label>
		</transition>
		<transition>
			<source ref="id2"/>
			<target ref="id5"/>
			<label kind="synchronisation" x="-44055" y="-44608">rejected[nextStation()]?</label>
			<label kind="assignment" x="-44055" y="-44591">timeForResubmission = 0,
nTimesRetried++</label>
			<nail x="-44063" y="-44583"/>
		</transition>
		<transition>
			<source ref="id3"/>
			<target ref="id2"/>
			<label kind="synchronisation" x="-44055" y="-44480">entry[nextStation()]!</label>
			<label kind="assignment" x="-44055" y="-44463">nTimesRetried = 0</label>
			<nail x="-43979" y="-44480"/>
		</transition>
		<transition>
			<source ref="id0"/>
			<target ref="id1"/>
			<label kind="guard" x="-44098" y="-44302">timeInStation &gt;= (rechargeTimeRequired() &gt;? minTimeInStation)</label>
			<label kind="synchronisation" x="-43961" y="-44319">departed[lastStation]!</label>
			<label kind="assignment" x="-43936" y="-44336">departing()</label>
		</transition>
		<transition>
			<source ref="id2"/>
			<target ref="id0"/>
			<label kind="synchronisation" x="-44268" y="-44404">accepted[nextStation()]?</label>
			<label kind="assignment" x="-44260" y="-44387">arrivedToNextStation()</label>
		</transition>
		<transition>
			<source ref="id1"/>
			<target ref="id3"/>
			<label kind="guard" x="-43682" y="-44403">timeTravelling &gt;= estimatedTimeTravelling()</label>
		</transition>
		<transition>
			<source ref="id5"/>
			<target ref="id2"/>
			<label kind="guard" x="-44336" y="-44599">timeForResubmission &gt;= R</label>
			<label kind="synchronisation" x="-44293" y="-44582">entry[nextStation()]!</label>
			<nail x="-44166" y="-44574"/>
		</transition>
	</template>
	<template>
		<name>Station</name>
		<parameter>const int pIndex, const int pCapacity</parameter>
		<declaration>int index = pIndex;              // index that corresponds to this station in the channels array
const int capacity = pCapacity; // Max number of trains that the station can contain
int[0,capacity] N = 0;          // number of trains present in a station

void trainDeparted() {{
    N--;
}}

void trainArrived() {{
    N++;
}}

bool canEnter() {{
    return N&lt;capacity;
}}</declaration>
		<location id="id6" x="-204" y="-51">
			<name x="-187" y="-59">TrainsWaiting</name>
			<urgent/>
		</location>
		<location id="id7" x="-416" y="-51">
			<name x="-459" y="-59">Idle</name>
		</location>
		<init ref="id7"/>
		<transition>
			<source ref="id7"/>
			<target ref="id7"/>
			<label kind="synchronisation" x="-578" y="-68">departed[index]?</label>
			<label kind="assignment" x="-578" y="-51">trainDeparted()</label>
			<nail x="-467" y="-17"/>
			<nail x="-467" y="-76"/>
		</transition>
		<transition>
			<source ref="id7"/>
			<target ref="id6"/>
			<label kind="synchronisation" x="-348" y="-68">entry[index]?</label>
		</transition>
		<transition>
			<source ref="id6"/>
			<target ref="id7"/>
			<label kind="guard" x="-357" y="-178">canEnter()</label>
			<label kind="synchronisation" x="-357" y="-161">accepted[index]!</label>
			<label kind="assignment" x="-357" y="-144">trainArrived()</label>
			<nail x="-204" y="-127"/>
			<nail x="-416" y="-127"/>
		</transition>
		<transition>
			<source ref="id6"/>
			<target ref="id7"/>
			<label kind="guard" x="-357" y="8">!canEnter()</label>
			<label kind="synchronisation" x="-357" y="25">rejected[index]!</label>
			<nail x="-204" y="8"/>
			<nail x="-416" y="9"/>
		</transition>
	</template>
	<system>// Stations (#, capacity)
MC = Station(0, 5); // Milano Centrale
ML = Station(1, 4); // Milano Lambrate
Tr = Station(2, 3); // Treviglio
RL = Station(3, 2); // Romano di Lombardia
Ch = Station(4, 2); // Chiari
Ro = Station(5, 3); // Rovato
Bs = Station(6, 5); // Brescia

// Train instantiations 
// int SOC0, int SOCmax, int V, int pCdis, int pCrec, int station, bool forward
t0 = Train(60, 100, {V}, {Cdis}, {Crec}, 0, true);
t1 = Train(60, 100, {V}, {Cdis}, {Crec}, 0, true);
t2 = Train(60, 100, {V}, {Cdis}, {Crec}, 0, true);
t3 = Train(60, 100, {V}, {Cdis}, {Crec}, 4, true);
t4 = Train(60, 100, {V}, {Cdis}, {Crec}, 4, true);

/** 
 * With this model we will pass or fail the safety tests deciding the "chargingPolicy" 
 * in Declarations. With policy 1 we will pass, with policy 2 we will fail.
 */
/*
t0 = Train(60, 100, 120, 4, 12, 0, true);
t1 = Train(60, 100, 120, 4, 12, 0, true);
t2 = Train(60, 100, 120, 4, 12, 0, true);
t3 = Train(60, 100, 120, 4, 12, 4, true);
t4 = Train(60, 100, 120, 4, 12, 4, true);
*/

// List one or more processes to be composed into a system.
system t0, t1, t2, t3, t4, MC, ML, Tr, RL, Ch, Ro, Bs;</system>
	<queries>
		<query>
			<formula>A[] t0.SOC &gt;= 0 and 
t1.SOC &gt;= 0 and 
t2.SOC &gt;= 0 and 
t3.SOC &gt;= 0 and 
t4.SOC &gt;= 0</formula>
			<comment>SAFETY: Check that the trains will always have enough charge to reach the next station </comment>
		</query>
		<query>
			<formula>A[] (t0.waitToEnter imply (t0.timeTravelling &lt;= t0.maximumTimeAvailable())) and
(t1.waitToEnter imply (t1.timeTravelling &lt;= t1.maximumTimeAvailable())) and
(t2.waitToEnter imply (t2.timeTravelling &lt;= t2.maximumTimeAvailable())) and
(t3.waitToEnter imply (t3.timeTravelling &lt;= t3.maximumTimeAvailable())) and
(t4.waitToEnter imply (t4.timeTravelling &lt;= t4.maximumTimeAvailable()))</formula>
			<comment>SAFETY: Check that the trains will always reach the stations in time, not exceeding the maximum time available</comment>
		</query>
	</queries>
</nta>
"""