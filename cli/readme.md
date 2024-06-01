
```sh
cd app/cli
```

### Split pdf to jpeg
```shell
sh split_pdf_to_jpeg.sh Къалэмбии_Адыгэ_хъыбархэр_1978.pdf
```

### Split book layout two pages to one page
```shell
python split_book_layout.py -d ../../media/tmp_processing/Къалэмбии_Адыгэ_хъыбархэр_1978.pdf -o ../../media/tmp_processing/Къалэмбии_Адыгэ_хъыбархэр_1978.pdf_splitted
```

### rotate images
```shell
python rotate_img.py -d ../../media/tmp_processing/Къалэмбии_Адыгэ_хъыбархэр_1978.pdf_splitted -o ../../media/tmp_processing/Къалэмбии_Адыгэ_хъыбархэр_1978.pdf_rotated
```

### smooth images
```shell
python smooth_img.py -d ../../media/tmp_processing/Къалэмбии_Адыгэ_хъыбархэр_1978.pdf_rotated -o ../../media/tmp_processing/Къалэмбии_Адыгэ_хъыбархэр_1978.pdf_smoothened
```

### apply image filters 
```shell
 python apply_img_filters.py -d ../../media/tmp_processing/Къалэмбии_Адыгэ_хъыбархэр_1978.pdf_smoothened -o ../../media/tmp_processing/Къалэмбии_Адыгэ_хъыбархэр_1978.pdf_processed -g 1
```


### Check the result
```shell
ls -haltr ../../media/tmp_processing                                                                
```

#### output
```text
drwxr-xr-x    6 panagoa  staff   192B Aug 20 03:05 ..
drwxr-xr-x    4 panagoa  staff   128B Aug 20 17:38 .
drwxr-xr-x  140 panagoa  staff   4.4K Aug 20 17:39 Къалэмбии_Адыгэ_хъыбархэр_1978.pdf_splitted
drwxr-xr-x   71 panagoa  staff   2.2K Aug 20 17:39 Къалэмбии_Адыгэ_хъыбархэр_1978.pdf
```


## Book processing
```shell
python -m cli box-processing -d data/dag_results/data/dag_results/pdf_processing/Къалэмбии_Адыгэ_хъыбархэр_1978__orig.pdf/rslt_collected_3_from_oshamaho_new_font_0.193_4395_18400/jpgs -o data/dag_results/data/dag_results/pdf_processing/Къалэмбии_Адыгэ_хъыбархэр_1978__orig.pdf/rslt_collected_3_from_oshamaho_new_font_0.193_4395_18400/boxes
```


## OCR
```shell
make all PDF_FILE=111-shorten-a-ti-pashchie-bechmyrze
```

```shell
img2pdf ../data/pdf_processed/111-shorten-a-ti-pashchie-bechmyrze.pdf_processed/B1.4__C1.7__S1.4/*.jpg --pagesize A4 -o ../data/pdf_processed/111-shorten-a-ti-pashchie-bechmyrze.pdf_processed/B1.4__C1.7__S1.4.pdf
```

```shell
ocrmypdf --pages 1-50 -l kbd_finetuned5_0.023_908_26600 --force-ocr --clean --clean-final --deskew --unpaper-args '--layout single' C1.7__B1.4__S1.4.pdf C1.7__B1.4__S1.ocr.pdf
```

#### convert image to black and white .pnm format for unpaper

```shell
convert -density 300 -resize 2481x3507 -black-threshold 70% -white-threshold 75% image.jpg image_bw.pnm
```

#### unpaper image

```shell
unpaper --layout single --black-threshold 0.1 image_bw.pnm image_bw_unpaper.pnm
```

#### reconvert image to jpg

```shell
convert image_bw_unpaper.pnm -compress jpeg -quality 100 image_bw_unpaper.jpg
```

#### join images to pdf and apply OCR

```shell
img2pdf my-images*.jpg | ocrmypdf - myfile.pdf
```