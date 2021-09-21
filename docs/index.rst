.. Mt. Data documentation master file, created by
   sphinx-quickstart on Mon Sep 20 10:52:25 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Mt. Data
========

**Mt. Data** (pronounced "mount data", like "Mount Everest") is a
tool to help people collect and store (mountains of) public data
from a variety of sources.

.. toctree::
   :maxdepth: 1
   :caption: Contents:

   development

Installation
------------



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



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
