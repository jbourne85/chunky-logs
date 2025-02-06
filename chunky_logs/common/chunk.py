import os
import logging
import pathlib
from zipfile import ZipFile
from chunky_logs.common.metadata import MetaData

class ChunkManagedFileError(OSError):
    pass

class Chunk:
    CHUNK_FILE_EXTENSION = '.chunk'
    def __init__(self, group_path: pathlib.Path, chunk_name: pathlib.Path):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._base_path = group_path
        self._file = chunk_name.with_suffix(Chunk.CHUNK_FILE_EXTENSION)

        self.metadata = MetaData(self._file)

        self._managed_files = [
            self._file,
            self.metadata.file
        ]

    def delete(self):
        """
        This deletes all the managed files associated with this Chunk
        """
        for file in self._managed_files:
            try:
                os.remove(file)
                self._logger.debug(f"Removed Chunk managed file. file={file}")
            except OSError as e:
                raise ChunkManagedFileError(f"Unable to remove managed file: {e}") from None

    def archive(self):
        """
        This archives all the managed files associated with this Chunk, all managed files will be zipped up and then
        removed
        """
        archive_filename = self.get_associated_file('zip')
        with ZipFile(archive_filename, 'w') as archive:
            for file in self._managed_files:
                if os.path.exists(file):
                    self._logger.debug(f"Archiving Chunk file. archive={archive_filename} file={file}")
                    archive.write(file)

        self.delete()
