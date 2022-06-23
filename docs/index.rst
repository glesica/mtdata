.. Mt. Data documentation master file, created by
   sphinx-quickstart on Mon Sep 20 10:52:25 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


.. toctree::
   :maxdepth: 1
   :hidden:

   development


.. mdinclude:: ../README.md


Installation
------------

There are two main ways to use Mt. Data, Pip and Docker.

Concepts
--------

A **dataset** is a collection of related data, usually a single
table. Each dataset knows how to download updates to the data,
how to transform fields names and values, and which fields are
useful for de-duplication.

A **store** is a means of persisting acquired data. For example,
a particular store might know how to talk to a database to save
data collected by datasets as database tables.

Usage
-----



* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
