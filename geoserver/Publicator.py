import time


class ELECTRO_L_2_RGB_GEOSERVER_PUBLICATOR:
    """ Publishes ELECTRO L2 RGB full disk GEO geotiff to geoserver. """

    # USE CASE
    # satellite = 'electro_l2'
    # args = 'ELECTRO_L_2_RGB_GEOSERVER', '2021', '07', '19', '2030'
    # projector = ELECTRO_2_JPEG_RGB_PUBLICATOR(satellite)
    # projector.workflow(args)

    def __init__(self, satellite):
        """ Init publicator. """
        if not satellite in ('electro_l2'):
            raise ValueError("satellite must to be electro_l2 ")
        self.satellite = satellite
        self.product = 'ELECTRO_L_2_RGB_GEOSERVER'
        self.publicator = Publicator(self.product)

    def workflow(self, args) -> str:
        """ Workflow method. """
        return self.publicator.workflow(args)


class AHI_L2_RGB_GEOSERVER_PUBLICATOR:
    """ Publishes HIMAWARI 8 disk GEO geotiff to geoserver. """

    # USE CASE
    # satellite = 'himawari8'
    # args = 'AHI_L2_RGB_GEOSERVER', '2021', '07', '19', '2030'
    # projector = AHI_L2_RGB_GEOSERVER_PUBLICATOR(satellite)
    # projector.workflow(args)

    def __init__(self, satellite):
        """ Init publicator. """
        if not satellite in ('himawari8'):
            raise ValueError("satellite must to be himawari8 ")
        self.satellite = satellite
        self.product = 'AHI_L2_RGB_GEOSERVER'
        self.publicator = Publicator(self.product)

    def workflow(self, args) -> str:
        """ Workflow method. """
        return self.publicator.workflow(args)


class ABI_L2_G17_RGB_GEOSERVER_PUBLICATOR:
    """ Publishes GEOS17 disk GEO geotiff to geoserver. """

    # USE CASE
    # satellite = 'geos17'
    # args = 'ABI_L2_G17_RGB_GEOSERVER', '2021', '07', '19', '2030'
    # projector = ABI_L2_G17_RGB_GEOSERVER_PUBLICATOR(satellite)
    # projector.workflow(args)

    def __init__(self, satellite):
        """ Init publicator. """
        if not satellite in ('goes17'):
            raise ValueError("satellite must to be goes17!")
        self.satellite = satellite
        self.product = 'ABI_L2_G17_RGB_GEOSERVER'
        self.publicator = Publicator(self.product)

    def workflow(self, args) -> str:
        """ Workflow method. """
        return self.publicator.workflow(args)


class ABI_L2_G16_RGB_GEOSERVER_PUBLICATOR:
    """ Publishes GEOS16 disk GEO geotiff to geoserver. """

    # USE CASE
    # satellite = 'geos16'
    # args = 'ABI_L2_G16_RGB_GEOSERVER', '2021', '07', '19', '2030'
    # projector = ABI_L2_G16_RGB_GEOSERVER_PUBLICATOR(satellite)
    # projector.workflow(args)

    def __init__(self, satellite):
        """ Init publicator. """
        if not satellite in ('goes16'):
            raise ValueError("satellite must to be goes16!")
        self.satellite = satellite
        self.product = 'ABI_L2_G16_RGB_GEOSERVER'
        self.publicator = Publicator(self.product)

    def workflow(self, args) -> str:
        """ Workflow method. """
        return self.publicator.workflow(args)


class Publicator:
    """ Publishes geotiff to geoserver. """

    def __init__(self, product: str):
        """ Init publicator. """
        self.product = product
        # init logger
        wflogger = WFLogger().plogger(self.product)
        self.logger = wflogger
        # init configs
        config = YConfig().config
        self._config = config
        storage_config = config['storage_config']
        product_config = config[self.product]
        geoserver_config = config['geoserver_config']
        # init dirs and names
        self.product = product_config['name']
        self._DIR_SOURCE = product_config['dir_source']
        self._DIR_SAT = storage_config['DIR_SAT']
        self._DIR_SAT_RGB = storage_config['DIR_SAT_RGB']
        self._DIR_SAT_PUBLIC = storage_config['DIR_SAT_PUBLIC']
        self._DIR_INIT = product_config['init_dir_name']
        self._DIR_TIFF = product_config['storage_dir_name']
        self._DIR_BASE = product_config['base_dir_name']
        self._source_file_sample = product_config['sample']
        self._file_extension = product_config['extension']
        self._zip_extension = '.zip'
        # geoserver initialization
        self._geoserver_url = geoserver_config['service_url']
        self._geoserver_username = geoserver_config['username']
        self._geoserver_password = geoserver_config['password']
        self.geoserver = Geoserver(
            service_url=self._geoserver_url,
            username=self._geoserver_username,
            password=self._geoserver_password
        )
        self.workspace_name = product_config['workspace']
        self.coveragestore_name = product_config['coveragestore']

    def _create_source_file_name(self, args) -> str:
        (_, year, month, day, dtime) = args
        return self._DIR_SOURCE + \
               '_' + year + month + day + \
               '_' + dtime + \
               '_' + self._source_file_sample + self._file_extension

    def _create_source_file_path(self, args) -> str:
        (_, year, month, day, dtime) = args
        # build file path
        local_source_filename = self._create_source_file_name(args)
        full_path_source_filename = PublicationUtils.create_filename(
            (
                self._DIR_SAT,
                self._DIR_SAT_RGB,
                self._DIR_SOURCE,
                year,
                month,
                day,
                dtime,
                local_source_filename
            )
        )
        return full_path_source_filename

    def _check_source_file_existence(self, args) -> bool:
        source_file_path = self._create_source_file_path(args)
        status = PublicationUtils.check_path_existence(source_file_path)
        if status:
            self.logger.info(f'File {source_file_path} exists: {status}')
        else:
            self.logger.error(f'File {source_file_path} exists: {status}')
        return status

    def _check_product_existence_in_filesystem(self, args) -> bool:
        product_name = args[0]
        # build file path
        local_product_dir = PublicationUtils.create_filename((self._DIR_SAT, self._DIR_SAT_PUBLIC, product_name))
        return PublicationUtils.check_path_existence(local_product_dir)

    def _create_product_in_filesystem(self, args) -> None:
        """ Create product. """
        # create dir and file names
        product_name = args[0]  # ELECTRO_L_2_RGB_GEOSERVER
        local_product_dir = PublicationUtils.create_filename((self._DIR_SAT, self._DIR_SAT_PUBLIC, product_name))
        local_source_file_name = self._create_source_file_name(args)
        local_source_file_path = self._create_source_file_path(args)
        init_dir_name = PublicationUtils.create_filename((local_product_dir, self._DIR_INIT))
        base_dir_name = PublicationUtils.create_filename((self._DIR_SAT, self._DIR_SAT_PUBLIC, self._DIR_BASE))
        base_init_dir_name = PublicationUtils.create_filename((base_dir_name, self._DIR_INIT))
        tif_storage_dir_name = PublicationUtils.create_filename((local_product_dir, self._DIR_TIFF))

        # create directory
        PublicationUtils.make_dir(local_product_dir)
        PublicationUtils.make_dir(tif_storage_dir_name)

        # copy files
        PublicationUtils.copy_dir_recursively(base_init_dir_name, init_dir_name)
        PublicationUtils.copy_file(
            local_source_file_path,
            PublicationUtils.create_filename((init_dir_name, local_source_file_name))
        )
        PublicationUtils.zip_dir(init_dir_name)
        self.logger.info(f'product {product_name} created in file system')

    def _check_workspace_existence_in_geoserver(self, args) -> None:
        # Check workspace
        workspace_names = [self.geoserver.get_workspaces()[i]['name']
                           for i in range(len(self.geoserver.get_workspaces()))]
        if self.workspace_name not in workspace_names:
            self.geoserver.create_workspace(self.workspace_name)
            self.logger.info(f'{self.workspace_name} created')
            return
        self.logger.info(f'{self.workspace_name} already created')
        return

    def _check_product_existence_in_geoserver(self, args) -> None:
        """ Check coveragestore existence in geoserver. """
        product_name = args[0]

        # Check coveragestore in workspace
        coveragesotre_names = [self.geoserver.get_coveragestores(workspace=self.workspace_name)[i]['name']
                               for i in range(len(self.geoserver.get_coveragestores(workspace=self.workspace_name)))]
        # todo: string indices must be integers -> workspace is empty!
        if self.coveragestore_name not in coveragesotre_names:
            path = PublicationUtils.create_filename(
                (
                    self._DIR_SAT,
                    self._DIR_SAT_PUBLIC,
                    product_name,
                    self._DIR_INIT + self._zip_extension
                )
            )

            self.geoserver.create_coveragestore(
                path=path,
                workspace=self.workspace_name,
                coveragestore_name=self.coveragestore_name
            )
            self.logger.info(f'empty coveragestore {self.coveragestore_name} created')

            self.geoserver.publish_time_dimension_to_coveragestore(
                workspace=self.workspace_name,
                coveragestore_name=self.coveragestore_name
            )
            self.logger.info(f'add time dimension to coveragestore {self.coveragestore_name}')

            self.geoserver.publish_timecahe_file_to_coveragestore(
                workspace=self.workspace_name,
                coveragestore_name=self.coveragestore_name
            )
            self.logger.info(f'add timecache file to coveragestore {self.coveragestore_name}')

            return

        self.logger.info(f'coveragestore {self.coveragestore_name} store already exists')
        return

    def _check_file_existence_in_product(self, args) -> bool:
        product, year, month, day, dtime = args
        granules = [i.split('/')[-1] for i in self.geoserver.get_granules_from_coveragestore(
            workspace=self.workspace_name,
            coveragestore_name=self.coveragestore_name
        ).values()]
        return self._create_source_file_name(args) in granules

    def _create_tif_file_path(self, args) -> str:
        product_name = args[0]  # ELECTRO_L_2_RGB_GEOSERVER
        local_product_dir = PublicationUtils.create_filename((self._DIR_SAT, self._DIR_SAT_PUBLIC, product_name))
        local_source_file_name = self._create_source_file_name(args)
        local_source_file_path = self._create_source_file_path(args)
        tiff_dir_name = PublicationUtils.create_filename((local_product_dir, self._DIR_TIFF))
        return PublicationUtils.create_filename((tiff_dir_name, local_source_file_name))

    def _move_file_to_product_dir(self, args) -> None:
        """ Move .tif file to tiff project directory. """
        local_source_file_path = self._create_source_file_path(args)
        tif_filename = self._create_tif_file_path(args)
        PublicationUtils.copy_file(
            local_source_file_path,
            tif_filename
        )

    def _publish_file_to_coveragestore(self, args) -> None:
        """ Publish .tif granula to coveragestore. """
        tif_filename = self._create_tif_file_path(args)
        self.geoserver.publish_file_to_coveragestore(
            path=tif_filename,
            workspace=self.workspace_name,
            coveragestore_name=self.coveragestore_name
        )

    def workflow(self, args) -> str:
        """ Check if there are files in local dir then load by args. """
        product, year, month, day, dtime = args
        # 'AHI_L2_RGB_GEOSERVER', '2021', '08', '02', '0330'

        tif_filename = self._create_source_file_name(args)

        if not self._check_source_file_existence(args):
            return 'source file existence error'

        if not self._check_product_existence_in_filesystem(args):
            self.logger.info(f'product {product} not exists in filesystem')

            self._create_product_in_filesystem(args)
            time.sleep(2)
            self._check_workspace_existence_in_geoserver(args)
            time.sleep(2)
            self._check_product_existence_in_geoserver(args)

            self.logger.info(f'product {product} finally created')
            self.logger.info(f'{tif_filename} file in product: {self._check_file_existence_in_product(args)}')
            return 'done' if self._check_file_existence_in_product(args) else 'initial file creation error'
        elif self._check_product_existence_in_filesystem(args) and not self._check_file_existence_in_product(args):
            self.logger.info(f'product {product} exists in filesystem')
            self.logger.info(f'file {tif_filename} does not exists in product dir')

            self._move_file_to_product_dir(args)
            self.logger.info(f'file {tif_filename} moved to product tiff dir')

            time.sleep(5)
            self._publish_file_to_coveragestore(args)
            self.logger.info(
                f'new {tif_filename} file published to product: {self._check_file_existence_in_product(args)}')
            return 'done' if self._check_file_existence_in_product(args) else 'file creation error'

        self.logger.info(f'{tif_filename} file already in product: {self._check_file_existence_in_product(args)}')
        return 'done'
