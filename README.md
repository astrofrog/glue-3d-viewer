Experimental Glue VisPy plugin
==============================

[![Build Status](https://travis-ci.org/glue-viz/glue-3d-viewer.svg)](https://travis-ci.org/glue-viz/glue-3d-viewer?branch=master)
[![Build status](https://ci.appveyor.com/api/projects/status/1gov2vtuesjnij69/branch/master?svg=true)](https://ci.appveyor.com/project/astrofrog/glue-3d-viewer/branch/master)

To install the plugin:

    python setup.py install
    
This will auto-register the plugin with Glue. Now simply start up Glue, open a
data cube, drag it onto the main canvas, then select '3D viewer'.

To run the tests, do:

    py.test vispy_volume

at the root of the repository. This requires the [pytest](http://pytest.org) module to be installed.

Have fun!
