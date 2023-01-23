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

from gmsh2opensees.g2o_utils import get_physical_groups_map
from gmsh2opensees.g2o_nodes_functions import get_all_nodes

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
		1         : ( "2-node-line"         , 2       )  ,
		2         : ( "3-node-triangle"     , 3       )  ,
		3         : ( "4-node-quadrangle"   , 4       )  ,
		4         : ( "4-node-tetrahedron"  , 4       )  ,
		5         : ( "8-node-hexahedron"   , 8       )  ,
		11        : ( "10-node-tetrahedron" , 10      ) ,
		15        : ( "1-node-point"        , 1       )  ,
	}
	if elementType in info:
		return info[elementType]
	else:
		print(f"elementType={elementType} unavailable. Contributions welcome. See https://gmsh.info/doc/texinfo/gmsh.html#MSH-file-format")
		exit(-1)
