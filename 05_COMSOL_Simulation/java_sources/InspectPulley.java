import com.comsol.model.*;
import com.comsol.model.util.*;
import com.comsol.model.physics.*;

public class InspectPulley {
    public static void main(String[] args) {
        try {
            Model model = ModelUtil.load("Model", "D:/COMSOL/COMSOL62/Multiphysics/applications/COMSOL_Multiphysics/Structural_Mechanics/stresses_in_pulley.mph");
            for (String comp : model.component().tags()) {
                System.out.println("Component: " + comp);
                for (String phys : model.component(comp).physics().tags()) {
                    Physics p = model.component(comp).physics(phys);
                    System.out.println("  Physics: " + phys + " (type=" + p.getType() + ")");
                    for (String feat : p.feature().tags()) {
                        PhysicsFeature f = p.feature(feat);
                        System.out.println("    Feature: tag=" + feat + " | type=" + f.getType() + " | label=" + f.label());
                    }
                }
            }
            ModelUtil.remove("Model");
        } catch (Exception e) {
            e.printStackTrace(System.out);
        }
    }
}
