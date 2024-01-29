### распаковка языкового пакета

```bash
combine_tessdata -u rus.traineddata kbd.
```

### распаковка словарей dawg в текстовый формат

```bash
dawg2wordlist kbd.unicharset kbd.freq-dawg freq-wlist
dawg2wordlist kbd.unicharset kbd.word-dawg word-wlist
dawg2wordlist kbd.unicharset kbd.bigram-dawg bigram-wlist
```

### упаковка словарей в бинарный формат dawg

```bash
wordlist2dawg freq-wlist kbd.freq-dawg kbd.unicharset
wordlist2dawg word-wlist kbd.word-dawg kbd.unicharset
wordlist2dawg bigram-wlist kbd.bigram-dawg kbd.unicharset
```

- #todo надо добавить имена и фамилии в словарь

### упаковка языкового пакета

```bash
combine_tessdata kbd.
```

### копирование языкового пакета в каталог tesseract

```bash
cp kbd.traineddata /opt/homebrew/share/tessdata/
```

### проверка что языковой пакет установлен

```bash
tesseract --list-langs
```

### проверка что языковой пакет работает

```bash
tesseract -l kbd --oem 3 SCR-20230604-fgln.png SCR-20230604-fgln.kbd.txt ../kdb.base.config.txt
```

### проверка что через ocrmypdf работает

```bash
ocrmypdf -l kbd --force-ocr --pages 1 --sidecar dysche_zhyg.ocr.13.pdf.txt dysche_zhyg.pdf dysche_zhyg.ocr.13.pdf --tesseract-config ../kdb.base.config.txt
```

### обучение

```bash
nohup gmake training MODEL_NAME=kbd START_MODEL=rus MAX_ITERATIONS=30000 | ts '[%Y-%m-%d %H:%M:%S]' | tee plot/output.log
```

### преобразование чекпоинтов в языковой пакет

```bash
gmake traineddata MODEL_NAME=kbd
```

### создание csv файла из лога обучения

```bash
cat plot/output.log | grep "New best BCER" | \
sed -e 's/\[//' -e 's/\] At iteration /,/' -e 's|/|,|g' -e 's/, mean rms=/,/' \
    -e 's/%, delta=/,/' -e 's/%, BCER train=/,/' -e 's/%, BWER train=/,/' \
    -e 's/%, skip ratio=/,/' -e 's/%, New best BCER = /,/' -e 's/ wrote checkpoint./,/' | \
awk 'BEGIN {FS=","; print "Timestamp,Iteration,Total1,Total2,Mean RMS,Delta,BCER Train,BWER Train,Skip Ratio,New Best BCER"}
     {print $1,$2,$3,$4,$5,$6,$7,$8,$9,$10}' OFS=',' > log.csv
```

### литература

https://tesseract-ocr.repairfaq.org/allaboutdawg.html

https://github.com/WojciechMula/pyDAWG

https://dawg.readthedocs.io/en/latest/