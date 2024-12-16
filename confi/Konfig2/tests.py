import unittest
from unittest.mock import patch, mock_open, MagicMock
import subprocess
import json
import os

from main import (get_package_dependencies, generate_mermaid,
                     save_mermaid_to_file, convert_mermaid_to_png, load_config)

class TestProgramFunctions(unittest.TestCase):

    # Тест get_package_dependencies
    @patch("subprocess.run")
    def test_get_package_dependencies(self, mock_run):
        # Настройка мока для subprocess.run
        mock_run.return_value.stdout = "Depends: libexample1\nDepends: libexample2\n"

        dependencies = get_package_dependencies("test_package", max_depth=1)
        self.assertEqual(set(dependencies), {"libexample1", "libexample2"})

        # Проверка вызова команды
        mock_run.assert_called_with(['apt-cache', 'depends', "test_package"], capture_output=True, text=True, check=True)

    @patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, 'apt-cache'))
    def test_get_package_dependencies_error(self, mock_run):
        dependencies = get_package_dependencies("bad_package", max_depth=1)
        self.assertEqual(dependencies, [])  # Ожидается пустой список

    # Тест generate_mermaid
    def test_generate_mermaid(self):
        package_name = "test_package"
        dependencies = ["libexample1", "libexample2"]
        expected_output = "graph TD\n    test_package --> libexample1\n    test_package --> libexample2\n"
        result = generate_mermaid(package_name, dependencies)
        self.assertEqual(result, expected_output)

    # Тест save_mermaid_to_file
    @patch("builtins.open", new_callable=mock_open)
    def test_save_mermaid_to_file(self, mock_file):
        mermaid_code = "graph TD\n    test_package --> libexample1\n"
        file_path = "output.mermaid"
        save_mermaid_to_file(mermaid_code, file_path)
        mock_file.assert_called_with(file_path, 'w')
        mock_file().write.assert_called_once_with(mermaid_code)

    # Тест convert_mermaid_to_png
    @patch("subprocess.run")
    def test_convert_mermaid_to_png(self, mock_run):
        mermaid_file = "input.mermaid"
        output_png = "output.png"
        cli_path = "/usr/bin/mmdc"
        convert_mermaid_to_png(mermaid_file, output_png, cli_path)
        mock_run.assert_called_with(
            [cli_path, "-i", mermaid_file, "-o", output_png, "--scale", "3"],
            check=True
        )

    @patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, 'mmdc'))
    def test_convert_mermaid_to_png_error(self, mock_run):
        with self.assertRaises(SystemExit):  # Проверка на sys.exit(1)
            convert_mermaid_to_png("input.mermaid", "output.png", "/usr/bin/mmdc")

    # Тест load_config
    @patch("builtins.open", new_callable=mock_open, read_data='{"package_name": "test", "output_png_path": "output.png", "mermaid_cli_path": "/usr/bin/mmdc"}')
    def test_load_config(self, mock_file):
        config = load_config("config.json")
        self.assertEqual(config["package_name"], "test")
        self.assertEqual(config["output_png_path"], "output.png")
        self.assertEqual(config["mermaid_cli_path"], "/usr/bin/mmdc")

    def test_load_config_file_not_found(self):
        with self.assertRaises(SystemExit):
            load_config("non_existent.json")

    @patch("builtins.open", new_callable=mock_open, read_data='invalid_json')
    def test_load_config_json_decode_error(self, mock_file):
        with self.assertRaises(SystemExit):
            load_config("bad_config.json")

if __name__ == "__main__":
    unittest.main()
