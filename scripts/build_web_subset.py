#!/usr/bin/env python3
"""生成网页用 WOFF2 子集。

读取 fonts/Nuokai-Regular.ttf，按 ASCII + GB2312 一级字 + 示例用字
裁出网页字体，输出 fonts/Nuokai-web.woff2。

用法：
    python3 -m pip install fonttools brotli
    python3 scripts/build_web_subset.py
"""

from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "fonts" / "Nuokai-Regular.ttf"
DST = ROOT / "fonts" / "Nuokai-web.woff2"

# 示例用字：站内页面、README 与样张里出现的句子，避免正文回退。
SAMPLE_TEXT = (
    "糯楷是一套面向日常排版的开源中文手写楷体，"
    "从霞鹜文楷改造而来，覆盖两万九千四百零四个汉字。"
    "起笔顿挫，收笔出锋，中宫收紧百分之三。"
    "适合正文、注释、书摘、菜单、包装文案与轻量品牌字。"
    "春日迟迟，卉木萋萋。仓庚喈喈，采蘩祁祁。"
    "小池残暑退，高树早凉归。"
    "落霞与孤鹜齐飞，秋水共长天一色。"
    "糯米团子般圆润，读来安静温和。"
    "こんにちは、さくら。ひらがなとカタカナ。"
    "おはようございます。ありがとう。"
    "안녕하세요. 한국어 테스트입니다."
    "반갑습니다. 오늘도 좋은 하루 되세요."
)


def gb2312_level1() -> list[str]:
    """GB2312 一级汉字：区 16 至 55，码位 0xB0A1 至 0xD7FE。"""
    chars: list[str] = []
    for hi in range(0xB0, 0xD8):
        for lo in range(0xA1, 0xFF):
            try:
                chars.append(bytes((hi, lo)).decode("gb2312"))
            except UnicodeDecodeError:
                continue
    return chars


def build_charset() -> list[str]:
    chars: set[str] = set()

    # ASCII 可打印字符与常用空白。
    chars.update(chr(c) for c in range(0x20, 0x7F))
    chars.update("\u3000\u00a0\n\r\t")

    # GB2312 一级汉字，同时带出对应全角标点。
    chars.update(gb2312_level1())

    # 日文平假名与片假名。
    chars.update(chr(cp) for cp in range(0x3040, 0x3100))

    # 韩文 KS X 1001 常用音节与兼容字母。
    chars.update(chr(cp) for cp in range(0xAC00, 0xD7A4))
    chars.update(chr(cp) for cp in range(0x3131, 0x318F))

    # 中文标点、全角符号与常见 CJK 符号。
    chars.update("，。、；：？！“”‘’（）《》〈〉【】〔〕…—·～￥％＋－×÷＝")
    chars.update("“”‘’·")

    # 全部数字与拉丁字母已在 ASCII 中，这里补全角形式。
    chars.update("０１２３４５６７８９ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ")

    chars.update(SAMPLE_TEXT)

    return sorted(chars)


def main() -> None:
    if not SRC.exists():
        raise SystemExit(f"找不到源字体：{SRC}")

    charset = build_charset()
    text = "".join(charset)

    options = subset.Options()
    options.flavor = "woff2"
    options.with_zopfli = False
    options.layout_features = ["*"]
    options.name_IDs = ["*"]
    options.name_legacy = True
    options.name_languages = ["*"]
    options.notdef_outline = True
    options.recalc_bounds = True
    options.drop_tables = []
    options.passthrough_tables = False

    font = TTFont(SRC)
    sub = subset.Subsetter(options=options)
    sub.populate(text=text)
    sub.subset(font)
    font.flavor = "woff2"
    font.save(DST)

    size = DST.stat().st_size
    print(f"字符数：{len(charset)}")
    print(f"输出：{DST}")
    print(f"大小：{size:,} 字节（{size / 1024:.0f} KiB）")


if __name__ == "__main__":
    main()
