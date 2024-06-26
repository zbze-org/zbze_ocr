### Генерация контекста по пакету для LLM


```python
import os

def extract_package_content(package_dir):
    markdown_content = []

    # Добавляем название директории
    markdown_content.append(f'{package_dir}/\n')

    # Собираем список файлов
    files = []
    for root, _, filenames in os.walk(package_dir):
        for filename in filenames:
            if filename.endswith('.py'):
                files.append(os.path.join(root, filename))

    # Сортируем файлы для консистентности
    files.sort()

    # Добавляем список файлов
    for file in files:
        rel_path = os.path.relpath(file, package_dir)
        markdown_content.append(f'* {rel_path}')

    markdown_content.append('\n')  # Пустая строка после списка файлов

    # Добавляем содержимое файлов
    for file in files:
        rel_path = os.path.relpath(file, package_dir)
        markdown_content.append(f'# {rel_path}')
        markdown_content.append('```python')
        with open(file, 'r', encoding='utf-8') as f:
            markdown_content.append(f.read())
        markdown_content.append('```\n')

    return '\n'.join(markdown_content)
```