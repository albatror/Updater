import unittest
from unittest import mock
import configparser
import io
import sys
import os # For path manipulation if needed, and for os.path.exists

# Adjust the Python path to include the directory where updater.py is located
# This assumes test_updater.py is in the same directory as updater.py
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

try:
    from updater import process_offsets_update, load_offsets_ini, ConsoleColors
except ModuleNotFoundError as e:
    print(f"Failed to import from updater: {e}. Ensure updater.py is in the Python path or same directory.")
    sys.exit(1)

# Import requests for its exceptions, used in mocking
import requests

# Mock ConsoleColors to prevent colored output during tests and avoid dependency
# on the actual ConsoleColors class structure if it's complex.
class MockConsoleColors:
    RESET = ''
    BOLD = ''
    UNDERLINE = ''
    RED = ''
    GREEN = ''
    YELLOW = ''
    BLUE = ''
    PURPLE = ''
    CYAN = ''

# Apply the mock globally for all tests in this module
updater_module = sys.modules['updater']
setattr(updater_module, 'ConsoleColors', MockConsoleColors)


class TestUpdater(unittest.TestCase):

    # --- Tests for load_offsets_ini ---

    # Local file scenarios
    @mock.patch('updater.os.path.exists', return_value=True)
    @mock.patch('updater.open', new_callable=mock.mock_open, read_data="[Section1]\nkey1=value1")
    def test_load_ini_local_success(self, mock_file_open, mock_path_exists):
        parser = load_offsets_ini("dummy_path.ini")
        self.assertIsNotNone(parser)
        self.assertIn("Section1", parser)
        self.assertEqual(parser["Section1"]["key1"], "value1")
        mock_path_exists.assert_called_with("dummy_path.ini") # Verify os.path.exists was checked

    @mock.patch('updater.os.path.exists', return_value=False) # Simulate file not existing
    def test_load_ini_local_not_found(self, mock_path_exists):
        # Note: load_offsets_ini for local files first checks os.path.exists (in the interactive part)
        # but the function itself when called with a path directly tries to open it.
        # The current load_offsets_ini doesn't use os.path.exists directly.
        # It relies on `open` raising FileNotFoundError.
        with mock.patch('updater.open', side_effect=FileNotFoundError):
            parser = load_offsets_ini("non_existent_path.ini")
            self.assertIsNone(parser)

    @mock.patch('updater.os.path.exists', return_value=True) # Assume path exists
    @mock.patch('updater.open', side_effect=IOError("Failed to open"))
    def test_load_ini_local_io_error(self, mock_file_open_io_error, mock_path_exists_io):
        parser = load_offsets_ini("dummy_path_io_error.ini")
        self.assertIsNone(parser)

    @mock.patch('updater.os.path.exists', return_value=True)
    @mock.patch('updater.open', new_callable=mock.mock_open, read_data="this is not valid ini content")
    def test_load_ini_local_invalid_content(self, mock_file_open_invalid, mock_path_exists_invalid):
        parser = load_offsets_ini("dummy_path_invalid.ini")
        self.assertIsNone(parser) # Expect None due to configparser.Error

    # URL scenarios
    @mock.patch('updater.requests.get')
    def test_load_ini_url_success(self, mock_requests_get):
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.text = "[SectionURL]\nkey_url=value_url"
        mock_response.raise_for_status = mock.Mock() # Ensure raise_for_status doesn't error
        mock_requests_get.return_value = mock_response

        parser = load_offsets_ini("http://example.com/offsets.ini")
        self.assertIsNotNone(parser)
        self.assertIn("SectionURL", parser)
        self.assertEqual(parser["SectionURL"]["key_url"], "value_url")

    @mock.patch('updater.requests.get', side_effect=requests.exceptions.RequestException("Network error"))
    def test_load_ini_url_request_exception(self, mock_requests_get_exception):
        parser = load_offsets_ini("http://example.com/offsets_error.ini")
        self.assertIsNone(parser)

    @mock.patch('updater.requests.get')
    def test_load_ini_url_bad_status(self, mock_requests_get_bad_status):
        mock_response = mock.Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Client Error")
        # Simulate response object for status_code access
        mock_response.response = mock.Mock()
        mock_response.response.status_code = 404
        mock_requests_get_bad_status.return_value = mock_response
        
        parser = load_offsets_ini("http://example.com/offsets_not_found.ini")
        self.assertIsNone(parser)

    @mock.patch('updater.requests.get')
    def test_load_ini_url_invalid_content(self, mock_requests_get_invalid_url_content):
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.text = "this is not valid ini from url"
        mock_requests_get_invalid_url_content.return_value = mock_response

        parser = load_offsets_ini("http://example.com/invalid_offsets.ini")
        self.assertIsNone(parser) # Expect None due to configparser.Error

    def test_load_type2_json_success(self):
        json_content = """
Dumper initialized successfully
Dump completed
{
  "Mics": {
    "CHLClient": "0x29BC348",
    "GameVersion": "v1.2.3"
  },
  "RecvTable": {
    "DT_BaseEntity": {
      "m_iTeamNum": "0x334"
    }
  },
  "weaponSettings": {
    "ammo_clip_size": "0x8FC"
  }
}
"""
        with mock.patch('updater.open', new_callable=mock.mock_open, read_data=json_content):
            with mock.patch('updater.os.path.exists', return_value=True):
                config = load_offsets_ini("dummy_type2.ini")
                self.assertIsNotNone(config)
                self.assertIn("Miscellaneous", config)
                self.assertEqual(config["Miscellaneous"]["CHLClient"], "0x29BC348")
                self.assertEqual(config["Miscellaneous"]["GameVersion"], "v1.2.3")
                self.assertIn("RecvTable.DT_BaseEntity", config)
                self.assertEqual(config["RecvTable.DT_BaseEntity"]["m_iTeamNum"], "0x334")
                self.assertIn("WeaponSettings", config)
                self.assertEqual(config["WeaponSettings"]["ammo_clip_size"], "0x8FC")

    # --- Tests for process_offsets_update ---
    def test_process_update_logic(self):
        # Setup INI data
        ini_data = {
            "Miscellaneous": {
                "GameVersion": "v1.2.3",
                "cl_entitylist": "0x111222"
            },
            "TestSection": {
                "TestKey": "0x222333",
                "AnotherKey": "0x333444"
            }
        }

        # Setup .h lines
        h_lines_input = [
            "constexpr uintptr_t dwEntityList = 0x123456; //[Miscellaneous].cl_entitylist updated 2023/01/01",
            "//Date 2023/01/01",
            "//GameVersion = v1.0.0",
            "constexpr uintptr_t dwNonExistent = 0xdeadbeef; //[Miscellaneous].NonExistentKey updated 2023/01/01",
            "//UnrecognizedComment",
            "#define NO_COMMENT_OFFSET 0x12345",
            "constexpr uintptr_t dwTestKey = 0x222222; //[TestSection].TestKey updated 2023/01/01",
            "// [MalformedSection.KeySyntax", # This should be unrecognized
            "constexpr uintptr_t dwNoIniValue = 0x444444; //[NoSection].NoKey updated 2023/01/01",
        ]
        current_date_str = "2023/10/26" # Example current date

        # Execute
        updated_lines, not_found, unrecognized = process_offsets_update(
            list(h_lines_input), # Pass a copy
            ini_data, 
            current_date_str
        )
        
        # Assert updated lines
        self.assertIn("0x111222", updated_lines[0]) # Check cl_entitylist
        self.assertIn(f"updated {current_date_str}", updated_lines[0])
        
        self.assertEqual(f"//Date {current_date_str}", updated_lines[1]) # Check Date
        
        self.assertEqual(f"//GameVersion = v1.2.3", updated_lines[2]) # Check GameVersion
        
        self.assertIn("0x222333", updated_lines[6]) # Check TestKey
        self.assertIn(f"updated {current_date_str}", updated_lines[6])

        # Assert not_found lines
        # Line 3: dwNonExistent's key "NonExistentKey" is not in ini_data["Miscellaneous"]
        self.assertIn(h_lines_input[3], not_found)
        # Line 8: dwNoIniValue's section "NoSection" is not in ini_data
        self.assertIn(h_lines_input[8], not_found)


        # Assert unrecognized lines
        # Line 4: "//UnrecognizedComment" - comment keyword not special, not [Section].Key
        self.assertIn(h_lines_input[4], unrecognized)
        # Line 7: "// [MalformedSection.KeySyntax" - starts with '[' but not valid [Section].Key
        self.assertIn(h_lines_input[7], unrecognized)

        # Check counts of found/unrecognized to ensure no overlaps or missed lines
        self.assertEqual(len(not_found), 2)
        self.assertEqual(len(unrecognized), 2)
        self.assertEqual(len(updated_lines), len(h_lines_input))


if __name__ == '__main__':
    unittest.main()
