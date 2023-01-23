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



from numpy import array, int32, double, concatenate, unique, setdiff1d, zeros, cos, sin, pi, sqrt
from numpy.linalg import norm
from gmsh2opensees.g2o_nodes_functions import get_all_nodes, get_displacements_at_nodes, get_eigenvector_at_nodes


def visualize_displacements_in_gmsh(gmshmodel, nodeTags=[], viewnum=-1,step=0,time=0.,new_view_name="Displacements"):
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

	if len(nodeTags) == 0:
		allGmshNodeTags, _ = get_all_nodes(gmshmodel)	
	else:
		allGmshNodeTags = nodeTags
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



def visualize_eigenmode_in_gmsh(gmshmodel, mode=1, f=0, viewnum=-1,step=0,time=0.,new_view_name="Mode",animate=False,normalize=True, nsteps=10, factor=0.):
	"""
	Visualize eigenvector displacement field in gmsh, only for defined nodes.
	If view-number is not supplied, will create a new view. 
	If you want an animation, create the view outside (or call this function without specifying a view),
	this function will output the view number (handle), then you can call this with
	fata for subsequent steps by specifying a different step and time, but passing
	the view number. 
	
	Call once per time-step.

	You can also change the default name of the view 
	"""
	import gmsh

	allGmshNodeTags, coords = get_all_nodes(gmshmodel)
	eigenvector_data = get_eigenvector_at_nodes(allGmshNodeTags, mode)

	if viewnum==-1:
		viewnum = gmsh.view.add(new_view_name + f" {mode} {f=}")

	if not animate:

		gmsh.view.addHomogeneousModelData(
			tag=viewnum, 
			step=step,
			time=time, 
			modelName=gmsh.model.getCurrent(),
			dataType="NodeData",
			numComponents=-1,
			tags=allGmshNodeTags,
			data=eigenvector_data.reshape((-1))
		)

	else:

		for step in range(nsteps):
			gmsh.view.addHomogeneousModelData(
				tag=viewnum, 
				step=step,
				time=float(time), 
				modelName=gmsh.model.getCurrent(),
				dataType="NodeData",
				numComponents=-1,
				tags=allGmshNodeTags,
				data=(eigenvector_data*cos(step/nsteps*2*pi)).reshape((-1))
			)

	gmsh.view.option.setNumber(viewnum, "VectorType", 5)


	if factor == 0:
		dx = coords[:,0].max() - coords[:,0].min()
		dy = coords[:,1].max() - coords[:,1].min()
		dz = coords[:,2].max() - coords[:,2].min()
		eigenmax = abs(eigenvector_data).max()
		factor = 0.1 * sqrt(dx**2 + dy**2 + dz**2) / eigenmax

	gmsh.view.option.setNumber(viewnum, "DisplacementFactor", factor)

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

