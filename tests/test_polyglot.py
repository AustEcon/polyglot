import polyglot
import os

my_path = os.path.abspath(os.path.dirname(__file__))

# ICONS
PATH_TO_SMALL_JPG = os.path.join(my_path, './test_content/images/Ludwig_von_Mises.jpg')


class TestUpload:
    def testfile_to_binary(self):
        binary = polyglot.Upload.file_to_binary(PATH_TO_SMALL_JPG)
        assert type(binary) == bytes




