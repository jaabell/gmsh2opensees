gmsh2opensees
=============
A simple python module to use gmsh and opensees together in python. 

![gmsh2opensees](/example.png)
A deformed shape created with this tool. 

Dependencies
------------

You need to have [openseespy](openseespydoc.readthedocs.io) installed. Try

    pip install openseespy

or follow instructions at the openseespy website to compile your own. You also need gmsh python:

	pip install gmsh


Installation
------------

For now, only though the git repo::

	git clone git@github.com:jaabell/gmsh2opensees.git

Use the `setup.py` script, using setuptools, to compile and install::

	sudo python setup.py install

If you dont' have sudo, you can install locally for your user with::

	python setup.py install --user


Quick start
------------

In your python script include the library 

	import opensees as ops
	import gmsh2opensees as g2o

	# write your model

To run execute:

	python script_name.py

See more examples in the examples folder. 


Dependencies
------------

- `openseespy`
- `gmsh`
- `numpy`
