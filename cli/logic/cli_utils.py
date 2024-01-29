import fnmatch
import os

import click
from tqdm import tqdm


def validate_input_file_path_and_dir_params(input_file_path, input_dir):
    if input_file_path is None and input_dir is None:
        click.echo('Please provide either --input-file-path or --input-dir')
        return False

    if input_file_path is not None and input_dir is not None:
        click.echo('Please provide only one of --input-file-path or --input-dir')
        return False

    return True


def get_files_to_process(input_file_path=None, input_dir=None, file_mask='*.jpg'):
    files_to_process = []
    if input_file_path is not None:
        # Если указан путь к файлу, запускаем обработку только для этого файла
        files_to_process.append(input_file_path)
    elif input_dir is not None:
        # Если указан путь к директории, обходим все файлы внутри директории и запускаем обработку для каждого файла
        files = sorted(os.listdir(input_dir))
        files = [
            os.path.join(input_dir, file_name) for file_name in files
            if os.path.isfile(os.path.join(input_dir, file_name))
        ]
        if file_mask:
            files = fnmatch.filter(files, file_mask)
        files_to_process.extend(files)
    return files_to_process


def generic_file_processor(process_function, files, output_dir=None, description_prefix='', **kwargs):
    progress_bar = tqdm(sorted(files), desc='Processing', unit='file')
    for index, file_path in enumerate(progress_bar):
        path, file_name = os.path.split(file_path)
        progress_bar.set_description(f'Processing with {process_function.__name__} {description_prefix}: {file_name}')

        ext = file_name.split('.')[-1]
        if output_dir is None:
            output_dir = file_path[:-len(ext) - 1]

        os.makedirs(output_dir, exist_ok=True)
        process_function(file_path=file_path, output_dir=output_dir, page=index, **kwargs)
