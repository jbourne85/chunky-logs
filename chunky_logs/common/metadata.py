import logging
import os

class MetaDataError(RuntimeError):
    pass

class MetaData:
    """
    This class represents the metadata associated with a Chunk file, it knows how to load them from disk
    """
    CHUNK_FILENAME_KEY = 'chunk.file'
    TIME_CREATE_KEY = 'time.create'
    TIME_UPDATE_KEY = 'time.update'
    LINE_COUNT_KEY = 'line.count'
    CHECKSUM_HASH_KEY = 'checksum.hash'
    CHECKSUM_TYPE_KEY = 'checksum.type'
    METADATA_FILE_EXTENSION = 'metadata'

    def __init__(self, chunk_file):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._metadata_keys = [
            MetaData.CHUNK_FILENAME_KEY,
            MetaData.TIME_CREATE_KEY,
            MetaData.TIME_UPDATE_KEY,
            MetaData.LINE_COUNT_KEY,
            MetaData.CHECKSUM_HASH_KEY,
            MetaData.CHECKSUM_TYPE_KEY
        ]
        self._metadata_file = f"{os.path.splitext(chunk_file)[0]}.{MetaData.METADATA_FILE_EXTENSION}"
        self._metadata = self._load_metadata(self._metadata_file)

    @property
    def metadata_file(self) -> str:
        return self._metadata_file

    @property
    def chunk_file(self) -> str:
        return self._metadata[MetaData.CHUNK_FILENAME_KEY]

    @property
    def time_create(self) -> int:
        return int(self._metadata[MetaData.TIME_CREATE_KEY])

    @property
    def time_update(self) -> int:
        return int(self._metadata[MetaData.TIME_UPDATE_KEY])

    @property
    def line_count(self) -> int:
        return int(self._metadata[MetaData.LINE_COUNT_KEY])

    @property
    def checksum_hash(self) -> str:
        return self._metadata[MetaData.CHECKSUM_HASH_KEY]

    @property
    def checksum_type(self) -> str:
        return self._metadata[MetaData.CHECKSUM_TYPE_KEY]

    def get_value(self, key):
        """
        This method gets the current metadata value based on a key value
        :param key: The metadata key to fetch
        :return: The matching metadata value on success, raises a MetaDataError on error
        """
        if key in self._metadata:
            return self._metadata[key]
        raise MetaDataError(f"Unknown metadata key. key={key}")

    def _load_metadata(self, metadata_file):
        """
        This method loads the metadata from a given metadata file
        :param metadata_file: The metadata file to load from
        :return: A dict of key, values that represent the metadata on disk
        """
        metadata = {}
        if os.path.exists(metadata_file):
            self._logger.debug(f"Existing metadata file found. metadata.filename={metadata_file}")
            with open(metadata_file, 'r') as reader:
                lines = reader.readlines()
                for line in lines:
                    if len(line.split('=')) == 2:
                        key, value = line.split('=')
                        key = key.strip()
                        value = value.strip()
                        metadata[key] = value
        else:
            raise MetaDataError(f"No matching metadata file found. metadata.filename={metadata_file})")

        if all(metadata_key in metadata for metadata_key in self._metadata_keys):
            for key, value in metadata.items():
                self._logger.debug(f"Metadata Loaded. metadata.file={metadata_file} {key}={value}")
            return metadata
        else:
            missing_keys = [metadata_key for metadata_key in self._metadata_keys if metadata_key not in metadata]
            raise MetaDataError(f"Missing metadata key(s) {', '.join(missing_keys)})")
