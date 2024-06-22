PDF_FILE ?= Къалэмбии_Адыгэ_хъыбархэр_1978.pdf
PDF_DIR ?= ../data/pdfs
TMP_PROCESSING_DIR ?= ../data/pdf_processed/$(PDF_FILE)

PDF_PATH := $(PDF_DIR)/$(PDF_FILE)
JPEG_DIR := $(TMP_PROCESSING_DIR)/00_jpeg
LAYOUT_DIR := $(TMP_PROCESSING_DIR)/01_layout_splitted
UNPAPER_DIR := $(TMP_PROCESSING_DIR)/02_unpapered
ROTATED_DIR := $(TMP_PROCESSING_DIR)/03_rotated
FILTERED_DIR := $(TMP_PROCESSING_DIR)/04_filtered
STANDARDIZED_DIR := $(TMP_PROCESSING_DIR)/05_standartized

GREEN = \033[0;32m
YELLOW = \033[0;33m
NC = \033[0m

DEFAULT_STEPS := check-input \
	split-pdf-to-jpeg \
	split-book-layout \
	unpaper-images \
	rotate-images \
	apply-image-filters \
	standartize-images \
	join-images-to-pdf \
	copy-original-pdf \
	clean-tmp-dir \
	check-result

STEPS := $(if $(EXCLUDE),$(filter-out $(EXCLUDE),$(DEFAULT_STEPS)),$(DEFAULT_STEPS))

help:
	@echo "${YELLOW}Доступные команды:${NC}"
	@echo "  ${YELLOW}make all${NC} - Выполнить все шаги по умолчанию"
	@echo "  ${YELLOW}make all EXCLUDE=\"step1 step2\"${NC} - Выполнить все шаги, исключая указанные (например: \"split-book-layout rotate-images\")"
	@echo "  ${YELLOW}make check-result${NC} - Проверить результат"
	@echo "  ${YELLOW}make split-pdf-to-jpeg${NC} - Разделить PDF на JPEG"
	@echo "  ${YELLOW}make split-book-layout${NC} - Разделить макет книги"
	@echo "  ${YELLOW}make unpaper-images${NC} - Постобработка скана"
	@echo "  ${YELLOW}make rotate-images${NC} - Повернуть изображения"
	@echo "  ${YELLOW}make apply-image-filters${NC} - Применить фильтры к изображениям"
	@echo "  ${YELLOW}make standartize-images${NC} - Стандартизировать изображения"
	@echo "  ${YELLOW}make join-images-to-pdf${NC} - Склеить изображения в PDF"
	@echo "  ${YELLOW}make copy-original-pdf${NC} - Скопировать оригинальный PDF"
	@echo "  ${YELLOW}make copy-original-images${NC} - Скопировать оригинальные изображения"
	@echo "  ${YELLOW}make clean-tmp-dir${NC} - Очистить временную директорию"

all:
	@echo "${GREEN}Выполняются шаги: $(STEPS)${NC}"
	for step in $(STEPS); do \
		make $$step ; \
	done

check-input:
	@echo "${GREEN}Проверка входных данных...${NC}"


split-pdf-to-jpeg:
	@echo "${GREEN}Разделение PDF на JPEG...${NC}"
	python split_pdf_to_jpeg.py -i $(PDF_PATH) -o $(JPEG_DIR)

split-book-layout:
	@echo "${GREEN}Разделение макета книги...${NC}"
	python split_book_layout.py -d $(JPEG_DIR) -o $(LAYOUT_DIR)

unpaper-images:
	@echo "${GREEN}Постобработка скана...${NC}"
	python unpaper_img.py -d $(LAYOUT_DIR) -o $(UNPAPER_DIR)

rotate-images:
	@echo "${GREEN}Поворот изображений...${NC}"
	python rotate_img.py -d $(UNPAPER_DIR) -o $(ROTATED_DIR)

# smooth-images:
# 	@echo "${GREEN}Сглаживание изображений...${NC}"
# 	python smooth_img.py -d $(TMP_PROCESSING_DIR)/$(PDF_FILE)_rotated -o $(TMP_PROCESSING_DIR)/$(PDF_FILE)_smoothened

apply-image-filters:
	@echo "${GREEN}Применение фильтров к изображениям...${NC}"
	python apply_img_filters.py -d $(ROTATED_DIR) -o $(FILTERED_DIR) -g 0

standartize-images:
	@echo "${GREEN}Стандартизация изображений...${NC}"
	python standartize_img.py -d $(FILTERED_DIR) -o $(STANDARDIZED_DIR)

join-images-to-pdf:
	@echo "${GREEN}Склейка изображений в PDF...${NC}"
	python join_jpeg_to_pdf.py -d $(STANDARDIZED_DIR) -o $(TMP_PROCESSING_DIR)/processed_$(PDF_FILE)

copy-original-pdf:
	@echo "${GREEN}Копирование оригинального PDF...${NC}"
	cp $(PDF_PATH) $(TMP_PROCESSING_DIR)/original_$(PDF_FILE)

clean-tmp-dir:
	@echo "${GREEN}Очистка временной директории...${NC}"
	@if [ -f "$(TMP_PROCESSING_DIR)/processed_$(PDF_FILE)" ]; then \
		echo "${YELLOW}Обнаружен обработанный PDF. Удаление временных файлов...${NC}"; \
		rm -rf $(JPEG_DIR) $(LAYOUT_DIR) $(UNPAPER_DIR) $(ROTATED_DIR) $(FILTERED_DIR) $(STANDARDIZED_DIR); \
		echo "${GREEN}Временные директории очищены.${NC}"; \
	else \
		echo "${YELLOW}Обработанный PDF не найден. Что-то пошло не так...${NC}"; \
	fi


check-result:
	@echo "${GREEN}Проверка результата...${NC}"
	ls -haltr $(TMP_PROCESSING_DIR)
