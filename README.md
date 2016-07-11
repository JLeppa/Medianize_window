                   median_degree.py

Technical Details
-----------------

The program is written in Python 3.5 and it uses the following pre-built
modules, classes and functions:

    Module 'path' from module 'os'
    Function 'search' from module 're'
    Classes 'datetime' and 'timedelta' from module 'datetime'
    Function 'median' from module 'statistics'

What is it?
-----------

The program 'median_degree.py' calculates median degree of a venmo transaction graph.
The graph is a collection of nodes and edges between them, with the nodes representing
users involved in transactions during a running 60 second time window and edges
connecting the two users involved in each transaction. A degree of a node is the number
of edges connected to it.

The program was created by Johannes Leppä in July 2016 for the challenge part of 
application to the Data Engineering program of Data Insight.
