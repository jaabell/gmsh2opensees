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




def get_all_nodes(gmshmodel):
	"""
	See function name. Return all node tags defined in the gmsh model, and their coordinates. 
	Only for 3-D models
	"""
	dim = -1  
	tag = -1
	nodeTags, coords, parametricCoord = gmshmodel.mesh.getNodes(dim, tag)

	return array(nodeTags, dtype=int), array(coords, dtype=double).reshape((-1,3))





def add_nodes_to_ops(nodeTags, gmshmodel, remove_duplicates=True):
	"""
	Adds nodes in list nodeTags (coming from one of the other functions in this library)
	to the opensees model. Possibly can avoid duplicates by setting the remove_duplicates flag. 
	"""

	#Flatten the nodeTags array and remove duplicate nodes within the physical group
	nodeTags = unique(array(nodeTags, dtype=int).reshape(-1))

	#Remove global duplicates if need be
	if remove_duplicates:
		defined_nodes = ops.getNodeTags()
		nodeTags = setdiff1d(nodeTags, defined_nodes)

	for nodeTag in nodeTags:
		coord, parametricCoord, dim, tag = gmshmodel.mesh.get_node(nodeTag)
		ops.node(int(nodeTag), *coord)





def fix_nodes(nodeTags, dofstring, verbose=False):
	"""
	Don't worry, the nodes are not broken. The nodes are fine. 
	This fixes the nodes in the sense of adding mechanical fixities.

	give a list of nodeTags (coming from one of the other functions herein)
	and a dofstring (such as "XYZ" if you want to fix all dofs or just "x" if you want
	to fix the singe x-direction DOF). The dofstring is case insensitive and
	letters other than xyz and repetitions will be ignored.

	Only supports 3-DOF nodes
	"""

	#Flatten the nodeTags array and remove duplicate nodes
	nodeTags = unique(array(nodeTags).reshape(-1))
	
	#Identify DOFs to be fixed
	fixX = 1 if dofstring.lower().find("x") >= 0 else 0
	fixY = 1 if dofstring.lower().find("y") >= 0 else 0
	fixZ = 1 if dofstring.lower().find("z") >= 0 else 0
	for i, tag in enumerate(nodeTags):
		if verbose:
			print(f"fixing {tag} {fixX}, {fixY}, {fixZ}")
		ops.fix(int(tag), fixX, fixY, fixZ)




def get_displacements_at_nodes(nodeTags):
	"""
	Helper function to return an array of noda displacements corresponding to 
	a list of node tags
	"""
	nodeTags = unique(array(nodeTags).reshape(-1))

	Nnodes = len(nodeTags)

	disps = zeros((Nnodes,3),dtype=float)

	for i, tag in enumerate(nodeTags):
		tag = int(tag)
		disps[i,:] = [ops.nodeDisp(tag,1),
			ops.nodeDisp(tag,2),
			ops.nodeDisp(tag,3)]

	return disps


def get_eigenvector_at_nodes(nodeTags, mode=1):
	"""
	Helper function to return an array of noda displacements corresponding to 
	a list of node tags
	"""
	nodeTags = unique(array(nodeTags).reshape(-1))

	Nnodes = len(nodeTags)

	disps = zeros((Nnodes,3),dtype=float)

	for i, tag in enumerate(nodeTags):
		tag = int(tag)
		disps[i,:] = [ops.nodeEigenvector(tag,mode,1),
			ops.nodeEigenvector(tag,mode,2),
			ops.nodeEigenvector(tag,mode,3)]

	return disps