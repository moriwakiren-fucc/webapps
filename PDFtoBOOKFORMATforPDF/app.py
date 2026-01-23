import io
import os
from pypdf import PdfReader, PdfWriter
import streamlit as st

st.title("PDF ページ毎→印刷用冊子形式")
def pdfforPrint(org_pdf, muki):
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
st.header('PDFアップロード')
files = st.file_uploader("", type="pdf", accept_multiple_files=True)
st.header('処理済みPDFダウンロード')
for file in files:
    if file is not None:
        if '国語' in file.name:
            idx = 1
        else:
            idx = 0
        for j, file in enumerate(files):
            option = st.selectbox(
                f'{file.name}の向きを指定: ',
                ['左→右(横書き)', '右→左(縦書き)', 'aaa'],
                index = idx,
                key = str(j)
            )
            if option == '左→右(横書き)':
                muki = "LtoR"
            elif option == '右→左(縦書き)':
                muki = "LtoR"
            else:
                st.error('aaa')
        pdfforPrint(file,muki)
