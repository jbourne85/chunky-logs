from unittest import mock
import pathlib
import pytest
from chunky_logs.common.chunk import Chunk, ChunkManagedFileError

@mock.patch("chunky_logs.common.chunk.MetaData")
def test_constructor(mock_metadata):
    group_path = pathlib.PurePosixPath('/tmp/test_group')
    chunk_name = pathlib.PurePosixPath('chunk_1')

    mock_metadata_instance = mock.MagicMock()
    mock_metadata.return_value = mock_metadata_instance
    with mock.patch.object(mock_metadata_instance, "file", new_callable=mock.PropertyMock) as mock_property:
        mock_property.return_value = 'chunk_1.metadata'

        test_chunk = Chunk(group_path, chunk_name)

        assert test_chunk._managed_files == [
            pathlib.PurePosixPath('/tmp/test_group/chunk_1.chunk'),
            mock_property
        ]

@mock.patch('os.remove')
@mock.patch("chunky_logs.common.chunk.MetaData")
def test_delete_success(mock_metadata, patch_os_remove):
    group_path = pathlib.PurePosixPath('/tmp/test_group')
    chunk_name = pathlib.PurePosixPath('chunk_1')

    mock_metadata_instance = mock.MagicMock()
    mock_metadata.return_value = mock_metadata_instance

    test_chunk = Chunk(group_path, chunk_name)
    test_chunk._managed_files = [
        'managed_file_1',
        'managed_file_2',
        'managed_file_3',
    ]

    test_chunk.delete()

    assert patch_os_remove.call_count == 3
    patch_os_remove.assert_any_call('managed_file_1')
    patch_os_remove.assert_any_call('managed_file_2')
    patch_os_remove.assert_any_call('managed_file_3')

@mock.patch('os.remove')
@mock.patch("chunky_logs.common.chunk.MetaData")
def test_delete_failure(mock_metadata, patch_os_remove):
    group_path = pathlib.PurePosixPath('/tmp/test_group')
    chunk_name = pathlib.PurePosixPath('chunk_1')

    mock_metadata_instance = mock.MagicMock()
    mock_metadata.return_value = mock_metadata_instance

    test_chunk = Chunk(group_path, chunk_name)
    test_chunk._managed_files = [
        'managed_file_1',
        'managed_file_2',
        'managed_file_3',
    ]

    patch_os_remove.side_effect=OSError("File not found")

    with pytest.raises(ChunkManagedFileError):
        test_chunk.delete()
