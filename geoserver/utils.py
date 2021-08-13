import os
import pathlib
import shutil


class PublicationUtils:
    """ File utils class """

    @staticmethod
    def make_dir(fpath) -> None:
        """ Make dir and ensurence the parent directory of a filepath exists. """
        pathlib.Path(fpath).mkdir(parents=True, exist_ok=True)

    @staticmethod
    def check_path_existence(fpath: str) -> bool:
        """ Check for file existence. """
        return os.path.exists(fpath)

    @staticmethod
    def create_filename(fpath_parts: tuple) -> str:
        """ Create file name from parts. """
        return os.path.join(*fpath_parts)

    @staticmethod
    def zip_dir(fpath: str) -> None:
        """ Zip folder with files. """
        # Example: '/NFS_WORK/sat/public/test_products/blue_marble/init'
        if not PublicationUtils.check_path_existence(fpath):
            return False
        shutil.make_archive(fpath, 'zip', fpath)
        return True

    @staticmethod
    def copy_file(fpath_from: str, fpath_to: str) -> None:
        """ Copy file from directory to directory. """
        if PublicationUtils.check_path_existence(fpath_to) or not PublicationUtils.check_path_existence(fpath_from):
            return False
        shutil.copyfile(fpath_from, fpath_to)
        return True

    @staticmethod
    def copy_dir_recursively(fpath_from: str, fpath_to: str) -> bool:
        """ Copy entire directory with files into an existing directory """
        if PublicationUtils.check_path_existence(fpath_to) or not PublicationUtils.check_path_existence(fpath_from):
            return False
        shutil.copytree(fpath_from, fpath_to)
        return True
