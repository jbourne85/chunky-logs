import tempfile
from unittest import mock
import pathlib
import pytest
from chunky_logs.common.chunk import Chunk

@mock.patch("chunky_logs.common.chunk.MetaData")
def test_constructor(mock_metadata):
    base_path = pathlib.Path(tempfile.NamedTemporaryFile().name)
    chunk_name = pathlib.Path('chunk_1')

    mock_metadata_instance = mock.MagicMock()
    mock_metadata.return_value = mock_metadata_instance
    with mock.patch.object(mock_metadata_instance, "file", new_callable=mock.PropertyMock) as mock_property:
        mock_property.return_value = 'metadata_file'

        test_chunk = Chunk(base_path, chunk_name)

        assert test_chunk._managed_files == [
            chunk_name.with_suffix('.chunk'),
            mock_property
        ]
