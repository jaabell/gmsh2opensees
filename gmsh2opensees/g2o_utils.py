# Set of helper functions to interface gmsh with opensees for SSI analysis
#
# By Jose A. Abell
# Prepared for the OPENSEES DAYS EURASIA (2022) Conference 
# SECOND EURASIAN CONFERENCE ON OPENSEES
#
# This is a very limited example python file. You will probably need to adapt it 
# to your needs. 
#
# Questions to jaabell@uandes.cl
#
# 2022 - Jose A. Abell M. - www.joseabell.com

from numpy import array, int32, double, concatenate, unique, setdiff1d, zeros
from numpy.linalg import norm
import opensees as ops


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

# def rigid_link_between_one_node_and_many(free_node, contrained_nodes, type_of_link):

# 	#Flatten the nodeTags array and remove duplicate nodes
# 	contrained_nodes = unique(array(contrained_nodes).reshape(-1))
	
# 	#Identify DOFs to be fixed
# 	for i, tag in enumerate(contrained_nodes):
# 		ops.rigidLink(type_of_link, free_node, int(tag))


def duplicate_equaldof_and_beam_link(free_node, constrained_nodes, gmshmodel, start_duplicate_tag, start_beam_tag, transfTag, E_mod):
	"""
	This is the magic function that is used to interface the continuum domai with a MoM-based domain in OpenSees
	This is similar to STKO beam-to-solid coupling, but not as refined. 
	This is a penalty approach to this problem. Very sensitive to your selection of E_mod
	"""

	parent_coord, _, _, _ = gmshmodel.mesh.get_node(free_node)

	#Flatten the nodeTags array and remove duplicate nodes
	constrained_nodes = unique(array(constrained_nodes).reshape(-1))
	
	#Penalty beam properties
	Area = 1.0
	G_mod = 1.0
	Jxx = 1.0
	Iy = 1.0
	Iz = 1.0
	#Identify DOFs to be fixed
	for i, nodeTag in enumerate(constrained_nodes):
		coord, _, _, _ = gmshmodel.mesh.get_node(nodeTag)

		if norm(parent_coord - coord) < 1e-4:
			continue

		duplicate_tag = int(start_duplicate_tag+nodeTag)
		ops.node(duplicate_tag,*coord)
		ops.equalDOF(int(nodeTag), duplicate_tag, 1,2,3)
		# ops.rigidLink("beam", free_node, duplicate_tag)
		eleTag = start_beam_tag + i
		ops.element('elasticBeamColumn', eleTag, free_node, duplicate_tag, Area, E_mod, G_mod, Jxx, Iy, Iz, transfTag)




def get_elements_and_nodes_in_physical_group(groupname, gmshmodel):
	"""
	Returns element tags, node tags (connectivity), element name (gmsh element type name), and
	number of nodes for the element type, given the name of a physical group. Inputs are the physical
	group string name and the gmsh model 
	"""


	dim, tag  = get_physical_groups_map(gmshmodel)[groupname]  
	entities = gmshmodel.getEntitiesForPhysicalGroup(dim, tag)


	allelementtags = array([], dtype=int32)
	allnodetags = array([], dtype=int32)

	base_element_type = -1

	for e in entities:
		elementTypes, elementTags, nodeags = gmshmodel.mesh.getElements(dim, e)

		if len(elementTypes) != 1:
			print("Cannot handle more than one element type at this moment. Contributions welcome. ")
			exit(-1)

		if base_element_type == -1:
			base_element_type = elementTypes[0]
		elif elementTypes[0] != base_element_type:
			print("All entities of physical group should have the same element type. Contributions welcome. ")
			exit(-1)


		allelementtags = concatenate((allelementtags,elementTags[0]))
		allnodetags = concatenate((allnodetags,nodeags[0]))

	element_name, element_nnodes = get_element_info_from_elementType(base_element_type)
	allnodetags = allnodetags.reshape((-1,element_nnodes))

		
	return int32(allelementtags).tolist(), int32(allnodetags).tolist(), element_name, element_nnodes





def get_element_info_from_elementType(elementType):
	"""
	Returns element gmsh name and number of nodes given element type
	Can be extended to add other elements.
	"""
	info = {
	#  elementType    Name                  Number of nodes
		1         : ( "2-node-line"        ,        2       ) ,
		2         : ( "3-node-triangle"    ,        3       ) ,
		3         : ( "4-node-quadrangle"  ,        4       ) ,
		4         : ( "4-node-tetrahedron" ,        4       ) ,
		5         : ( "8-node-hexahedron"  ,        8       ) ,
		15        : ( "1-node-point"       ,        1       ) ,
	}
	if elementType in info:
		return info[elementType]
	else:
		print(f"elementType={elementType} unavailable. Contributions welcome. See https://gmsh.info/doc/texinfo/gmsh.html#MSH-file-format")
		exit(-1)


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
