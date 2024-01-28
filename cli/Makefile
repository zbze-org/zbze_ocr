PDF_FILE ?= Къалэмбии_Адыгэ_хъыбархэр_1978.pdf
PDF_DIR ?= ../data/pdfs
TMP_PROCESSING_DIR ?= ../data/pdf_processed

GREEN = \033[0;32m
YELLOW = \033[0;33m
NC = \033[0m

DEFAULT_STEPS := split-pdf-to-jpeg split-book-layout rotate-images smooth-images apply-image-filters check-result
STEPS := $(if $(EXCLUDE),$(filter-out $(EXCLUDE),$(DEFAULT_STEPS)),$(DEFAULT_STEPS))

help:
	@echo "${YELLOW}Доступные команды:${NC}"
	@echo "  ${YELLOW}make all${NC} - Выполнить все шаги по умолчанию"
	@echo "  ${YELLOW}make all EXCLUDE=\"step1 step2\"${NC} - Выполнить все шаги, исключая указанные (например: \"split-book-layout rotate-images\")"
	@echo "  ${YELLOW}make check-result${NC} - Проверить результат"
	@echo "  ${YELLOW}make split-pdf-to-jpeg${NC} - Разделить PDF на JPEG"
	@echo "  ${YELLOW}make split-book-layout${NC} - Разделить макет книги"
	@echo "  ${YELLOW}make rotate-images${NC} - Повернуть изображения"
	@echo "  ${YELLOW}make smooth-images${NC} - Сгладить изображения"
	@echo "  ${YELLOW}make apply-image-filters${NC} - Применить фильтры к изображениям"

all:
	@echo "${GREEN}Выполняются шаги: $(STEPS)${NC}"
	for step in $(STEPS); do \
		make $$step ; \
	done

split-pdf-to-jpeg:
	@echo "${GREEN}Выполняется разделение PDF на JPEG...${NC}"
	python split_pdf_to_jpeg.py -i $(PDF_DIR)/$(PDF_FILE) -o $(TMP_PROCESSING_DIR)/$(PDF_FILE)

split-book-layout:
	@echo "${GREEN}Выполняется разделение макета книги...${NC}"
	python split_book_layout.py -d $(TMP_PROCESSING_DIR)/$(PDF_FILE) -o $(TMP_PROCESSING_DIR)/$(PDF_FILE)_splitted

rotate-images:
	@echo "${GREEN}Поворот изображений...${NC}"
	python rotate_img.py -d $(TMP_PROCESSING_DIR)/$(PDF_FILE)_splitted -o $(TMP_PROCESSING_DIR)/$(PDF_FILE)_rotated

smooth-images:
	@echo "${GREEN}Сглаживание изображений...${NC}"
	python smooth_img.py -d $(TMP_PROCESSING_DIR)/$(PDF_FILE)_rotated -o $(TMP_PROCESSING_DIR)/$(PDF_FILE)_smoothened

apply-image-filters:
	@echo "${GREEN}Применение фильтров к изображениям...${NC}"
	python apply_img_filters.py -d $(TMP_PROCESSING_DIR)/$(PDF_FILE)_smoothened -o $(TMP_PROCESSING_DIR)/$(PDF_FILE)_processed -g 1 && \
	cp -r $(TMP_PROCESSING_DIR)/$(PDF_FILE)_rotated/ $(TMP_PROCESSING_DIR)/$(PDF_FILE)_processed/orig

check-result:
	@echo "${GREEN}Проверка результата...${NC}"
	ls -haltr $(TMP_PROCESSING_DIR)
