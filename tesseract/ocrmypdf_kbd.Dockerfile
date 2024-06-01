ARG OCRMYPDF_VERSION=v16.3.1

FROM jbarlow83/ocrmypdf:${OCRMYPDF_VERSION}

COPY trained_data/kbd_finetuned.traineddata /usr/share/tesseract-ocr/5/tessdata/kbd.traineddata
COPY kdb.base.config.txt /etc/ocrmypdf/kbd.config