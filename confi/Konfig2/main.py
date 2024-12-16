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


def generate_mermaid(package_name, dependencies):
    """Генерация описания графа зависимостей в формате Mermaid."""
    mermaid_output = "graph TD\n"
    for dep in dependencies:
        mermaid_output += f'    {package_name} --> {dep}\n'
    return mermaid_output


def save_mermaid_to_file(mermaid_code, mermaid_file_path):
    """Сохранение Mermaid-кода в файл."""
    try:
        with open(mermaid_file_path, 'w') as file:
            file.write(mermaid_code)
        print(f"Mermaid граф успешно сохранен в {mermaid_file_path}")
    except IOError as e:
        print(f"Ошибка при сохранении файла Mermaid: {e}")


def convert_mermaid_to_png(mermaid_file_path, output_png_path, mermaid_cli_path):
    """Конвертация графа Mermaid в PNG с использованием Mermaid CLI."""
    try:
        subprocess.run(
            [mermaid_cli_path, "-i", mermaid_file_path, "-o", output_png_path, "--scale", "3"],
            check=True
        )
        print(f"Граф успешно преобразован в PNG: {output_png_path}")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при конвертации Mermaid в PNG: {e}")
        sys.exit(1)


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

    package_name = config.get("package_name")
    output_png_path = config.get("output_png_path")
    max_depth = config.get("max_depth", 1)
    mermaid_cli_path = config.get("mermaid_cli_path")

    if not package_name or not output_png_path or not mermaid_cli_path:
        print("Некорректная конфигурация: Проверьте параметры package_name, output_png_path и mermaid_cli_path.")
        sys.exit(1)

    print(f"Имя пакета: {package_name}")
    print(f"Путь для сохранения PNG: {output_png_path}")
    print(f"Путь к Mermaid CLI: {mermaid_cli_path}")

    print("Получение зависимостей пакета...")
    dependencies = get_package_dependencies(package_name, max_depth)
    print(f"Зависимости: {dependencies}")

    if dependencies:
        # Генерация и сохранение Mermaid-кода
        mermaid_graph = generate_mermaid(package_name, dependencies)
        mermaid_file_path = f"{package_name}_dependencies.mermaid"
        save_mermaid_to_file(mermaid_graph, mermaid_file_path)

        # Конвертация в PNG
        print("Создание PNG изображения...")
        convert_mermaid_to_png(mermaid_file_path, output_png_path, mermaid_cli_path)

        # Удаление промежуточного файла Mermaid
        os.remove(mermaid_file_path)
        print("Визуализация завершена успешно.")
    else:
        print(f"Не удалось получить зависимости для пакета {package_name}.")


if __name__ == "__main__":
    main()
