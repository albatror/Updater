import unittest
from unittest import mock
import configparser
import io
import sys
import os
import json

# Adjust the Python path to include the directory where updater.py is located
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

try:
    from updater import process_offsets_update, load_offsets_data, ConsoleColors
except ModuleNotFoundError as e:
    print(f"Failed to import from updater: {e}. Ensure updater.py is in the Python path or same directory.")
    sys.exit(1)

# Import requests for its exceptions, used in mocking
import requests

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

updater_module = sys.modules['updater']
setattr(updater_module, 'ConsoleColors', MockConsoleColors)


class TestUpdater(unittest.TestCase):

    # --- Tests for load_offsets_data ---

    @mock.patch('updater.open', new_callable=mock.mock_open, read_data="[Section1]\nkey1=value1")
    def test_load_ini_local_success(self, mock_file_open):
        data = load_offsets_data("dummy_path.ini")
        self.assertIsNotNone(data)
        self.assertIn("Section1", data)
        self.assertEqual(data["Section1"]["key1"], "value1")

    @mock.patch('updater.open', new_callable=mock.mock_open, read_data='header\n{"Mics": {"Key": "0x123"}}')
    def test_load_json_local_success(self, mock_file_open):
        data = load_offsets_data("dummy_path.json")
        self.assertIsNotNone(data)
        self.assertIn("Miscellaneous", data)
        self.assertEqual(data["Miscellaneous"]["key"], "0x123")

    @mock.patch('updater.open', new_callable=mock.mock_open,
                read_data='header\n{"RecvTable": {"DT_Base": {"m_health": "0x10"}}}')
    def test_load_json_flattening(self, mock_file_open):
        data = load_offsets_data("dummy_path.json")
        self.assertIsNotNone(data)
        self.assertIn("RecvTable.DT_Base", data)
        self.assertEqual(data["RecvTable.DT_Base"]["m_health"], "0x10")

    @mock.patch('updater.open', new_callable=mock.mock_open,
                read_data='header\n{"weaponSettings": {"active_crosshair_count": "0x280"}}')
    def test_load_json_weapon_settings(self, mock_file_open):
        data = load_offsets_data("dummy_path.json")
        self.assertIsNotNone(data)
        self.assertIn("WeaponSettings", data)
        self.assertEqual(data["WeaponSettings"]["active_crosshair_count"], "0x280")

    @mock.patch('updater.requests.get')
    def test_load_ini_url_success(self, mock_requests_get):
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.text = "[SectionURL]\nkey_url=value_url"
        mock_response.raise_for_status = mock.Mock()
        mock_requests_get.return_value = mock_response

        data = load_offsets_data("http://example.com/offsets.ini")
        self.assertIsNotNone(data)
        self.assertIn("SectionURL", data)
        self.assertEqual(data["SectionURL"]["key_url"], "value_url")

    # --- Tests for process_offsets_update ---
    def test_process_update_logic_fuzzy(self):
        # Setup data with some prefixes
        data = {
            "Miscellaneous": {
                "lastvisibletime": "0x111",
                "gameversion": "v1.2.3"
            },
            "RecvTable.DT_BaseAnimating": {
                "nforcebone": "0x222"
            }
        }

        # Setup .h lines with prefixes in tags. Use valid hex values for replacement to work.
        h_lines_input = [
            "#define OFFSET_VISIBLE_TIME 0x123 //[Miscellaneous].CPlayer!lastVisibleTime updated 2023/01/01",
            "//GameVersion",
            "#define OFFSET_BONES 0x456 //[RecvTable.DT_BaseAnimating].m_nForceBone updated 2023/01/01",
        ]
        current_date_str = "2023/10/26"

        updated_lines, not_found, unrecognized = process_offsets_update(
            list(h_lines_input),
            data,
            current_date_str
        )
        
        self.assertIn("0x111", updated_lines[0])
        self.assertNotIn("0x123", updated_lines[0])
        self.assertEqual(f"//GameVersion = v1.2.3", updated_lines[1])
        self.assertIn("0x222", updated_lines[2])
        self.assertNotIn("0x456", updated_lines[2])
        self.assertEqual(len(not_found), 0)
        self.assertEqual(len(unrecognized), 0)


if __name__ == '__main__':
    unittest.main()
