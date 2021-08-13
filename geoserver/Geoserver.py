import os
import requests
import xml.etree.ElementTree as ET
from typing import Optional, Union


class Geoserver:
    """
    Attributes
    ----------
    service_url : str
        The URL for the GeoServer instance.
    username : str
        Login name for session.
    password: str
        Password for session.
    """

    def __init__(
            self,
            service_url="http://10.110.0.22:8080/geoserver",
            username="admin",
            password="12345678",
    ):
        self._service_url = service_url
        self._username = username
        self._password = password

    def __repr__(self):
        return "I am Geoserver at {}".format(self._service_url)

    def reset(self) -> str:
        """
        Resets all store, raster, and schema caches. This operation is used to force GeoServer to drop all caches and
        store connections and reconnect to each of them the next time they are needed by a request. This is useful in
        case the stores themselves cache some information about the data structures they manage that may have changed
        in the meantime.
        """

        url = "{}/rest/reset".format(self._service_url)

        try:
            r = requests.post(url, auth=(self._username, self._password))
            return "Status code: {}.".format(r.status_code)

        except Exception as e:
            return "Reset error. {0}. Status code: {1}.".format(e, r.status_code)

    def reload(self) -> str:
        """
        Reloads the GeoServer catalog and configuration from disk.
        This operation is used in cases where an external tool has modified the on-disk configuration.
        This operation will also force GeoServer to drop any internal caches and reconnect to all data stores.
        """

        url = "{}/rest/reload".format(self._service_url)

        try:
            r = requests.post(url, auth=(self._username, self._password))
            return "Status code: {}.".format(r.status_code)

        except Exception as e:
            return "Reload error. {0}. Status code: {1}.".format(e, r.status_code)

    def get_workspaces(self) -> Union[dict, str]:
        """ Returns all the workspaces. """

        url = "{}/rest/workspaces".format(self._service_url)

        try:
            r = requests.get(url, auth=(self._username, self._password))
            return r.json()['workspaces']['workspace']

        except Exception as e:
            return "Can not get workspaces. {0}. Status code: {1}.".format(e, r.status_code)

    def get_layers(self, workspace: Optional[str]) -> Union[dict, str]:
        """
        Get all the layers from geoserver
        If workspace is None, it will listout all the layers from geoserver.
        """

        url = "{}/rest/layers".format(
            self._service_url) if workspace is None else "{}/rest/workspaces/{}/layers".format(self._service_url,
                                                                                               workspace)

        try:
            r = requests.get(url, auth=(self._username, self._password))
            return r.json()

        except Exception as e:
            return "Can not get layers. {0}. Status code: {1}.".format(e, r.status_code)

    def get_coveragestores(self, workspace: Optional[str]) -> Union[dict, str]:
        """ Returns all the coveragestores inside a specific workspace. """

        if workspace is None:
            workspace = "default"

        url = "{}/rest/workspaces/{}/coveragestores".format(self._service_url, workspace)

        try:
            r = requests.get(url, auth=(self._username, self._password))
            return r.json()['coverageStores']['coverageStore']

        except TypeError as e:
            return []  # if coveragestore is empty return empty array
        except Exception as e:
            return "Can not get coveragestores. {0}. Status code: {1}.".format(e, r.status_code)

    def delete_workspace(self, workspace: str) -> str:
        """ Delete workspace by name. """

        url = "{}/rest/workspaces/{}".format(self._service_url, workspace)

        params = {"recurse": "true"}  # flag to delete all layers and coveragestores from this workspace

        try:
            r = requests.delete(url, auth=(self._username, self._password), params=params)

            if r.status_code == 200:
                return "Workspace {0} deleted. Status code: {1}.".format(workspace, r.status_code)

        except Exception as e:
            return "Can not delete workspace. {0}. Status code: {1}.".format(e, r.status_code)

    def delete_layer(
            self,
            workspace: str,
            coveragestore_name: str,
    ) -> str:
        """ 
        Delete layer from coveragestore by name.
        
        Notes:
        -----
        Layer name is the same as coveragestore name. 
        """

        url = '{0}/rest/workspaces/{1}/coveragestores/{2}/coverages/{2}.xml'.format(self._service_url, workspace,
                                                                                    store_name)

        params = {"recurse": "true"}

        try:
            r = requests.delete(url, auth=(self._username, self._password), params=params)

            if r.status_code in (200, 201, 202):
                return 'Layer {0} deleted. Status code : {1}.'.format(coveragestore_name, r.status_code)

        except Exception as e:
            return "Can not delete layer. {0}. Status code: {1}.".format(e, r.status_code)

    def delete_coveragesotre(self, coveragestore_name: str, workspace: Optional[str]) -> str:
        """ Delete coveragestore by name from workspace. """

        if workspace is None:  # geoserver will search coverag estore among all workspaces
            url = "{}/rest/coveragestores/{}".format(self._service_url, coveragestore_name)
        else:
            url = "{}/rest/workspaces/{}/coveragestores/{}".format(
                self._service_url,
                workspace,
                coveragestore_name
            )

        params = {"recurse": "true"}  # flag to delete all layers from coverage store

        try:
            r = requests.delete(url, auth=(self._username, self._password), params=params)
            if r.status_code == 200:
                return "Coverage store deleted successfully. Status code: {}.".format(r.status_code)

        except Exception as e:
            return ("Coverage store can not be deleted. {0}. Status code: {1}.".format(e, r.status_code))

    def create_workspace(self, workspace: str) -> str:
        """ Create a new workspace in geoserver. """

        url = "{}/rest/workspaces".format(self._service_url)

        # to create a workspace you should at least give it a name
        data = "<workspace><name>{}</name></workspace>".format(workspace)

        headers = {"content-type": "text/xml"}

        try:
            r = requests.post(url, data, auth=(self._username, self._password), headers=headers)

            if r.status_code == 201:
                return "Workspace {0} created. Status code: {1}.".format(workspace, r.status_code)

            if r.status_code == 401:
                raise Exception("The workspace already exist. Status code: {}.".format(r.status_code))

        except Exception as e:
            return "The workspace can not be created. {0}. Status code: {1}.".format(e, r.status_code)

    def create_coveragestore(
            self,
            path,
            workspace: Optional[str] = None,
            coveragestore_name: Optional[str] = None,
            configure: Optional[bool] = None,
            file_type: str = "imagemosaic",
            content_type: str = "application/zip",
    ):
        """ Create coveragestore in worksapce. """

        if not os.path.exists(path):
            raise FileNotFoundError('This path not exists!')

        if workspace is None:
            workspace = 'default'

        if configure:
            params['configure'] = 'none'

        url = '{0}/rest/workspaces/{1}/coveragestores/{2}/file.{3}'.format(
            self._service_url, workspace, coveragestore_name, file_type
        )

        headers = {
            'content-type': content_type
        }

        params = {
            'coverageName': coveragestore_name
        }

        try:
            with open(path, 'rb') as f:
                r = requests.put(url, data=f.read(),
                                 auth=(self._username, self._password), headers=headers, params=params)

            return 'Coveragestore {0} is created. Status code: {1}.'.format(coveragestore_name, r.status_code)

        except Exception as e:
            return "The coveragestore can not be created. {0}. Status code: {1}.".format(e, r.status_code)

    def _get_granules_list_from_json(self, granules_json: dict) -> dict:
        """ Get granules(layers) names and their file locations from json. """

        ids = [el['id'] for el in granules_json['features']]  # all ids of granules
        locations = [el['properties']['location'] for el in granules_json['features']]  # all locations of granules
        return dict(zip(ids, locations))

    def get_granules_from_coveragestore(
            self,
            workspace: str,
            coveragestore_name: str,
    ) -> Union[dict, str]:
        """ Get all granules(layers) from coveragesotre. """

        url = '{0}/rest/workspaces/{1}/coveragestores/{2}/coverages/{2}/index/granules.json'.format(
            self._service_url,
            workspace,
            coveragestore_name
        )

        try:
            r = requests.get(url, auth=(self._username, self._password))
            return self._get_granules_list_from_json(r.json())

        except Exception as e:
            return "Can not get granules from coveragestore. {0}. Status code: {1}.".format(e, r.status_code)

    def delete_granula_from_coveragestore(
            self,
            workspace: str,
            coveragestore_name: str,
            granula_id: str
    ) -> str:
        """ Delete one specific granula from coveragestore. """

        url = '{0}/rest/workspaces/{1}/coveragestores/{2}/coverages/{2}/index/granules/{3}.xml'.format(
            self._service_url,
            workspace,
            coveragestore_name,
            granula_id
        )

        try:
            r = requests.delete(url, auth=(self._username, self._password))
            return 'Granula "{0}" deleted successfully. Status code: {1}.'.format(granula_id, r.status_code)

        except Exception as e:
            return "Can not delete granula. {0}. Status code: {1}.".format(e, r.status_code)

    def publish_file_to_coveragestore(
            self,
            path,
            coveragestore_name: str,
            workspace: str,
            file_type: str = "imagemosaic",
            content_type: str = "image/tiff"
    ) -> str:
        """ 
        Publish file/folder/zip to coveragestore.
        
        Notes
        -----
        Examples:
        
        path to folder with .tif files : '/NFS_WORK/sat/public/test_products/projects_with_tiff/tiff'
        path in curl request:  'file:///NFS_WORK/sat/public/test_products/projects_with_tiff/tiff'
        content type: text/plain
        
        path to .tif: /NFS_WORK/sat/public/test_products/init_with_tiff/tiff/202107090500_RGB_1024pxs_EPSG4326.tiff'
        path in curl request: 'file:///NFS_WORK/sat/public/test_products/init_with_tiff/tiff/202107090500_RGB_1024pxs_EPSG4326.tiff'
        content type: image/tiff
        """

        if not os.path.exists(path):
            raise FileNotFoundError('This path not exists.')

        path = 'file://' + path

        url = '{0}/rest/workspaces/{1}/coveragestores/{2}/external.{3}'.format(
            self._service_url,
            workspace,
            coveragestore_name,
            file_type
        )

        headers = {
            "content-type": content_type
        }

        configuration_data = path

        try:
            r = requests.post(
                url,
                data=configuration_data,
                auth=(self._username, self._password),
                headers=headers
            )

            if r.status_code in (200, 201, 202):
                return 'Published. Status code: {}.'.format(r.status_code)

        except Exception as e:
            return "Can not publish it. {0}. Status code: {1}.".format(e, r.status_code)

    def publish_zip_to_coveragestore(
            self,
            path,
            coveragestore_name: str,
            workspace: str,
            file_type: str = 'imagemosaic',
            content_type: str = "application/zip"
    ):
        """ 
        Publish zip file to coveragestore like a binary. 
        
        Notes:
        -----
        Example of path: '/NFS_WORK/sat/public/test_products/init_with_tiff/tiff.zip'
        """

        url = '{0}/rest/workspaces/{1}/coveragestores/{2}/file.{3}'.format(self._service_url, workspace,
                                                                           coveragestore_name, file_type)

        headers = {
            "content-type": content_type
        }

        params = {
            "recalculate": ["nativebbox", "latlonbbox"]
        }

        try:
            with open(path, 'rb') as f:
                r = requests.post(url, data=f.read(), auth=(
                    self._username, self._password), headers=headers, params=params)

            if r.status_code in (200, 201, 202):
                return 'Zip file published. Status code: {}.'.format(r.status_code)

        except Exception as e:
            return "Can not publish zip file. {0}. Status code: {1}.".format(e, r.status_code)

    def _get_id_of_layer(self, description: str) -> str:
        """ Get layer id from parsed description string. """
        return ET.fromstring(description).find('id').text

    def _get_layer_description(
            self,
            coveragestore_name: str,
            workspace: str,
            content_type: str = "application/xml; charset=UTF-8",
    ) -> str:
        """ Get layer description by name. """

        url = '{0}/gwc/rest/layers/{1}:{2}'.format(self._service_url, workspace, coveragestore_name)

        headers = {
            "accept": content_type
        }

        try:
            r = requests.get(url, auth=(self._username, self._password), headers=headers)

            if r.status_code in (200, 201, 202):
                return r.text

        except Exception as e:
            return "Can not get description. {0}. Status code: {1}.".format(e, r.status_code)

    def publish_timecahe_file_to_coveragestore(
            self,
            coveragestore_name: str,
            workspace: str,
            content_type: str = "application/xml; charset=UTF-8",
            blob: str = "RAM",
            start_time: str = "2021-07-09T00:00:00Z"  # default value
    ) -> str:
        """ 
        Replaces the old timecache file with a new one with a description of the time dimension and cache data. 
        """

        url = '{0}/gwc/rest/layers/{1}:{2}.xml'.format(self._service_url, workspace, coveragestore_name)

        headers = {
            "content-type": content_type
        }

        coveragestore_id = self._get_id_of_layer(
            self._get_layer_description(workspace=workspace, coveragestore_name=coveragestore_name))

        timecache_data = (
            "<GeoServerLayer>"
            "<id>{0}</id>"
            "<enabled>true</enabled>"
            "<inMemoryCached>true</inMemoryCached>"
            "<name>{1}:{2}</name>"
            "<blobStoreId>{3}</blobStoreId>"
            "<mimeFormats>"
            "<string>image/png</string>"
            "<string>image/jpeg</string>"
            "</mimeFormats>"
            "<gridSubsets>"
            "<gridSubset>"
            "<gridSetName>EPSG:4326</gridSetName>"
            "</gridSubset>"
            "<gridSubset>"
            "<gridSetName>EPSG:900913</gridSetName>"
            "</gridSubset>"
            "</gridSubsets>"
            "<metaWidthHeight>"
            "<int>4</int>"
            "<int>4</int>"
            "</metaWidthHeight>"
            "<expireCache>0</expireCache>"
            "<expireClients>0</expireClients>"
            "<parameterFilters>"
            "<regexParameterFilter>"
            "<key>TIME</key>"
            "<defaultValue>{4}</defaultValue>"
            "<normalize>"
            "<locale></locale>"
            "</normalize>"
            "<regex>[0-9]{4}-[0-9]{2}-[0-9]{2}T([0-9]{2}:){2}[0-9]{2}[.][0-9]{3}Z</regex>"
            "</regexParameterFilter>"
            "<styleParameterFilter>"
            "<key>STYLES</key>"
            "<defaultValue></defaultValue>"
            "</styleParameterFilter>"
            "</parameterFilters>"
            "<gutter>0</gutter>"
            "* Connection #0 to host localhost left intact"
            "</GeoServerLayer>".format(
                coveragestore_id, workspace, coveragestore_name, blob, start_time
            )
        )

        try:
            r = requests.put(
                url,
                data=timecache_data,
                auth=(self._username, self._password),
                headers=headers
            )

            if r.status_code in (200, 201, 202):
                return 'Timecache file is published. Status code: {}.'.format(r.status_code)

        except Exception as e:
            return "Can not publish. {0}. Status code: {1}.".format(e, r.status_code)

    def publish_time_dimension_to_coveragestore(
            self,
            workspace: str,
            coveragestore_name: str,
            presentation: str = 'LIST',
            units: str = 'ISO8601',
            default_value: str = 'MINIMUM',
            content_type: str = "application/xml; charset=UTF-8"
    ):
        """
        Create time dimension in coverage store to publish time series in geoserver.
        
        Notes:
        -----
        More about time support in geoserver WMS you can read here:
        https://docs.geoserver.org/master/en/user/services/wms/time.html
        """

        url = '{0}/rest/workspaces/{1}/coveragestores/{2}/coverages/{2}'.format(self._service_url, workspace,
                                                                                coveragestore_name)

        headers = {
            "content-type": content_type
        }

        time_dimension_data = (
            "<coverage>"
            "<enabled>true</enabled>"
            "<metadata>"
            "<entry key='time'>"
            "<dimensionInfo>"
            "<enabled>true</enabled>"
            "<presentation>{0}</presentation>"
            "<units>{1}</units>"
            "<defaultValue>"
            "<strategy>{2}</strategy>"
            "</defaultValue>"
            "</dimensionInfo>"
            "</entry>"
            "</metadata>"
            "</coverage>".format(
                presentation, units, default_value
            )
        )

        try:
            r = requests.put(url,
                             data=time_dimension_data,
                             auth=(self._username, self._password),
                             headers=headers
                             )

            if r.status_code in (200, 201):
                return 'Time dimension is published. Status code: {}.'.format(r.status_code)

        except Exception as e:
            return "Can not publish time dimension. {0}. Status code: {1}.".format(e, r.status_code)
