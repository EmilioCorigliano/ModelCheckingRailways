# ModelCheckingRailways
Repository for the Homework of "Formal Methods for Concurrent and Real-Time Systems" of the year 2022

In the root folder there is the UPPAAL modeling and the verification queries.

In the scripts folder there is:
- assertChecker.py: takes a model and verifies all his assertions. This must be a modified model so that we can vary the parameters of interest
- graphGenerator.py: from a csv file it takes the data and builds a 3D graph that shows graphically the impact of the variation of parameters on the safety of the model
- generateAsserts.py: just an helper script to generate long repetitive asserts

In the deliverables folder there is:
- the images produced by the graphGenerator.py script
- the report of the project
