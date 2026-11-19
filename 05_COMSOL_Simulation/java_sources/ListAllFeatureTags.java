import com.comsol.model.*;
import com.comsol.model.util.*;
import com.comsol.model.physics.*;

public class ListAllFeatureTags {
    public static void main(String[] args) {
        try {
            Model model = ModelUtil.create("TestTags");
            model.modelNode().create("comp1");
            model.component("comp1").geom().create("geom1", 3);
            Physics solid = model.component("comp1").physics().create("solid", "SolidMechanics", "geom1");
            
            FeatureInfoList fil = solid.featureInfo();
            System.out.println("FeatureInfo tags count: " + fil.tags().length);
            for (String tag : fil.tags()) {
                System.out.println("  " + tag);
            }
            ModelUtil.remove("TestTags");
        } catch (Exception e) {
            e.printStackTrace(System.out);
        }
    }
}
