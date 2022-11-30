//+
SetFactory("OpenCASCADE");
Box(1) = {0, 0, 0, 1, 1, 1};
//+
Physical Volume("Solid", 13) = {1};
//+
Physical Surface("Fixed", 14) = {5};
//+
Physical Point("Load", 15) = {7};
