//+
SetFactory("OpenCASCADE");
Rectangle(1) = {-2, -.25, 0, 0.5, 0.5, 0};

//+
Extrude {{0, 1, 0}, {0, 0, 0}, Pi} {
  Surface{1}; 
}
//+
Rotate {{0, 0, 1}, {0, 0, 0}, -Pi/2} {
  Duplicata { Volume{1}; }
}
//+
BooleanUnion{ Volume{1}; Delete; }{ Volume{2}; Delete; }

//+
Physical Volume("Solid", 53) = {1};
//+
Physical Surface("Fixed", 54) = {2, 13, 9, 21};
//+
Physical Point("Load", 55) = {24};
