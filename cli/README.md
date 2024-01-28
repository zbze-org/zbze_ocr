
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
