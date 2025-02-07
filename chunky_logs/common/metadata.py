import json
import logging
import os.path
import pathlib
from chunky_logs.common.hashing import file_md5sum

class MetaDataError(RuntimeError):
    pass

class MetaDataSourceError(RuntimeError):
    pass

class MetaDataKeyError(KeyError):
    pass

class MetaData:
    """
    This class represents the metadata associated with a Chunk file, it knows how to load them from disk
    """
    CHUNK_FILENAME_KEY = 'chunk.file'
    CHUNK_TIME_CREATE_KEY = 'chunk.time.create'
    CHUNK_TIME_UPDATE_KEY = 'chunk.time.update'
    CHUNK_LINE_COUNT_KEY = 'chunk.line.count'
    CHUNK_CHECKSUM_HASH_KEY = 'chunk.checksum.hash'
    CHUNK_CHECKSUM_TYPE_KEY = 'chunk.checksum.type'
    METADATA_FILE_EXTENSION = '.metadata.json'

    def __init__(self, group_path: pathlib.Path, chunk_name: pathlib.Path):
        self._logger = logging.getLogger(self.__class__.__name__)

        self._default_keys = [
            MetaData.CHUNK_FILENAME_KEY,
            MetaData.CHUNK_TIME_CREATE_KEY,
            MetaData.CHUNK_TIME_UPDATE_KEY,
            MetaData.CHUNK_LINE_COUNT_KEY,
            MetaData.CHUNK_CHECKSUM_HASH_KEY,
            MetaData.CHUNK_CHECKSUM_TYPE_KEY
        ]

        self._type_schema = {
            'str': str,
            'int': int,
            'float': float,
            'bool': bool,
            'path': pathlib.Path
        }

        self._metadata_file = group_path.joinpath(chunk_name.with_suffix(MetaData.METADATA_FILE_EXTENSION))

        if os.path.exists(self._metadata_file):
            self.load_from_disk()
        else:
            self._metadata = {}
            self._default_metadata()

    def _default_metadata(self):
        """
        This will populate the metadata with default values
        :param chunk_file: This is the relative path to the chunk file
        """
        def add_default_metadata_key(key, value, value_type):
            self._metadata[key] = {
                "value": value,
                "type": value_type
            }

        add_default_metadata_key(MetaData.CHUNK_FILENAME_KEY, pathlib.Path(''), 'path')
        add_default_metadata_key(MetaData.CHUNK_TIME_CREATE_KEY, 0, 'int')
        add_default_metadata_key(MetaData.CHUNK_TIME_UPDATE_KEY, 0, 'int')
        add_default_metadata_key(MetaData.CHUNK_LINE_COUNT_KEY, 0, 'int')
        add_default_metadata_key(MetaData.CHUNK_CHECKSUM_HASH_KEY, '', 'str')
        add_default_metadata_key(MetaData.CHUNK_CHECKSUM_TYPE_KEY, 'md5', 'str')

    def _data_key_exception(self):
        def _property_exception_f(*args):
            try:
                return self(*args)
            except KeyError as e:
                raise MetaDataKeyError(f"Metadata non-existent Key: {e}") from None
        return _property_exception_f

    @_data_key_exception
    def __getitem__(self, key):
        return self._metadata[key]['value']

    def __contains__(self, key):
        return key in self._metadata

    @property
    def checksum(self) -> str:
        return file_md5sum(self.file)

    @property
    def file(self) -> pathlib.Path:
        return self._metadata_file

    @property
    def chunk_file(self) -> pathlib.Path:
        return self._metadata[MetaData.CHUNK_FILENAME_KEY]['value']

    @property
    def chunk_time_create(self) -> int:
        return self._metadata[MetaData.CHUNK_TIME_CREATE_KEY]['value']

    @property
    def chunk_time_update(self) -> int:
        return self._metadata[MetaData.CHUNK_TIME_UPDATE_KEY]['value']

    @property
    def chunk_line_count(self) -> int:
        return self._metadata[MetaData.CHUNK_LINE_COUNT_KEY]['value']

    @property
    def chunk_checksum_hash(self) -> str:
        return self._metadata[MetaData.CHUNK_CHECKSUM_HASH_KEY]['value']

    @property
    def chunk_checksum_type(self) -> str:
        return self._metadata[MetaData.CHUNK_CHECKSUM_TYPE_KEY]['value']

    def load_from_disk(self):
        """
        This will update the metadata data with that stored on disk
        :return: None
        """
        self._metadata = self._load_metadata(self._metadata_file)

    def _load_metadata(self, metadata_json_file):
        """
        This method loads the metadata from a given json metadata source file. It will use the _type_schema in order
        to set the correct types for the metadata
        :param metadata_json_file: The metadata json source file to load
        :return: A dictionary representing the metadata in the form {key: {value:'VALUE', type:'TYPE}, ...*}
        """
        try:
            with open(metadata_json_file) as metadata_json_handle:
                metadata_json = json.load(metadata_json_handle)
                for key in metadata_json:
                    metadata_json[key]['value'] = self._type_schema[metadata_json[key]['type']](metadata_json[key]['value'])
        except FileNotFoundError as e:
            raise MetaDataSourceError(f"Unable to source metadata: {e}") from None

        if all(metadata_key in metadata_json for metadata_key in self._default_keys):
            for key in metadata_json:
                self._logger.debug(f"Metadata Loaded. metadata.json.file={metadata_json_file} {key}={metadata_json[key]['value']}")
            return metadata_json
        else:
            missing_keys = [metadata_key for metadata_key in self._default_keys if metadata_key not in metadata_json]
            raise MetaDataError(f"Missing metadata key(s) {', '.join(missing_keys)})")
