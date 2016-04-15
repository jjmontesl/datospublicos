DatosPublicos
=============

Introduction
------------

This project intends to make public data easier to analyze.

It combines data from different sources and makes it available as an OLAP database
that can be examined in an analytical way.

DatosPublicos currently focuses on a few public Spanish government data sources. If you
wish to see data from other sources (which is publicly accessible) please get in touch.


Disclaimer
----------

As data is obtained from different datasources, we cannot make guarantees about the
accuracy of the provided data. There may also be bugs in the transformation phase
impacting the final result. Bottom line is: use at your own risk.

Please file an issue if you find any incorrect data.

Reference to source documents or websites is provided for
all datasets.


Technology
----------

This project is based on the open source [CubesViewer](https://github.com/jjmontesl/cubesviewer) project, using
[Cubes Server](http://databrewery.org/cubes.html) as OLAP backend.
Data processing is performed using a custom tool [CubETL](https://github.com/jjmontesl/cubetl).


Running ETL processes
---------------------

This repository contains the ETL processes used to build the database and data model used
by Cubes and CubesViewer to serve the data. It does not contain information about how to
set up CubesViewer (please refer to the respective sites for further information).

