import tempfile
from unittest import mock
import pathlib
import pytest
from chunky_logs.common.metadata import MetaData, MetaDataError, MetaDataSourceError, MetaDataKeyError

@mock.patch('os.path.exists')
@mock.patch('builtins.open')
def test_load_metadata_success(patch_builtins_open, patch_os_path_exists):
    temp_filename = tempfile.NamedTemporaryFile().name
    chunk_filename = pathlib.Path(temp_filename).with_suffix('.chunk')

    patch_os_path_exists.return_value = True
    mock_data = {
        'chunk.file': {
            'value': chunk_filename,
            'type': 'path'
        },
        'time.create': {
            'value': '1648829317',
            'type': 'int'
        },
        'time.update': {
            'value': '1648915726',
            'type': 'int'
        },
        'line.count': {
            'value': '1440',
            'type': 'int'
        },
        'checksum.hash': {
            'value': 'xliyudtn3e',
            'type': 'str'
        },
        'checksum.type': {
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

    with mock.patch("json.loads", return_value=mock_data):
        test_metadata = MetaData(chunk_filename)

        # Assert the default metadata
        assert test_metadata.metadata_file == pathlib.Path(chunk_filename).with_suffix('.metadata.json')
        assert pathlib.Path(test_metadata.chunk_file) == chunk_filename
        assert test_metadata.time_create == 1648829317
        assert test_metadata.time_update == 1648915726
        assert test_metadata.line_count == 1440
        assert test_metadata.checksum_hash == "xliyudtn3e"
        assert test_metadata.checksum_type == "md5"

        # Assert the extra custom metadata
        assert test_metadata['data.start'] == 1652334530
        assert test_metadata['data.end'] == 1661424345

@mock.patch('os.path.exists')
def test_load_metadata_failed_missing_file(patch_os_path_exists):
    patch_os_path_exists.return_value = False

    with pytest.raises(MetaDataSourceError):
        MetaData(pathlib.Path('chunkfile'))

def test_metadata_key_exceptions():
    with mock.patch.object(MetaData, '_load_metadata', return_value={}):
        test_metadata = MetaData(pathlib.Path('test_chunk_file.dat'))

        with pytest.raises(MetaDataKeyError):
            test_metadata.chunk_file

        with pytest.raises(MetaDataKeyError):
            test_metadata.time_create

        with pytest.raises(MetaDataKeyError):
            test_metadata.time_update

        with pytest.raises(MetaDataKeyError):
            test_metadata.line_count

        with pytest.raises(MetaDataKeyError):
            test_metadata.checksum_hash

        with pytest.raises(MetaDataKeyError):
            test_metadata.checksum_type

        with pytest.raises(MetaDataKeyError):
            test_metadata['nonexistent-key']
