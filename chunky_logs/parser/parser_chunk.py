import logging
import pathlib
from chunky_logs.common.chunk import Chunk, ChunkManagedFileError

class ParserChunkManagedFileError(ChunkManagedFileError):
    pass

class ParserChunkReadError(ChunkManagedFileError):
    pass

class ParserChunk(Chunk):
    def __init__(self, group_path: pathlib.Path, chunk_name: pathlib.Path):
        super().__init__(group_path, chunk_name)
        self._logger = logging.getLogger(self.__class__.__name__)
        self._chunk_pos = None
        self._current_checksum = self.metadata.checksum

    def read(self):
        """
        This reads the latest line from the chunk file being followed by this instance of the Parser Chunk.
        It should always be able to read the next line after it was last read
        :return: The line read on success
        """
        try:
            with open(self._chunk_file, 'r') as chunk_data:
                if self._chunk_pos:
                    chunk_data.seek(self._chunk_pos)

                line = chunk_data.readline()

                if line:
                    self._chunk_pos = chunk_data.tell()
                return line.strip()
        except FileNotFoundError as e:
            raise ParserChunkManagedFileError(f"Chunk file not found: {e}") from None
        except Exception as e:
            raise ParserChunkReadError(f"Error while reading chunk: {e}") from None

    def has_changed(self):
        """
        This will use the checksum of the metadata file to decide if the chunk has been updated, this is lighter weight
        than relying on the checksum of the chunk file as it will most likely be magnitudes smaller
        :return: True if the metadata changes (indicating there is new data to parse in the chunk), False if not
        """
        current_checksum = self.metadata.checksum
        if current_checksum != self._current_checksum:
            self._logger.debug(f"Metadata file has been updated, reloading.")
            self.metadata.reload()
            self._current_checksum = current_checksum
            return True
        return False