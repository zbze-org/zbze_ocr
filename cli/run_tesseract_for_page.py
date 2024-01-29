import os
from subprocess import Popen, PIPE

import click
from tqdm import tqdm

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TESSERACT_CONFIG = os.path.join(PROJECT_DIR, 'tesseract', 'kdb.base.config.txt')


@click.command()
@click.option('--tesseract-lang', '-l', default=None, help='Tesseract language')
@click.option('--jpg-dir', '-j', default=None, help='Directory with JPEG files')
@click.option('--txt-dir', '-t', default=None, help='Directory for output TXT files')
def run_tesseract_for_page(tesseract_lang, jpg_dir, txt_dir):
    if tesseract_lang is None:
        click.echo("Please provide a Tesseract language.")
        return

    if jpg_dir is None:
        click.echo("Please provide a directory with JPEG files.")
        return

    if txt_dir is None:
        click.echo("Please provide a directory for output TXT files.")
        return

    os.makedirs(txt_dir, exist_ok=True)

    jpgs = sorted(os.listdir(jpg_dir))
    pgbar = tqdm(jpgs)

    for jpeg_file_name in pgbar:
        pgbar.set_description(f'Processing {jpeg_file_name}')
        jpg_path = os.path.join(jpg_dir, jpeg_file_name)
        txt_path = os.path.join(txt_dir, jpeg_file_name.replace('.jpg', ''))
        command = [
            'tesseract', '-l', tesseract_lang,
            jpg_path, txt_path, TESSERACT_CONFIG
        ]
        p = Popen(command, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        output, err = p.communicate()
        print(f'output: {output} err: {err}')


if __name__ == '__main__':
    run_tesseract_for_page()
