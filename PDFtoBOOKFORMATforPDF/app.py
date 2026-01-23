import io
import os
from pypdf import PdfReader, PdfWriter
import streamlit as st

st.header("PDF ページ毎→印刷用冊子形式")
def pdfforPrint(org_pdf, muki="LtoR"):
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
    pdf_buffer = io.BytesIO()
    out_writer.write(pdf_buffer)
    new_name = f'{org_pdf.name[:-4]}_BookFormt.pdf'
    st.download_button(
        label=new_name,
        data=pdf_buffer,
        file_name=new_name,
        mime='application/pdf'
    )
    pdf_buffer.close()
    return f'{org_pdf.name}BookFormt'
paths = []
files = st.file_uploader("PDFをアップロード！", type="pdf", accept_multiple_files=True)
st.header('ダウンロード')
for file in files:
    if file is not None:
        pdfforPrint(file, muki="RtoL")
