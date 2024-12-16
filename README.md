Конфигурационное управление

### Задание №2

## Постановка задачи

Разработать инструмент командной строки для визуализации графа
зависимостей, включая транзитивные зависимости. Сторонние средства для
получения зависимостей использовать нельзя.
Зависимости определяются по имени пакета ОС Ubuntu (apt). Для описания
графа зависимостей используется представление Mermaid. Визуализатор должен
выводить результат в виде сообщения об успешном выполнении и сохранять граф
в файле формата png.
Конфигурационный файл имеет формат json и содержит:
- Путь к программе для визуализации графов.
- Имя анализируемого пакета.
- Путь к файлу с изображением графа зависимостей.
- Максимальная глубина анализа зависимостей.
Все функции визуализатора зависимостей должны быть покрыты тестами.

Для запуска используется WSL(чтобы брать зависимости с Ubuntu) ввести в консоль: 

```python3 main.py config.json```

Для запуска тестов ввести в консоль: 

```python3 tests.py```

Этот код предназначен для получения зависимостей пакета в Linux, 

визуализации их в виде графа Mermaid и конвертации результата в PNG-изображение 

с использованием Mermaid CLI. Программа гибко настраивается через JSON-файл конфигурации.


## Описание алгоритма

1. Функция get_package_dependencies(package_name, max_depth, current_depth=0):

Получает список зависимостей пакета с использованием команды apt-cache depends (только для систем с apt).
Логика работы:
- Запускает apt-cache depends <package_name> и парсит вывод для строк, начинающихся с Depends: или Recommends:.
- Рекурсивно вызывает себя для каждого найденного пакета, увеличивая текущую глубину (current_depth).
- Прерывает рекурсию при достижении max_depth.
- Возвращает уникальный список зависимостей, используя set.
Обработка ошибок:
- Если выполнение команды завершается с ошибкой, выводит сообщение об ошибке и возвращает пустой список.

2. Функция generate_mermaid(package_name, dependencies):

Генерирует текст в формате Mermaid для визуализации зависимостей пакета в виде графа.
Логика работы:
- Создает строку с Mermaid-синтаксисом для графа graph TD.
- Для каждой зависимости добавляет связь package_name --> dependency.
- Возвращает сгенерированный текст.

3. Функция save_mermaid_to_file(mermaid_code, mermaid_file_path):

Сохраняет Mermaid-код в файл.
Логика работы:
- Открывает файл по указанному пути в режиме записи и записывает Mermaid-код.
- Выводит сообщение об успешном сохранении.
Обработка ошибок:
- При ошибках ввода-вывода выводит сообщение об ошибке.

4. Функция convert_mermaid_to_png(mermaid_file_path, output_png_path, mermaid_cli_path):

Конвертирует Mermaid-файл в PNG-изображение с использованием Mermaid CLI.
Логика работы:
- Запускает Mermaid CLI с аргументами для конвертации файла:
- mmdc -i input.mermaid -o output.png --scale 3
- Масштаб увеличивается с помощью параметра --scale 3 для улучшения качества изображения.
Обработка ошибок:
- Если команда завершается с ошибкой, программа выводит сообщение и завершает выполнение с кодом 1.

5. Функция load_config(config_path):

Загружает конфигурацию из JSON-файла.
Логика работы:
- Открывает указанный JSON-файл и читает его содержимое.
- Возвращает загруженные данные в виде словаря.
- Обработка ошибок:
- Если файл не найден, программа выводит сообщение и завершает выполнение.
- Если файл содержит некорректный JSON, также выводится сообщение и выполнение завершается.

6. Главная функция main()
   
Основная функция программы.
Логика работы:
- Проверяет наличие аргумента командной строки (путь к конфигурационному файлу).
- Загружает конфигурацию с помощью load_config.
- Извлекает параметры: package_name, output_png_path, max_depth, mermaid_cli_path.
- Проверяет корректность конфигурации.
- Получает зависимости пакета с помощью get_package_dependencies.
- Генерирует Mermaid-код и сохраняет его в файл.
- Конвертирует Mermaid-файл в PNG.
- Удаляет временный Mermaid-файл.
- Выводит сообщение об успешном завершении.

Файл зависимостей:
![image](https://github.com/user-attachments/assets/0131a7ca-24cf-4623-8f4b-a4a9d9401027)

## Тестирование программы

1. Вывод программы:

![image](https://github.com/user-attachments/assets/26877802-b55e-458f-bdd4-d332f9484282)

2. Появившиеся новые файлы:

![image](https://github.com/user-attachments/assets/d7c426e9-ce14-4f55-80d3-ef561f543b3e)

3. Unittest:

![image](https://github.com/user-attachments/assets/d761af2c-c14e-4560-a030-4999c0400b25)
