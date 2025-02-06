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
