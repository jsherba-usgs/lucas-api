LandCarbon-CDI
==============

Installation
------------

Install system dependencies on Ubuntu 16.04:

    sudo apt-get install libsqlite3-mod-spatialite

If you are on Ubuntu 14.04 with an older version of SpatiaLite, this package
does not exist. Instead, create a `settings_local.py` with these contents to
override the library path:

    SPATIALITE_LIBRARY_PATH = '/usr/lib/x86_64-linux-gnu/libspatialite.so'

Install this project from scratch for development by running:

    git clone git@github.com:berkeley-gif/landcarbon-cdi.git
    cd landcarbon-cdi
    make build
