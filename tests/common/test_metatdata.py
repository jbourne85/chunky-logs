import tempfile
from unittest import mock
import pathlib
import pytest
from chunky_logs.common.metadata import MetaData, MetaDataError, MetaDataKeyError

@mock.patch('os.path.exists')
def test_load_metadata_success(patch_os_path_exists):
    temp_filename = tempfile.NamedTemporaryFile().name
    chunk_filename = pathlib.Path(temp_filename).with_suffix('.chunk')

    patch_os_path_exists.return_value = True
    mock_metadata_file = mock.mock_open()
    mock_metadata_file.return_value.readlines.return_value = [
        f"chunk.file ={chunk_filename}\n",
        f"time.create = 1648829317\n",
        f"time.update = 1648915726\n",
        f"line.count=1440\n",
        f"checksum.hash=xliyudtn3e",
        f"checksum.type=md5",
        f"data.start = 1652334530\n",
        f"data.end = 1661424345\n",
        "\n",
    ]

    with mock.patch('builtins.open', mock_metadata_file):
        test_metadata = MetaData(chunk_filename)

        # Assert the default metadata
        assert test_metadata.metadata_file == pathlib.Path(chunk_filename).with_suffix('.metadata')
        assert pathlib.Path(test_metadata.chunk_file) == chunk_filename
        assert test_metadata.time_create == 1648829317
        assert test_metadata.time_update == 1648915726
        assert test_metadata.line_count == 1440
        assert test_metadata.checksum_hash == "xliyudtn3e"
        assert test_metadata.checksum_type == "md5"

        # Assert the extra custom metadata
        assert test_metadata.get_value('data.start') == '1652334530'
        assert test_metadata.get_value('data.end') == '1661424345'

@mock.patch('os.path.exists')
def test_load_metadata_failed_missing_file(patch_os_path_exists):
    patch_os_path_exists.return_value = False

    with pytest.raises(MetaDataError):
        MetaData('chunkfile')

def test_metadata_key_exceptions():
    with mock.patch.object(MetaData, '_load_metadata', return_value={}):
        test_metadata = MetaData('test_chunk_file.dat')

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
