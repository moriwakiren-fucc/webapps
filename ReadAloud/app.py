import os
from PyPDF2 import PdfReader, PdfWriter


def pdfforPrint(org_pdf: str, muki="LtoR"):
    assert muki == "RtoL" or muki == "LtoR", f"\n変数mukiに\"{muki}\"はありえないよ\n\"LtoR\"か\"RtoL\"のどちらかしてね"
    # 元PDFを読み込み
    reader = PdfReader(org_pdf)
    pgs = len(reader.pages)

    # 4の倍数になるように追加する白紙枚数
    whs = 4 - pgs % 4

    # 一時的に白紙追加後のPDFを作成
    writer_wh = PdfWriter()
    for page in reader.pages:
        writer_wh.add_page(page)

    # 白紙ページを追加
    if pgs > 0:
        blank_page = writer_wh.add_blank_page(
            width=reader.pages[0].mediabox.width,
            height=reader.pages[0].mediabox.height
        )
        # add_blank_page で1枚追加されるため調整
        for _ in range(whs - 1):
            writer_wh.add_blank_page(
                width=reader.pages[0].mediabox.width,
                height=reader.pages[0].mediabox.height
            )

    with open(str(pgs)+".pdf", "wb") as f:
        writer_wh.write(f)
    wh_pgs = len(writer_wh.pages)
    npgs = int(wh_pgs / 2)

    # 並び替え用PDF
    out_writer = PdfWriter()

    if muki == "RtoL":
        # 指定ロジックに基づいてページを追加
        for i in range(0, npgs, 2):
            out_writer.add_page(writer_wh.pages[i])
            out_writer.add_page(writer_wh.pages[wh_pgs - i - 1])
            out_writer.add_page(writer_wh.pages[wh_pgs - i - 2])
            out_writer.add_page(writer_wh.pages[i + 1])
    elif muki == "LtoR":
        for i in range(0, npgs, 2):
            out_writer.add_page(writer_wh.pages[wh_pgs - i - 1])
            out_writer.add_page(writer_wh.pages[i])
            out_writer.add_page(writer_wh.pages[i + 1])
            out_writer.add_page(writer_wh.pages[wh_pgs - i - 2])

    # 保存先フォルダ（org_pdfと同じ場所）
    base_dir = os.path.dirname(org_pdf)
    out_dir = os.path.join(base_dir, "forPrint")
    os.makedirs(out_dir, exist_ok=True)

    # 出力ファイル名
    base_name = os.path.splitext(os.path.basename(org_pdf))[0]
    out_pdf = os.path.join(out_dir, f"{base_name}_forPrint.pdf")

    # 保存
    with open(out_pdf, "wb") as f:
        out_writer.write(f)

    return out_pdf

paths = []
"""
for n in range(1, 9):
    path = os.path.join("drive", "MyDrive", "共テ模試過去問", str(n) + ".pdf")
    print(path)
    a = pdfforPrint(path)
    print(a)
"""
path = os.path.join("drive", "MyDrive", "共テ模試過去問", str(3) + ".pdf")
print(path)
a = pdfforPrint(path, muki="RtoL")
print(a)
