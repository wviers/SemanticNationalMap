package gov.usgs.cegis.nationalmap2rdf;

import org.python.core.PyException;
import org.python.core.PyInteger;
import org.python.core.PyObject;
import org.python.util.PythonInterpreter;

import java.io.InputStream;
import java.lang.ClassLoader;



public class Main {
  public static void main(String[] args) throws PyException {
    PythonInterpreter interp = new PythonInterpreter();
    InputStream pysrc = ClassLoader.class.getResourceAsStream("/python/nationalmap2rdf-new.py");
    interp.execfile(pysrc);
    
  }
}