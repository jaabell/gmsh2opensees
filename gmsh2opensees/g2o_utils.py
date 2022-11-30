# Set of helper functions to interface gmsh with opensees 
#
# Questions to jaabell@uandes.cl
#
# 2022 - Jose A. Abell M. - www.joseabell.com

import os

if os.name == 'nt':
	import openseespy.opensees as ops
else:   #not checked in mac
	import opensees as ops



from numpy import array, int32, double, concatenate, unique, setdiff1d, zeros
from numpy.linalg import norm





def get_physical_groups_map(gmshmodel):
	"""
	Given the gmsh model, return a map of all defined physical groups and their names.
	The map will return the dimension and rag of the physical group if indexed by name
	"""
	pg = gmshmodel.getPhysicalGroups()
	the_physical_groups_map = {}
	for dim, tag in pg:
		name = gmshmodel.getPhysicalName(dim, tag)
		the_physical_groups_map[name] = (dim, tag)

	return the_physical_groups_map



