import unittest
from main.se_parser import get_xml_string, get_file_download_link, extract_zip_file_str, cleaning_xml_string, \
    extract_load


class TestSteelEyeParser(unittest.TestCase):
    """
    Tests various methods of Steel Eye parser script
    """

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        file_url = None

    def test_correct_type_returned_after_hitting_url(self):
        """
        This test ensures that correct type is returned after hitting file_url
        :return: string
        """
        file_url = "some_url"
        self.assertIsInstance(get_xml_string(file_url), str)

    def test_xml_returns_file_download_link(self):
        """
        This test ensures that an url is returned after parsing of the above xml string
        :return: string
        """
        resp = "some xml string"
        expected_return_value = "some value"
        self.assertEquals(get_file_download_link(resp), expected_return_value)

    def get_extract_zip_file_str(self):
        """
        This test ensures that correct type is returned after hitting the extracted url
        :return: string
        """
        download_link = "some_url"
        self.assertIsInstance(get_xml_string(download_link), str)



