import subprocess
import json
import sys
import os

def get_package_dependencies(package_name, max_depth, current_depth=0):
    """Получение зависимостей пакета с учетом максимальной глубины."""
    if current_depth >= max_depth:
        return []

    try:
        result = subprocess.run(
            ['apt-cache', 'depends', package_name],
            capture_output=True, text=True, check=True
        )
        output = result.stdout
        dependencies = []
        for line in output.splitlines():
            line = line.strip()
            if line.startswith("Depends:") or line.startswith("Recommends:"):
                dep = line.split()[1]
                dependencies.append(dep)

        all_dependencies = dependencies[:]
        for dep in dependencies:
            all_dependencies += get_package_dependencies(dep, max_depth, current_depth + 1)
        return list(set(all_dependencies))
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при получении зависимостей для {package_name}: {e}")
        return []


def generate_graphviz(package_name, dependencies):
    """Генерация кода графа для программы визуализатора Graphviz."""
    dot_output = f'digraph "{package_name}" {{\n'
    dot_output += f'    "{package_name}" [shape=box];\n'

    for dep in dependencies:
        dot_output += f'    "{package_name}" -> "{dep}";\n'

    dot_output += "}\n"
    return dot_output


def save_graph_to_png(dot_file, graphviz_path, output_path):
    """Сохранение графа в формате PNG."""
    try:
        subprocess.run(
            [graphviz_path, '-Tpng', dot_file, '-o', output_path],
            check=True
        )
        print(f"Граф успешно сохранен в {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при создании изображения: {e}")


def load_config(config_path):
    """Загрузка конфигурации из JSON-файла."""
    try:
        with open(config_path, 'r') as file:
            config = json.load(file)
        return config
    except FileNotFoundError:
        print(f"Файл конфигурации {config_path} не найден.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Ошибка в формате JSON файла конфигурации {config_path}.")
        sys.exit(1)


def main():
    if len(sys.argv) != 2:
        print("Использование: python program.py <config_path>")
        sys.exit(1)

    config_path = sys.argv[1]
    config = load_config(config_path)

    graphviz_path = config.get("graphviz_path")
    package_name = config.get("package_name")
    output_path = config.get("output_path")
    max_depth = config.get("max_depth", 1)

    if not graphviz_path or not package_name or not output_path:
        print("Некорректная конфигурация: Проверьте параметры graphviz_path, package_name и output_path.")
        sys.exit(1)

    print(f"Путь к Graphviz: {graphviz_path}")
    print(f"Имя пакета: {package_name}")
    print(f"Путь для сохранения изображения: {output_path}")

    print("Получение зависимостей пакета...")
    dependencies = get_package_dependencies(package_name, max_depth)
    print(f"Зависимости: {dependencies}")

    if dependencies:
        dot_graph = generate_graphviz(package_name, dependencies)
        dot_filename = f"{package_name}_dependencies.dot"

        with open(dot_filename, 'w') as f:
            f.write(dot_graph)

        print("Создание PNG изображения...")
        save_graph_to_png(dot_filename, graphviz_path, output_path)

        os.remove(dot_filename)
        print("Визуализация завершена успешно.")
    else:
        print(f"Не удалось получить зависимости для пакета {package_name}.")


if __name__ == "__main__":
    main()
