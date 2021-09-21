Developer Documentation
=======================

It is relatively straightforward to extend Mt. Data in various ways.
The documentation below walks through several common tasks such as
adding a new dataset.

.. toctree::
   :maxdepth: 1
   :caption: Contents:

   modules

Adding a Dataset
----------------

A dataset is implemented as a sub-class of the `Dataset` abstract
class in the :mod:`mtdata.datasets` module. Once the dataset
is implemented, add the class to the list in
:mod:`mtdata.manifest`. Once this is done, the new dataset
will run by default when the `mtdata` module is run.

It may be easiest to adapt an existing dataset, e.g.
:mod:`mtdata.datasets.air_quality`. See
:mod:`mtdata.dataset` for specific documentation on
:class:`mtdata.dataset.Dataset` methods.

Adding a Store
--------------


