import com.comsol.model.*;
import com.comsol.model.util.*;
import com.comsol.model.physics.*;

import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;

/**
 * BatchScrewSimulation.java
 *
 * Standalone COMSOL 6.2 Java API automation script.
 * Automates 3D linear static structural FEA simulations sequentially for:
 *   1. AS1_screw.step (Re-entrant Auxetic)
 *   2. AS2_screw.step (Chiral Auxetic)
 *   3. NS_screw.step  (Non-Auxetic Hexagonal Benchmark)
 *
 * Material: Ti-6Al-4V ELI (E = 110 GPa, nu = 0.33, rho = 4430 kg/m^3)
 * Boundary Conditions:
 *   - Fixed Tip: Coordinate Box Selection Y in [-0.5, 2.0] mm
 *   - Tensile Pull: Coordinate Box Selection Y in [28.0, 30.0] mm, Uy = 0.2 mm
 * Outputs:
 *   - D:/MBSE/<screwName>_results.csv
 *   - D:/MBSE/<screwName>_solved.mph
 */
public class BatchScrewSimulation {

    private static final String BASE_DIR = "D:/MBSE/";

    private static final String[] SCREW_NAMES = {
        "AS1_screw",
        "AS2_screw",
        "NS_screw"
    };

    public static void main(String[] args) {
        System.out.println("=============================================================");
        System.out.println(" BatchScrewSimulation — COMSOL Multiphysics 6.2 Java API");
        System.out.println(" 3D Auxetic Bone Screw Linear Static Structural FEA");
        System.out.println(" Total models to simulate: " + SCREW_NAMES.length);
        System.out.println("=============================================================");

        for (int i = 0; i < SCREW_NAMES.length; i++) {
            String screwName = SCREW_NAMES[i];
            String modelTag  = "Model_" + screwName;

            System.out.println("\n-------------------------------------------------------------");
            System.out.printf(" [%d/%d] STARTING SIMULATION: %s%n", i + 1, SCREW_NAMES.length, screwName);
            System.out.println("-------------------------------------------------------------");

            Model model = null;
            try {
                long tStart = System.currentTimeMillis();
                model = simulateScrew(screwName, modelTag);
                long tElapsed = (System.currentTimeMillis() - tStart) / 1000;
                System.out.printf(">>> [SUCCESS] %s completed in %d seconds.%n", screwName, tElapsed);

            } catch (Exception e) {
                System.err.println(">>> [ERROR] Simulation failed for: " + screwName);
                e.printStackTrace(System.out);

            } finally {
                if (model != null) {
                    try {
                        ModelUtil.remove(modelTag);
                        System.out.println("    Model " + modelTag + " cleared from memory.");
                    } catch (Exception ex) {
                        System.err.println("    Warning clearing model: " + ex.getMessage());
                    }
                }
            }
        }

        System.out.println("\n=============================================================");
        System.out.println(" BatchScrewSimulation — All 3 simulations finished!");
        System.out.println(" Results saved in: D:/MBSE/");
        System.out.println("=============================================================");
    }

    private static Model simulateScrew(String screwName, String modelTag) throws Exception {
        final String stepPath = BASE_DIR + screwName + ".step";
        final String csvPath  = BASE_DIR + screwName + "_results.csv";
        final String mphPath  = BASE_DIR + screwName + "_solved.mph";

        // 1. Initialize Model
        System.out.println(">>> [1/8] Creating component and geometry sequence...");
        Model model = ModelUtil.create(modelTag);
        model.modelNode().create("comp1");

        GeomSequence geom = model.component("comp1").geom().create("geom1", 3);
        geom.lengthUnit("mm");

        // 2. Import STEP CAD
        System.out.println(">>> [2/8] Importing CAD: " + stepPath);
        GeomFeature imp = geom.create("imp1", "Import");
        imp.set("filename", stepPath);
        long tGeom0 = System.currentTimeMillis();
        geom.run();
        System.out.printf("    Geometry imported and unioned in %.2f s.%n",
                (System.currentTimeMillis() - tGeom0) / 1000.0);

        // 3. Assign Material: Ti-6Al-4V ELI
        System.out.println(">>> [3/8] Assigning material Ti-6Al-4V ELI...");
        Material mat = model.component("comp1").material().create("mat1", "Common");
        mat.label("Ti-6Al-4V ELI");
        mat.selection().all();
        mat.propertyGroup("def").set("youngsmodulus", new String[]{"110[GPa]"});
        mat.propertyGroup("def").set("poissonsratio", new String[]{"0.33"});
        mat.propertyGroup("def").set("density", new String[]{"4430[kg/m^3]"});

        // 4. Solid Mechanics Physics
        System.out.println(">>> [4/8] Configuring 3D Solid Mechanics physics...");
        Physics solid = model.component("comp1").physics().create("solid", "SolidMechanics", "geom1");
        solid.selection().all();

        // 5. Boundary Condition Selections (Coordinate Box)
        System.out.println(">>> [5/8] Locating boundary surfaces via coordinate box filters...");
        // Tip selection: Y in [-0.5, 2.0] mm
        SelectionFeature selFix = model.component("comp1").selection().create("sel_fix", "Box");
        selFix.label("Fixed Tip Selection");
        selFix.set("entitydim", 2);
        selFix.set("condition", "intersects");
        selFix.set("xmin", -5.0); selFix.set("xmax", 5.0);
        selFix.set("ymin", -0.5); selFix.set("ymax", 2.0);
        selFix.set("zmin", -5.0); selFix.set("zmax", 5.0);

        // Head selection: Y in [28.0, 30.0] mm
        SelectionFeature selDisp = model.component("comp1").selection().create("sel_disp", "Box");
        selDisp.label("Displacement Head Selection");
        selDisp.set("entitydim", 2);
        selDisp.set("condition", "intersects");
        selDisp.set("xmin", -5.0); selDisp.set("xmax", 5.0);
        selDisp.set("ymin", 28.0); selDisp.set("ymax", 30.0);
        selDisp.set("zmin", -5.0); selDisp.set("zmax", 5.0);

        int[] fixFaces = selFix.entities(2);
        int[] dispFaces = selDisp.entities(2);
        System.out.printf("    Tip fixed boundaries found: %d | Head displacement boundaries found: %d%n",
                fixFaces.length, dispFaces.length);

        if (fixFaces.length == 0 || dispFaces.length == 0) {
            throw new RuntimeException("Boundary detection failed: zero boundaries selected!");
        }

        // Apply Fixed Constraint at tip
        PhysicsFeature fix1 = solid.create("fix1", "Fixed", 2);
        fix1.selection().set(fixFaces);

        // Apply Prescribed Tensile Displacement Uy = 0.2 mm at head
        PhysicsFeature disp1 = solid.create("disp1", "Displacement2");
        disp1.selection().set(dispFaces);
        disp1.set("Direction", new int[][]{{0}, {1}, {0}});
        disp1.set("U0", new String[]{"0", "0.2[mm]", "0"});

        // 6. Free Tetrahedral Mesh (autoMeshSize = 6: balanced accuracy and memory)
        System.out.println(">>> [6/8] Generating 3D tetrahedral mesh...");
        MeshSequence mesh = model.component("comp1").mesh().create("mesh1");
        mesh.autoMeshSize(6);
        long tMesh0 = System.currentTimeMillis();
        mesh.run();
        System.out.printf("    Mesh generated in %.2f s.%n",
                (System.currentTimeMillis() - tMesh0) / 1000.0);

        // 7. Stationary Structural Solver
        System.out.println(">>> [7/8] Running stationary structural solver...");
        Study std = model.study().create("std1");
        std.create("stat1", "Stationary");
        long tSolve0 = System.currentTimeMillis();
        std.run();
        System.out.printf("    Solver converged in %.2f s.%n",
                (System.currentTimeMillis() - tSolve0) / 1000.0);

        // 8. Result Extraction & Export
        System.out.println(">>> [8/8] Evaluating results and exporting to CSV...");
        NumericalFeature maxStress = model.result().numerical().create("max_stress", "MaxVolume");
        maxStress.set("expr", "solid.mises");
        maxStress.set("unit", "MPa");
        maxStress.selection().all();
        double maxVonMises_MPa = maxStress.getReal()[0][0];

        NumericalFeature rf = model.result().numerical().create("rxn_force", "IntSurface");
        rf.set("expr", "solid.RFy");
        rf.set("unit", "N");
        rf.selection().set(fixFaces);
        double rxnForce_N = Math.abs(rf.getReal()[0][0]);

        System.out.println("    ---------------------------------------------");
        System.out.printf("    Max von Mises Stress : %.4f MPa%n", maxVonMises_MPa);
        System.out.printf("    Axial Reaction Force : %.4f N%n", rxnForce_N);
        System.out.println("    ---------------------------------------------");

        // Write CSV
        writeResultsCSV(csvPath, screwName, maxVonMises_MPa, rxnForce_N);
        System.out.println("    Results saved to: " + csvPath);

        // Save Solved MPH Model
        try {
            System.out.println("    Saving solved model: " + mphPath);
            model.save(mphPath);
            System.out.println("    Model file saved successfully.");
        } catch (Exception ex) {
            System.err.println("    Notice: could not save MPH file (" + ex.getMessage() + ")");
        }

        return model;
    }

    private static void writeResultsCSV(String filePath, String screwName,
                                        double maxStress_MPa, double reactionForce_N) throws IOException {
        FileWriter fw = null;
        PrintWriter pw = null;
        try {
            fw = new FileWriter(filePath);
            pw = new PrintWriter(fw);
            pw.println("Screw,MaxVonMisesStress_MPa,ReactionForce_N");
            pw.printf("%s,%.6f,%.6f%n", screwName, maxStress_MPa, reactionForce_N);
        } finally {
            if (pw != null) pw.close();
            if (fw != null) fw.close();
        }
    }
}
