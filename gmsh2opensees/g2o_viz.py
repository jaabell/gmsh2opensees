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
	this function will output the view number (handle), then you can call this with
	fata for subsequent steps by specifying a different step and time, but passing
	the view number. 
	
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


def visualize_eleResponse_in_gmsh(gmshmodel, eleTags, args, viewnums=[],step=0,time=0.,new_view_name=f"eleResponse"):
	"""
	Visualize a per-element field in gmsh, only for defined elements.
	If the eleResponse is a vector, will add as many views as vector
	components.

	If view-number is not supplied, will create a new view. 
	If you want an animation, create the view outside (or call this function without specifying a view),
	this function will output the view number (handle), then you can call this with
	fata for subsequent steps by specifying a different step and time, but passing
	the view number. 
	
	Call once per time-step.

	You can also change the default name of the view 
	"""
	import gmsh


	one_eleResponse_data = ops.eleResponse(eleTags[0], args)

	print(f"eleResponse({args=}) for {eleTags[0]=} = {one_eleResponse_data}")

	Ncomponents = len(one_eleResponse_data)
	Nelements = len(eleTags)

	eleResponse_data = zeros((Nelements, Ncomponents))

	for i, eleTag in enumerate(eleTags):
		eleResponse_data[i,:] = ops.eleResponse(eleTag, args)

	if len(viewnums)==0:
		for i in range(Ncomponents):
			viewnums.append(gmsh.view.add(new_view_name + f" {i}"))

	print(f"{eleTags=}")
	print(f"{eleResponse_data=}")

	for i in range(Ncomponents):
		gmsh.view.addHomogeneousModelData(
			tag=viewnums[i], 
			step=step,
			time=time, 
			modelName=gmsh.model.getCurrent(),
			dataType="ElementData",
			numComponents=-1,
			tags=eleTags,
			data=eleResponse_data[:,i].reshape((-1))
		)

	return viewnums

