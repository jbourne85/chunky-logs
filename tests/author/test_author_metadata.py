import pathlib
import pytest
from unittest import mock
from chunky_logs.author import AuthorMetaData, AuthorMetaDataItem, AuthorMetaDataError

@mock.patch('os.path.exists')
@mock.patch('builtins.open')
def test_set_default_data(patch_builtins_open, patch_os_path_exists):
    patch_os_path_exists.return_value = False
    group_path = pathlib.PurePosixPath('/tmp/test_group')
    chunk_name = pathlib.PurePosixPath('chunk_1')

    test_metadata = AuthorMetaData(group_path, chunk_name)
    test_metadata.chunk_file = pathlib.PurePosixPath('/tmp/test_group/chunk_1.chunk')
    test_metadata.chunk_time_create = 1648829317
    test_metadata.chunk_time_update = 1648915726
    test_metadata.chunk_line_count = 1440
    test_metadata.chunk_checksum_hash = "xliyudtn3e"

    assert test_metadata.file == pathlib.PurePosixPath('/tmp/test_group/chunk_1.metadata.json')
    assert test_metadata.chunk_file == pathlib.PurePosixPath('/tmp/test_group/chunk_1.chunk')
    assert test_metadata.chunk_time_create == 1648829317
    assert test_metadata.chunk_time_update == 1648915726
    assert test_metadata.chunk_line_count == 1440
    assert test_metadata.chunk_checksum_hash == "xliyudtn3e"
    assert test_metadata.chunk_checksum_type == "md5"

@mock.patch('os.path.exists')
@mock.patch('builtins.open')
def test_add_new_success(patch_builtins_open, patch_os_path_exists):
    patch_os_path_exists.return_value = False
    group_path = pathlib.PurePosixPath('/tmp/test_group')
    chunk_name = pathlib.PurePosixPath('chunk_1')

    test_metadata = AuthorMetaData(group_path, chunk_name)

    test_metadata.add(AuthorMetaDataItem('test.data.int', '10', 'int'))
    test_metadata.add(AuthorMetaDataItem('test.data.str', 'test_data', 'str'))
    test_metadata.add(AuthorMetaDataItem('test.data.path', '/tmp/test_group', 'path'))

    assert test_metadata['test.data.int'] == 10
    assert test_metadata['test.data.str'] == 'test_data'
    assert test_metadata['test.data.path'] == pathlib.Path('/tmp/test_group')

@mock.patch('os.path.exists')
@mock.patch('builtins.open')
def test_add_new_failure(patch_builtins_open, patch_os_path_exists):
    patch_os_path_exists.return_value = False
    group_path = pathlib.PurePosixPath('/tmp/test_group')
    chunk_name = pathlib.PurePosixPath('chunk_1')

    test_metadata = AuthorMetaData(group_path, chunk_name)
    test_metadata._type_schema = {'int':int} #  Limiting valid type to just int

    # Test adding an incompatible type
    with pytest.raises(AuthorMetaDataError):
        test_metadata.add(AuthorMetaDataItem('test.data.int', 'test_data', 'str'))

    # Test adding a mismatched type (the value cannot become the type)
    with pytest.raises(AuthorMetaDataError):
        test_metadata.add(AuthorMetaDataItem('test.data.int', 'test_data', 'int'))

@mock.patch('os.path.exists')
@mock.patch('builtins.open', new_callable=mock.mock_open)
@mock.patch('json.dump')
def test_write_to_disk(patch_json_dump, patch_builtins_open, patch_os_path_exists):
    patch_os_path_exists.return_value = False
    group_path = pathlib.PurePosixPath('/tmp/test_group')
    chunk_name = pathlib.PurePosixPath('chunk_1')

    test_metadata = AuthorMetaData(group_path, chunk_name)

    # Set the main data
    test_metadata.chunk_file = pathlib.PurePosixPath('/tmp/test_group/chunk_1.chunk')
    test_metadata.chunk_time_create = 1648829317
    test_metadata.chunk_time_update = 1648915726
    test_metadata.chunk_line_count = 1440
    test_metadata.chunk_checksum_hash = "xliyudtn3e"

    # Add some extra data
    test_metadata.add(AuthorMetaDataItem('test.data.int', '10', 'int'))
    test_metadata.add(AuthorMetaDataItem('test.data.str', 'test_data', 'str'))

    test_metadata.write_to_disk()


    patch_json_dump.assert_called_with({
        'chunk.file': {
            'value': pathlib.PurePosixPath('/tmp/test_group/chunk_1.chunk'),
            'type': 'path'
        },
        'chunk.time.create': {
            'value': 1648829317,
            'type': 'int'
        },
        'chunk.time.update': {
            'value': 1648915726,
            'type': 'int'
        },
        'chunk.line.count': {
            'value': 1440,
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
        'test.data.int': {
            'value': 10,
            'type': 'int'
        },
        'test.data.str': {
            'value': 'test_data',
            'type': 'str'
        }
    },
    patch_builtins_open())
