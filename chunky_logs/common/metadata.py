import logging
import os

class MetaDataError(RuntimeError):
    pass

class MetaData:
    CHUNK_FILENAME_KEY = 'chunk.file'
    TIME_CREATE_KEY = 'time.create'
    TIME_UPDATE_KEY = 'time.update'
    LINE_COUNT_KEY = 'line.count'
    CHECKSUM_HASH_KEY = 'checksum.hash'
    CHECKSUM_TYPE_KEY = 'checksum.type'
    METADATA_FILE_EXTENSION = 'metadata'

    def __init__(self, chunk_filename):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._metadata_keys = [
            MetaData.CHUNK_FILENAME_KEY,
            MetaData.TIME_CREATE_KEY,
            MetaData.TIME_UPDATE_KEY,
            MetaData.LINE_COUNT_KEY,
            MetaData.CHECKSUM_HASH_KEY,
            MetaData.CHECKSUM_TYPE_KEY
        ]
        self._metadata = self._load_metadata(chunk_filename)

    @property
    def chunk_filename(self) -> str:
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
        if key in self._metadata:
            return self._metadata[key]
        raise MetaDataError(f"Unknown metadata key. key={key}")

    def _load_metadata(self, chunk_filename):
        metadata_file = f"{os.path.splitext(chunk_filename)[0]}.{MetaData.METADATA_FILE_EXTENSION}"
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
