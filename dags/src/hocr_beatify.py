import os

from bs4 import BeautifulSoup


def _get_color(confidence):
    confidence_color_map = {
        (0, 10): "darkred",
        (10, 20): "red",
        (20, 30): "orangered",
        (30, 40): "darkorange",
        (40, 50): "gold",
        (50, 60): "darkkhaki",
        (60, 70): "olivedrab",
        (70, 80): "green",
        (80, 90): "darkgreen",
        (90, 100): "black",
    }
    for (min_conf, max_conf), color in confidence_color_map.items():
        if min_conf <= confidence < max_conf:
            return color
    return "black"


def _conf_prettify(soup):
    words = soup.find_all("span", class_="ocrx_word")
    for word in words:
        confidence = float(word["title"].split(";")[1].split()[1])
        color = _get_color(confidence)
        word["style"] = f"color: {color};"

    return soup


def hocr_to_html(hocr_dir, output_path):
    soup = None
    for page, filename in enumerate(sorted(os.listdir(hocr_dir))):
        if filename.endswith(".hocr"):
            file_path = os.path.join(hocr_dir, filename)
            page_soup = BeautifulSoup(open(file_path, encoding="utf-8"), "html.parser")
            page_soup = _conf_prettify(page_soup)
            page_div = page_soup.find("div", class_="ocr_page")
            page_div["id"] = f"page_{page}"  # Добавить id к div
            if page == 0:
                soup = page_soup
            else:
                # add horizontal line between pages
                soup.body.append(soup.new_tag("hr"))
                soup.body.append(page_div)

    with open(output_path, "w", encoding="utf-8") as output_file:
        output_file.write(soup.prettify())


if __name__ == "__main__":
    dir_name = "Dygenshe_iles_kbd_0.229_2995_10800"
    folder_path = f"../../references/book/{dir_name}"
    output_path = os.path.join(folder_path, "output.html")

    hocr_to_html(folder_path, output_path)
