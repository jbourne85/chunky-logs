import tempfile
from chunky_logs.common.hashing import file_md5sum

def test_get_file_md5sum():
    """
    Tests getting the md5 checksum for a text file, it will generate the file contents on order to calculate the
    checksum. It also checks that adding a newline will change the checksum to ensure its operating in binary mode
    """
    data = [
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore\n",
        "magna aliqua.Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo\n",
        "consequat.Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla\n",
        "pariatur.Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est\n",
        "laborum."
    ]
    with tempfile.NamedTemporaryFile(mode='w', delete=True) as temp_file:
        temp_file.writelines(data)
        temp_file.flush()

        assert file_md5sum(temp_file.name) == '2e1c81e7816b8e75c617c80525344a3f'

        temp_file.write('\n')
        temp_file.flush()

        assert file_md5sum(temp_file.name) != '2e1c81e7816b8e75c617c80525344a3f'


def test_get_large_file_md5sum():
    """
    Tests getting the md5 checksum for a large text file, this checks that creating a file larger than the block size
    (which is 4k) the checskum is still correct
    """
    data = [
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore\n",
        "magna aliqua.Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo\n",
        "consequat.Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla\n",
        "pariatur.Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est\n",
        "laborum."
    ]

    with tempfile.NamedTemporaryFile(mode='w', delete=True) as temp_file:
        # Create an approx 100MB file
        for i in range(250000):
            temp_file.writelines(data)
            temp_file.flush()

        assert file_md5sum(temp_file.name) == '94a3d4bf17e438258768d3b708e606f1'
