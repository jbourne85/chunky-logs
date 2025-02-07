from unittest import mock
import pathlib
import pytest
from chunky_logs.common import MetaData, MetaDataKeyError

@mock.patch('os.path.exists')
@mock.patch('builtins.open')
def test_load_metadata_success(patch_builtins_open, patch_os_path_exists):
    """
    This will test that when a metadata file exists that the json is correctly loaded and parsed
    """
    patch_os_path_exists.return_value = True
    mock_data = {
        'chunk.file': {
            'value': pathlib.PurePosixPath('chunk_1.chunk'),
            'type': 'path'
        },
        'chunk.time.create': {
            'value': '1648829317',
            'type': 'int'
        },
        'chunk.time.update': {
            'value': '1648915726',
            'type': 'int'
        },
        'chunk.line.count': {
            'value': '1440',
            'type': 'int'
        },
        'chunk.checksum.hash': {
            'value': 'xliyudtn3e',
            'type': 'str'
        },
        'chunk.checksum.type': {
            'value': 'md5',
            'type': 'str'
        },
        'data.start': {
            'value': '1652334530',
            'type': 'int'
        },
        'data.end': {
            'value': '1661424345',
            'type': 'int'
        }
    }

    group_path = pathlib.PurePosixPath('/tmp/test_group')
    chunk_name = pathlib.PurePosixPath('chunk_1')

    with mock.patch("json.loads", return_value=mock_data):
        test_metadata = MetaData(group_path, chunk_name)

        # Assert the default metadata
        assert test_metadata.file == pathlib.PurePosixPath('/tmp/test_group/chunk_1.metadata.json')
        assert pathlib.Path(test_metadata.chunk_file) == pathlib.PurePosixPath('chunk_1.chunk')
        assert test_metadata.chunk_time_create == 1648829317
        assert test_metadata.chunk_time_update == 1648915726
        assert test_metadata.chunk_line_count == 1440
        assert test_metadata.chunk_checksum_hash == "xliyudtn3e"
        assert test_metadata.chunk_checksum_type == "md5"

        # Assert the extra custom metadata
        assert test_metadata['data.start'] == 1652334530
        assert test_metadata['data.end'] == 1661424345

@mock.patch('os.path.exists')
def test_load_metadata_default_data(patch_os_path_exists):
    """
    This will test that when a metadata file does not exist then default values are set
    """
    patch_os_path_exists.return_value = False
    group_path = pathlib.PurePosixPath('/tmp/test_group')
    chunk_name = pathlib.PurePosixPath('chunk_1')

    test_metadata = MetaData(group_path, chunk_name)

    assert test_metadata.chunk_file == pathlib.Path('.')
    assert test_metadata.chunk_time_create == 0
    assert test_metadata.chunk_time_update == 0
    assert test_metadata.chunk_line_count == 0
    assert test_metadata.chunk_checksum_hash == ""
    assert test_metadata.chunk_checksum_type == "md5"

def test_metadata_key_exceptions():
    """
    This will test that when accessing a non-existent metadata key an exception is raised
    """
    group_path = pathlib.PurePosixPath('/tmp/test_group')
    chunk_name = pathlib.PurePosixPath('chunk_1')

    with mock.patch.object(MetaData, '_load_metadata', return_value={}):
        test_metadata = MetaData(group_path, chunk_name)

        with pytest.raises(MetaDataKeyError):
            test_metadata['nonexistent-key']
