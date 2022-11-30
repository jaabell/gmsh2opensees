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
from gmsh2opensees.g2o_nodes_functions import get_all_nodes, get_displacements_at_nodes


def visualize_displacements_in_gmsh(gmshmodel, viewnum=-1,step=0,time=0.,new_view_name="Displacements"):
	"""
	Visualize displacement field in gmsh, only for defined nodes.
	If view-number is not supplied, will create a new view. 
	If you want an animation, create the view outside (or call this function without specifying a view),
	then call with a different step and time number. 
	Call once per time-step.

	You can also change the default name of the view 
	"""
	import gmsh

	allGmshNodeTags, _ = get_all_nodes(gmshmodel)
	displacement_data = get_displacements_at_nodes(allGmshNodeTags)

	if viewnum==-1:
		viewnum = gmsh.view.add(new_view_name)

	gmsh.view.addHomogeneousModelData(
		tag=viewnum, 
		step=step,
		time=time, 
		modelName=gmsh.model.getCurrent(),
		dataType="NodeData",
		numComponents=-1,
		tags=allGmshNodeTags,
		data=displacement_data.reshape((-1))
	)

	return viewnum
