# Geoserver-imagemosaic-rest <br/>

Python library for management for geospatial imagemosaic data (time series) in GeoServer. Python REST API. <br/> 

## Overview

The `geoserver-imagemosaic-rest` package is useful for the management of geospatial imagemosaic data in [GeoServer](http://geoserver.org/). The package is useful for the creating, updating and deleting geoserver workspaces, stores, granula files.

## Usage

```python
# Import the library
from geoserver.Geoserver import Geoserver

# Initialize the library
geo = Geoserver(service_url='http://127.0.0.1:8080/geoserver', username='admin', password='geoserver')

# for creating workspace
geo.create_workspace(workspace='work')

# for creating coveragestore
# zip file should contains at least one .tif file and some configuration .properties files
# more about it read here https://docs.geoserver.org/latest/en/user/data/raster/imagemosaic/configuration.html
geo.create_coveragestore(path=r'path\to\init\init.zip', workspace='work', coveragestore_name='my_store')

# add time series properties to your coveragestore
geo.publish_time_dimension_to_coveragestore(workspace='work', coveragestore_name='my_store')

# add timecache properties to your coveragestore
geo.publish_timecahe_file_to_coveragestore(workspace='work', coveragestore_name='my_store')

# for uploading raster data to the geoserver 
geo.publish_file_to_coveragestore(path=r'path\to\raster\file.tif', workspace='work', coveragestore_name='my_store')

# see all ids of .tif files in coveragestore
geo.get_granules_from_coveragestore(workspace='work', coveragestore_name='my_store')

# delete one .tif file from coveragestore by id
geo.delete_granula_from_coveragestore(workspace='work', coveragestore_name='my_store', granula_id='my_store.1')

# delete workspace
geo.delete_workspace(workspace='work')

# delete coveragestore
geo.delete_layer(workspace='work', coveragestore_name='my_store')
```

## Application
This API helps me to create geographic meteo information portal.  
Server: [Geoserver](https://github.com/geoserver/geoserver)  
Client: [TerriaJS](https://github.com/TerriaJS/terriajs)  
Some images of system:
![1](https://user-images.githubusercontent.com/54303323/129359939-5e5c7b9a-4b4d-4702-bae3-3db5fd7af2d0.png)
![2](https://user-images.githubusercontent.com/54303323/129359974-a9b4f7f0-8d6c-4ae6-8aa6-e98629107e8f.png)
