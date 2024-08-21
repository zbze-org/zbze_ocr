# Main

## Оглавление
1. [Подготовка окружения](#подготовка-окружения)
   1. [Создание виртуального окружения](#создание-виртуального-окружения-с-python310)
   2. [Установка зависимостей](#установка-python-зависимостей)
   3. [Проверка и установка дополнительных инструментов](#проверка-и-установка-дополнительных-инструментов)
      - [ImageMagick](#imagemagick) 
      - [OCRmyPDF](#ocrmypdf)
      - [Tesseract](#tesseract)
      - [Добавление языковой модели для Tesseract](#добавление-языковой-модели-для-tesseract)
      - [Unpaper](#unpaper)
2. [Подготовка PDF для OCR](#подготовка-pdf-для-ocr)
   1. [Подготовка файлов](#подготовка-файлов)
   2. [Запуск обработки](#запуск-обработки)
   3. [Результаты обработки](#результаты-обработки)
3. [Запуск OCR](#запуск-ocr)

## Подготовка окружения

### Создание виртуального окружения с Python3.10

```shell
python3.10 -m venv venv
```

### Установка Python зависимостей

```shell
pip install -r requirements.txt
```

### Проверка и установка дополнительных инструментов

#### ImageMagick

проверка версии:
```shell
convert --version
```

Пример вывода:
```shell
Version: ImageMagick 7.1.1-34 Q16-HDRI aarch64 22301 https://imagemagick.org
Copyright: (C) 1999 ImageMagick Studio LLC
License: https://imagemagick.org/script/license.php
Features: Cipher DPC HDRI Modules OpenMP(5.0) 
Delegates (built-in): bzlib fontconfig freetype gslib heic jng jp2 jpeg jxl lcms lqr ltdl lzma openexr png ps raw tiff webp xml zlib zstd
Compiler: gcc (4.2)
```

Для установки следуйте инструкциям: [Install ImageMagick](https://imagemagick.org/script/download.php)


#### OCRmyPDF

Проверка версии:
```shell
ocrmypdf --version
```

Для установки следуйте инструкциям: [Install OCRmyPDF](https://ocrmypdf.readthedocs.io/en/latest/installation.html)

#### Tesseract

Проверка версии:
```shell
tesseract --version 
```

Пример вывода:
```shell
tesseract --version                         
tesseract 5.4.1
 leptonica-1.84.1
  libgif 5.2.1 : libjpeg 8d (libjpeg-turbo 3.0.0) : libpng 1.6.43 : libtiff 4.6.0 : zlib 1.2.11 : libwebp 1.4.0 : libopenjp2 2.5.2
 Found NEON
 Found libarchive 3.7.4 zlib/1.2.11 liblzma/5.4.6 bz2lib/1.0.8 liblz4/1.9.4 libzstd/1.5.6
 Found libcurl/7.88.1 SecureTransport (LibreSSL/3.3.6) zlib/1.2.11 nghttp2/1.51.0
```

Для установки следуйте инструкциям: [Install Tesseract](https://tesseract-ocr.github.io/tessdoc/Installation.html)

#### Добавление языковой модели для Tesseract

```shell
cp trained_data/kbd_finetuned.traineddata /usr/share/tesseract-ocr/5/tessdata/kbd.traineddata
```

Проверка добавления языка:
```shell
tesseract --list-langs | grep kbd
```

#### Unpaper

Проверка версии:
```shell
unpaper --version
```

Установка:
- Linux (Debian/Ubuntu):
  ```shell
  apt-get install -y unpaper
  ```
- MacOS:
  ```shell
  brew install unpaper
  ```

## Подготовка PDF для OCR

### Подготовка файлов

1. Перейдите в директорию cli:
   ```shell
   cd cli
   ```

2. Скопируйте PDF файл в директорию `data/pdfs`:
   ```
   data/pdfs
   ├── 100-mafiedz-serebii-tkhygekher-iape-tom-povestkher-1995ge.pdf
   ├── 101-kermokue-kh-adyge-khybaryzhkher.pdf
   ├── 104-kambii-dzhefar-dyshche-ueshkh.pdf
   └── 109-alo-l-uerii-dade-turykhkher-1989.pdf
   ```

### Запуск обработки

Запустите цепочку обработки через make:
```shell
make all PDF_FILE=104-kambii-dzhefar-dyshche-ueshkh.pdf
```

Пример вывода логов обработки:
```shell
Выполняются шаги: check-input split-pdf-to-jpeg split-book-layout unpaper-images rotate-images apply-image-filters standartize-images join-images-to-pdf copy-original-pdf clean-tmp-dir check-result
for step in check-input split-pdf-to-jpeg split-book-layout unpaper-images rotate-images apply-image-filters standartize-images join-images-to-pdf copy-original-pdf clean-tmp-dir check-result; do \
                make $step ; \
        done
Проверка входных данных...
Разделение PDF на JPEG...
python split_pdf_to_jpeg.py -i ../data/pdfs/104-kambii-dzhefar-dyshche-ueshkh.pdf -o ../data/pdf_processed/104-kambii-dzhefar-dyshche-ueshkh.pdf/00_jpeg
Converting PDF to JPEG: 100%|██████████████████████████████████████████████████████████████████████████████████████████████████████| 145/145 [00:39<00:00,  3.67page/s]
Разделение макета книги...
python split_book_layout.py -d ../data/pdf_processed/104-kambii-dzhefar-dyshche-ueshkh.pdf/00_jpeg -o ../data/pdf_processed/104-kambii-dzhefar-dyshche-ueshkh.pdf/01_layout_splitted
Processing with split_book_processing : 100%|██████████████████████████████████████████████████████████████████████████████████████| 145/145 [00:08<00:00, 16.56file/s]
Постобработка скана...
python unpaper_img.py -d ../data/pdf_processed/104-kambii-dzhefar-dyshche-ueshkh.pdf/01_layout_splitted -o ../data/pdf_processed/104-kambii-dzhefar-dyshche-ueshkh.pdf/02_unpapered
Processing with unpaper_processing : 100%|█████████████████████████████████████████████████████████████████████████████████████████| 288/288 [11:22<00:00,  2.37s/file]
Поворот изображений...
python rotate_img.py -d ../data/pdf_processed/104-kambii-dzhefar-dyshche-ueshkh.pdf/02_unpapered -o ../data/pdf_processed/104-kambii-dzhefar-dyshche-ueshkh.pdf/03_rotated
Processing with rotate_image : 100%|███████████████████████████████████████████████████████████████████████████████████████████████| 288/288 [00:24<00:00, 11.91file/s]
Применение фильтров к изображениям...
python apply_img_filters.py -d ../data/pdf_processed/104-kambii-dzhefar-dyshche-ueshkh.pdf/03_rotated -o ../data/pdf_processed/104-kambii-dzhefar-dyshche-ueshkh.pdf/04_filtered -g 0
Processing with apply_image_filters Brightness 1.4 Contrast 1.9 Sharpness 1.7: 100%|███████████████████████████████████████████████| 288/288 [01:08<00:00,  4.21file/s]
Стандартизация изображений...
python standartize_img.py -d ../data/pdf_processed/104-kambii-dzhefar-dyshche-ueshkh.pdf/04_filtered -o ../data/pdf_processed/104-kambii-dzhefar-dyshche-ueshkh.pdf/05_standartized
Processing with standardize_img_width : 100%|██████████████████████████████████████████████████████████████████████████████████████| 288/288 [00:17<00:00, 16.81file/s]
Склейка изображений в PDF...
python join_jpeg_to_pdf.py -d ../data/pdf_processed/104-kambii-dzhefar-dyshche-ueshkh.pdf/05_standartized -o ../data/pdf_processed/104-kambii-dzhefar-dyshche-ueshkh.pdf/processed_104-kambii-dzhefar-dyshche-ueshkh.pdf
Processing images: 100%|█████████████████████████████████████████████████████████████████████████████████████████████████████████████| 288/288 [00:33<00:00,  8.56it/s]
PDF created successfully: ../data/pdf_processed/104-kambii-dzhefar-dyshche-ueshkh.pdf/processed_104-kambii-dzhefar-dyshche-ueshkh.pdf
Копирование оригинального PDF...
cp ../data/pdfs/104-kambii-dzhefar-dyshche-ueshkh.pdf ../data/pdf_processed/104-kambii-dzhefar-dyshche-ueshkh.pdf/original_104-kambii-dzhefar-dyshche-ueshkh.pdf
Очистка временной директории...
Обнаружен обработанный PDF. Удаление временных файлов...
Временные директории очищены.
Проверка результата...
ls -haltr ../data/pdf_processed/104-kambii-dzhefar-dyshche-ueshkh.pdf
total 610344
drwxr-xr-x  6 panagoa  staff   192B Aug 21 13:16 ..
-rw-r--r--  1 panagoa  staff   284M Aug 21 13:31 processed_104-kambii-dzhefar-dyshche-ueshkh.pdf
-rw-r--r--  1 panagoa  staff    14M Aug 21 13:31 original_104-kambii-dzhefar-dyshche-ueshkh.pdf
drwxr-xr-x  4 panagoa  staff   128B Aug 21 13:31 .
```

### Результаты обработки

Результат обработки появится в директории `data/pdf_processed`:

просмотр содержимого директории:
```shell
tree ../data/pdf_processed/104-kambii-dzhefar-dyshche-ueshkh.pdf
```

```shell    
../data/pdf_processed/104-kambii-dzhefar-dyshche-ueshkh.pdf
├── original_104-kambii-dzhefar-dyshche-ueshkh.pdf
└── processed_104-kambii-dzhefar-dyshche-ueshkh.pdf

1 directory, 2 files
```

переход в директорию:
```shell
cd ../data/pdf_processed/104-kambii-dzhefar-dyshche-ueshkh.pdf
```

## Запуск OCR

### Через OCRmyPDF

Детальное описание процесса OCR находится в [документе](tesseract/readme.md).

Доступны два варианта запуска OCR (подробности в указанном документе).

#### cli
```shell
ocrmypdf -l kbd --force-ocr --clean --deskew --unpaper-args '--layout single' processed_104-kambii-dzhefar-dyshche-ueshkh.pdf  104-kambii-dzhefar-dyshche-ueshkh.ocr.pdf --sidecar 104-kambii-dzhefar-dyshche-ueshkh.txt --tesseract-config ../../../tesseract/kdb.base.config.txt
```

#### через docker
```shell
ocrmypdf_kbd -l kbd --force-ocr --clean --deskew --unpaper-args '--layout single' processed_104-kambii-dzhefar-dyshche-ueshkh.pdf 104-kambii-dzhefar-dyshche-ueshkh.ocr.pdf --sidecar 104-kambii-dzhefar-dyshche-ueshkh.txt --tesseract-config /etc/ocrmypdf/kbd.config
```

### запуск OCR и вычитка через web сервис (TBD)
Этот раздел находится в разработке. В будущем здесь будет представлена информация о том, как запустить процесс OCR и выполнить вычитку результатов через веб-сервис.