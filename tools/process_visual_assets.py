# -*- coding: utf-8 -*-
"""将生图 API 返回的大图裁成 Tkinter GUI 直接使用的固定尺寸。"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parent.parent
TMP = ROOT / "tmp" / "imagegen"
PORTRAIT_RAW = TMP / "portraits_raw"
ILLUSTRATION_RAW = TMP / "illustrations_raw"
PORTRAIT_OUT = ROOT / "assets" / "portraits"
ILLUSTRATION_OUT = ROOT / "assets" / "illustrations"


def _fit(source, destination, size, centering):
    with Image.open(source) as image:
        image = ImageOps.exif_transpose(image).convert("RGB")
        image = ImageOps.fit(image, size, method=Image.Resampling.LANCZOS, centering=centering)
        image.save(destination, format="PNG", optimize=True)


def _process_folder(source_dir, destination_dir, size, centering):
    destination_dir.mkdir(parents=True, exist_ok=True)
    count = 0
    for source in sorted(source_dir.glob("*.png")):
        _fit(source, destination_dir / source.name, size, centering)
        count += 1
    return count


def _contact_sheet(files, output, thumb_size, columns):
    files = list(files)
    if not files:
        return
    label_height = 20
    rows = (len(files) + columns - 1) // columns
    sheet = Image.new(
        "RGB",
        (thumb_size[0] * columns, (thumb_size[1] + label_height) * rows),
        "#14161c",
    )
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()
    for index, path in enumerate(files):
        with Image.open(path) as image:
            image = image.convert("RGB")
            image.thumbnail(thumb_size, Image.Resampling.LANCZOS)
            x = index % columns * thumb_size[0]
            y = index // columns * (thumb_size[1] + label_height)
            sheet.paste(image, (x, y))
            draw.text((x + 4, y + thumb_size[1] + 3), path.stem, fill="#e8e2d2", font=font)
    sheet.save(output, format="PNG", optimize=True)


def main():
    portraits = _process_folder(PORTRAIT_RAW, PORTRAIT_OUT, (176, 176), (0.5, 0.43))
    illustrations = _process_folder(
        ILLUSTRATION_RAW,
        ILLUSTRATION_OUT,
        (832, 208),
        (0.5, 0.5),
    )
    _contact_sheet(sorted(PORTRAIT_OUT.glob("*.png")), TMP / "portraits-contact-sheet.png", (176, 176), 6)
    _contact_sheet(
        sorted(ILLUSTRATION_OUT.glob("*.png")),
        TMP / "illustrations-contact-sheet.png",
        (416, 104),
        2,
    )
    print(f"Processed {portraits} portraits and {illustrations} illustrations.")


if __name__ == "__main__":
    main()
