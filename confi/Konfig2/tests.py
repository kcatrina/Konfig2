import unittest
from unittest.mock import patch, mock_open, MagicMock
import subprocess
import json
import os

from main import get_package_dependencies, generate_graphviz, save_graph_to_png, load_config

class TestDependencyGraph(unittest.TestCase):
    @patch('subprocess.run')
    def test_get_package_dependencies(self, mock_subprocess_run):
        """Тестирование функции получения зависимостей."""
        mock_subprocess_run.return_value = MagicMock(
            stdout="Depends: libexample1\nDepends: libexample2\n",
            returncode=0
        )

        dependencies = get_package_dependencies("test-package", max_depth=1)
        self.assertEqual(set(dependencies), {"libexample1", "libexample2"})

        mock_subprocess_run.assert_called_with(
            ['apt-cache', 'depends', 'test-package'],
            capture_output=True, text=True, check=True
        )

    def test_generate_graphviz(self):
        """Тестирование генерации графа в формате Graphviz."""
        dependencies = ["libexample1", "libexample2"]
        expected_output = (
            'digraph "test-package" {\n'
            '    "test-package" [shape=box];\n'
            '    "test-package" -> "libexample1";\n'
            '    "test-package" -> "libexample2";\n'
            '}\n'
        )
        result = generate_graphviz("test-package", dependencies)
        self.assertEqual(result, expected_output)

    @patch('subprocess.run')
    def test_save_graph_to_png(self, mock_subprocess_run):
        """Тестирование сохранения графа в PNG (мокаем subprocess)."""
        mock_subprocess_run.return_value = MagicMock(returncode=0)

        dot_file = "test.dot"
        graphviz_path = "/usr/bin/dot"
        output_path = "output.png"

        save_graph_to_png(dot_file, graphviz_path, output_path)

        mock_subprocess_run.assert_called_with(
            [graphviz_path, '-Tpng', dot_file, '-o', output_path],
            check=True
        )

    @patch("builtins.open", new_callable=mock_open, read_data='{"key": "value"}')
    def test_load_config_valid(self, mock_file):
        """Тестирование загрузки корректного конфигурационного файла."""
        config = load_config("config.json")
        self.assertEqual(config, {"key": "value"})
        mock_file.assert_called_with("config.json", "r")

    @patch("builtins.open", side_effect=FileNotFoundError)
    def test_load_config_file_not_found(self, mock_file):
        """Тестирование обработки ошибки при отсутствии файла конфигурации."""
        with self.assertRaises(SystemExit) as cm:
            load_config("missing.json")
        self.assertEqual(cm.exception.code, 1)

    @patch("builtins.open", new_callable=mock_open, read_data='invalid json')
    def test_load_config_invalid_json(self, mock_file):
        """Тестирование обработки ошибки при некорректном JSON формате."""
        with self.assertRaises(SystemExit) as cm:
            load_config("invalid.json")
        self.assertEqual(cm.exception.code, 1)


if __name__ == "__main__":
    unittest.main()
