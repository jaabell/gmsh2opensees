//+
SetFactory("OpenCASCADE");
Rectangle(1) = {2, -0.25, 0, 0.5, 0.5, 0};
//+
Extrude {{0, 1, 0}, {0, 0, 0}, -Pi} {
  Surface{1}; 
}
//+
Rotate {{0, 0, 1}, {0, 0, 0}, Pi/2} {
  Duplicata { Volume{1}; }
}
//+
BooleanUnion{ Volume{1}; Delete; }{ Volume{2}; Delete; }
//+
Physical Surface("Fixed", 53) = {2, 9, 23, 17};
//+
Physical Volume("Solid", 54) = {1};
