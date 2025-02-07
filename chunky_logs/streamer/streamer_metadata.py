import logging
import pathlib
import json
from chunky_logs.common.metadata import MetaData, MetaDataError

class StreamerMetaDataError(MetaDataError):
    pass

class StreamerMetaDataFileNotFound(MetaDataError):
    pass

class StreamerMetaData(MetaData):
    def __init__(self, group_path: pathlib.Path, chunk_name: pathlib.Path):
        self._logger = logging.getLogger(self.__class__.__name__)
        super().__init__(group_path, chunk_name)

    @MetaData._data_key_exception
    def __setitem__(self, key, value):
        self._metadata[key]['value'] = value

    def add(self, metadata_key, metadata_value, metadata_type):
        """
        Adds a new metadata value
        :param metadata_key: The key to reference the metadata by
        :param metadata_value: The value of the metadata
        :param metadata_type: The value type (as defined in the data schema)
        """
        if metadata_type not in self._type_schema:
            raise StreamerMetaDataError(f"Unknown value type not in schema: {metadata_type}")

        self._metadata[metadata_key] = {
            "value": metadata_value,
            "type": metadata_type
        }

        self._logger.debug(f"Added new metadata: key={metadata_key} value={metadata_value} type{metadata_type}")

    @MetaData.chunk_file.setter
    def chunk_file(self, chunk_file: pathlib.Path):
        self._metadata[MetaData.CHUNK_FILENAME_KEY]['value'] = chunk_file

    @MetaData.chunk_time_create.setter
    def chunk_time_create(self, time_create: int):
        self._metadata[MetaData.CHUNK_TIME_CREATE_KEY]['value'] = time_create

    @MetaData.chunk_time_update.setter
    def chunk_time_update(self, time_update: int):
        self._metadata[MetaData.CHUNK_TIME_UPDATE_KEY]['value'] = time_update

    @MetaData.chunk_line_count.setter
    def chunk_line_count(self, line_count: int):
        self._metadata[MetaData.CHUNK_LINE_COUNT_KEY]['value'] = line_count

    @MetaData.chunk_checksum_hash.setter
    def chunk_checksum_hash(self, checksum_hash: str):
        self._metadata[MetaData.CHUNK_CHECKSUM_HASH_KEY]['value'] = checksum_hash

    def write_to_disk(self):
        """
        This will write the current metadata to disk
        :return:
        """
        with open(self.file, 'w') as metadata_data:
            json.dump(self._metadata, metadata_data)