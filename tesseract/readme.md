## OCRmyPDF

[Produce PDF and text file containing OCR text](https://ocrmypdf.readthedocs.io/en/latest/cookbook.html#produce-pdf-and-text-file-containing-ocr-text)

```shell
ocrmypdf --sidecar output.txt input.pdf output.pdf
```

[Control of unpaper](https://ocrmypdf.readthedocs.io/en/latest/advanced.html#control-of-unpaper)

In this example, we tell unpaper to expect two pages of text on a sheet (image), such as occurs when two facing pages of a book are scanned. unpaper uses this information to deskew each independently and clean up the margins of both.

```shell
ocrmypdf --clean --clean-final --unpaper-args '--layout double' input.pdf output.pdf
ocrmypdf --clean --clean-final --unpaper-args '--layout double --no-noisefilter' input.pdf output.pdf
```

### Install ocrmypdf
- [Installing OCRmyPDF](https://ocrmypdf.readthedocs.io/en/latest/installation.html#installing-ocrmypdf)
- [Docker image](https://ocrmypdf.readthedocs.io/en/latest/docker.html)
 
### build ocrmypdf with KBD language
```shell
sudo docker build -t ocrmypdf_kbd -f ocrmypdf_kbd.Dockerfile .
```

### run ocrmypdf in docker
```shell
docker run --rm  -i --user "$(id -u):$(id -g)" --workdir /data -v "$PWD:/data" ocrmypdf_kbd
```

### create a alias for ocrmypdf
```shell
alias ocrmypdf_kbd='docker run --rm  -i --user "$(id -u):$(id -g)" --workdir /data -v "$PWD:/data" ocrmypdf_kbd'
```

### run via alias

#### single layout
```shell
ocrmypdf_kbd -l kbd --force-ocr --clean --deskew --unpaper-args '--layout single' input.pdf output.pdf
```

#### double layout
```shell
ocrmypdf_kbd -l kbd --force-ocr --clean --deskew --unpaper-args '--layout double' input.pdf output.pdf
```

#### with custom tesseract config
```shell
ocrmypdf_kbd -l kbd --force-ocr --clean --deskew --unpaper-args '--layout double' --tesseract-config /etc/ocrmypdf/kbd.config --sidecar output.txt input.pdf output.pdf 
```

***see more options***:
- [ocrmypdf Basic examples](https://ocrmypdf.readthedocs.io/en/latest/cookbook.html)
- [ocrmypdf Advanced features](https://ocrmypdf.readthedocs.io/en/latest/advanced.html)
- [unpaper options](https://github.com/Flameeyes/unpaper/blob/main/doc/image-processing.md)