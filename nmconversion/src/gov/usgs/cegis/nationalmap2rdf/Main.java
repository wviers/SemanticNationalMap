package gov.usgs.cegis.nationalmap2rdf;

import org.python.core.PyException;
import org.python.core.PyInteger;
import org.python.core.PyObject;
import org.python.util.PythonInterpreter;

import java.io.InputStream;
import java.lang.ClassLoader;
import java.util.Properties;
import java.net.URLDecoder;


public class Main {
  public static void main(String[] args) throws PyException {
    String path = Main.class.getProtectionDomain().getCodeSource().getLocation().getPath();
    String decodedPath = "";
    try {
      decodedPath = URLDecoder.decode(path, "UTF-8");
    } catch (Exception e) {

    }

    decodedPath += "/python/";

    PythonInterpreter interp = new PythonInterpreter();
    interp.exec("import sys");
    interp.exec("sys.path.append('" + decodedPath + "/')");
    InputStream pysrc = ClassLoader.class.getResourceAsStream("/python/nationalmap2rdf-new.py");
    interp.execfile(pysrc);
    
  }
}