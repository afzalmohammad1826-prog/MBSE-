import com.comsol.model.*;
import com.comsol.model.util.*;
import java.io.*;
public class VolCheck {
  public static void main(String[] a) throws Exception {
    String[] n = {"AS1_screw","AS2_screw","NS_screw","AS2U_screw","AS2G_screw"};
    PrintWriter pw = new PrintWriter(new FileWriter("D:/MBSE/volumes.csv"));
    for (String s : n) {
      Model m = ModelUtil.create("v_"+s);
      m.modelNode().create("comp1");
      GeomSequence g = m.component("comp1").geom().create("geom1",3);
      g.lengthUnit("mm");
      GeomFeature imp = g.create("imp1","Import");
      imp.set("filename","D:/MBSE/"+s+".step");
      g.run();
      g.measure().selection().init(3); g.measure().selection().all();
      double vv = g.measure().getVolume();
      pw.printf("%s,%.4f%n", s, vv); pw.flush();
      ModelUtil.remove("v_"+s);
    }
    pw.close();
  }
}
