import opensees as ops
import gmsh2opensees as g2o
import gmsh

gmsh.initialize()
gmsh.open("example2.msh")


ops.model("basicBuilder","-ndm",3,"-ndf",3)

#Add solid material model
solidMaterialTag =  1
E = 210e9  # Pa
nu = 0.3   # - 
rho = 7300. # kg / m³ 
g = 9.81    # m/s²
ops.nDMaterial('ElasticIsotropic', solidMaterialTag, E, nu, rho)

elementTags, nodeTags, elementName, elementNnodes =g2o.get_elements_and_nodes_in_physical_group("Solid", gmsh.model)


g2o.add_nodes_to_ops(nodeTags, gmsh.model)




tetElementTags = elementTags

#Add solid elements
for eleTag, eleNodes in zip(elementTags, nodeTags):
	ops.element('FourNodeTetrahedron', eleTag, *eleNodes, solidMaterialTag, 0., 0., -rho*g)


elementTags, nodeTags, elementName, elementNnodes = g2o.get_elements_and_nodes_in_physical_group("Fixed", gmsh.model)

g2o.fix_nodes(nodeTags, "XYZ")


#add a load
ts_tag = 1
ops.timeSeries('Constant', ts_tag)

patternTag = 1
ops.pattern('Plain', patternTag, ts_tag)

ops.eleLoad("-ele", *tetElementTags, "-type", "-selfWeight", 0, 0, 2.)

# loaded_node = 209
# Fx = 0.
# Fy = 0.
# Fz = -10000  #N
# ops.load(loaded_node, Fx, Fy, Fz)

# ops.printModel()

ops.system("UmfPack")
ops.numberer("Plain")
ops.constraints('Plain')
ops.integrator("LoadControl", 1.0)
ops.algorithm("Linear")

ops.analysis("Static")

ops.analyze(1)

g2o.visualize_eleResponse_in_gmsh(gmsh.model, tetElementTags, "stresses", new_view_name="stress")

viewnum = g2o.visualize_displacements_in_gmsh(gmsh.model)

for viewnum in range(2,8):
	gmsh.view.option.setNumber(viewnum, "Visible", 0)



gmsh.fltk.run()


gmsh.finalize()
