from collections import namedtuple
import logging
import pathlib
import json
from chunky_logs.common.metadata import MetaData, MetaDataError

class AuthorMetaDataError(MetaDataError):
    pass

class AuthorMetaDataFileNotFound(MetaDataError):
    pass

AuthorMetaDataItem = namedtuple('MetaDataItem', ['key', 'value', 'type'])

class AuthorMetaData(MetaData):
    def __init__(self, group_path: pathlib.Path, chunk_name: pathlib.Path):
        self._logger = logging.getLogger(self.__class__.__name__)
        super().__init__(group_path, chunk_name)

    @MetaData._data_key_exception
    def __setitem__(self, key, value):
        self._metadata[key]['value'] = value

    def add(self, item: AuthorMetaDataItem):
        """
        Adds a new metadata value, using the AuthorMetaDataItem tuple. It will also
        ensure that the data is converted to the correct type
        :param item: This is the MetaDataItem representing the new metadata item to add
        """
        if item.type not in self._type_schema:
            raise AuthorMetaDataError(f"Unknown value type not in schema: {item.type}")

        self._metadata[item.key] = {
            "value": self._type_schema[item.type](item.value),
            "type": item.type
        }

        self._logger.debug(f"Added new metadata: key={item.key} value={item.value} type{item.type}")

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