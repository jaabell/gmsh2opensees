#Import gmsh and load the mesh we generated
import gmsh
gmsh.initialize()
gmsh.open("example2.msh")

#Import opensees and the tools
import opensees as ops
import gmsh2opensees as g2o



#We'll add 3-DOF nodes
ops.model("basicBuilder","-ndm",3,"-ndf",3)

#Add solid material model
solidMaterialTag =  1
E = 200e9
nu = 0.3
rho = 7300.
ops.nDMaterial('ElasticIsotropic', solidMaterialTag, E, nu, rho)

#Add nodes from Soil physical group
elementTags, nodeTags, elementName, elementNnodes = g2o.get_elements_and_nodes_in_physical_group("Solid", gmsh.model)
g2o.add_nodes_to_ops(nodeTags, gmsh.model)

#Add solid elements
for eleTag, eleNodes in zip(elementTags, nodeTags):
	ops.element('FourNodeTetrahedron', eleTag, *eleNodes, solidMaterialTag)


#Apply fixities
elementTags, nodeTags, elementName, elementNnodes = g2o.get_elements_and_nodes_in_physical_group("Fixed", gmsh.model)
g2o.fix_nodes(nodeTags, "XYZ")





#Lets add the load at the tip of the beam
elementTags, nodeTags, elementName, elementNnodes = g2o.get_elements_and_nodes_in_physical_group("Load", gmsh.model)
loaded_node = nodeTags[0][0]

linear_ts_tag = 1
ops.timeSeries('Linear', linear_ts_tag)

patternTag = 1
ops.pattern('Plain', patternTag, linear_ts_tag)

Fx, Fy, Fz = 0., 0, -1000.

ops.load(loaded_node, Fx, Fy, Fz)




Nsteps = 1
ops.system("UmfPack")
ops.numberer("Plain")


# ops.constraints('Penalty', alphaS, alphaM)
ops.constraints('Plain')
ops.integrator("LoadControl", 1.0/Nsteps)
ops.algorithm("Newton")
ops.test('NormDispIncr',1e-8, 10, 1)

ops.analysis("Static")

ops.analyze(Nsteps)




g2o.visualize_displacements_in_gmsh(gmsh.model)

gmsh.fltk.run()


gmsh.finalize()

