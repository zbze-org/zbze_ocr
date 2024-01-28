import concurrent
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor
from subprocess import list2cmdline

from tqdm import tqdm

from .const import TESSTRAIN_DIR


def _run_prepare(name, ground_truth_dir, tesstrain_dir=TESSTRAIN_DIR):
    with open(os.path.join(ground_truth_dir, f'{name}.box'), "w") as box_file:
        cmd1 = [
            "PYTHONIOENCODING=utf-8", "python3", os.path.join(tesstrain_dir, "generate_line_box.py"),
            "-i", os.path.join(ground_truth_dir, f'{name}.png'),
            "-t", os.path.join(ground_truth_dir, f'{name}.gt.txt'),
        ]
        cmd1 = list2cmdline(cmd1)
        subprocess.run(cmd1, shell=True, stdout=box_file, text=True)

    cmd2 = [
        "tesseract",
        os.path.join(ground_truth_dir, f"{name}.png"),
        os.path.join(ground_truth_dir, f"{name}"),
        "--psm", "13", "lstm.train"
    ]
    cmd2 = list2cmdline(cmd2)
    subprocess.run(cmd2, shell=True, text=True)


def run_prepare(boxes, ground_truth_dir, tesstrain_dir=TESSTRAIN_DIR, par_factor=4):
    with tqdm(total=len(boxes)) as pbar, ThreadPoolExecutor(max_workers=par_factor) as executor:
        futures = [
            executor.submit(
                _run_prepare,
                b,
                ground_truth_dir,
                tesstrain_dir,
            )
            for b in boxes
        ]
        count = 0
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
                count += 1
                if count % 100 == 0:
                    pbar.update(1)
            except Exception as e:
                raise e


def get_wo_boxes(ground_truth_dir):
    png = [f for f in os.listdir(ground_truth_dir) if f.endswith('.png')]
    lstmf = [f for f in os.listdir(ground_truth_dir) if f.endswith('.lstmf')]

    wo_boxes = set(
        [f.replace('.png', '') for f in png]
    ).difference(
        [f.replace('.lstmf', '') for f in lstmf]
    )
    return wo_boxes


def prepare_box_lstmf(ground_truth_dir, walk_subdirs=False, par_factor=4):
    if walk_subdirs:
        for dir_name in os.listdir(ground_truth_dir):
            ground_truth_dir_sub = os.path.join(ground_truth_dir, dir_name)
            if not os.path.isdir(os.path.join(ground_truth_dir, dir_name)):
                continue

            wo_boxes = get_wo_boxes(ground_truth_dir_sub)
            run_prepare(wo_boxes, ground_truth_dir_sub, par_factor=par_factor)
    else:
        wo_boxes = get_wo_boxes(ground_truth_dir)
        run_prepare(wo_boxes, ground_truth_dir, par_factor=par_factor)
