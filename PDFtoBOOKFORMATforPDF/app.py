import io
import os
from pypdf import PdfReader, PdfWriter
import streamlit as st

st.title("PDF ページ毎→印刷用冊子形式")
def pdfforPrint(org_pdf, muki, f_name):
    if muki != "RtoL" and muki != "LtoR":
        st.error("エラー")
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
    new_name = f"{f_name}.pdf"
    st.download_button(
        label=f'\"{new_name}\"をダウンロード',
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
for j, file in enumerate(files):
    if file is not None:
        if '外国語' in file.name:
            idx = 0
        elif '国語' in file.name:
            idx = 1
        else:
            idx = 0
        option = st.selectbox(
            '向き',
            ['左→右(横書き)', '右→左(縦書き)'],
            index = idx,
            key = 'muki' + str(j)
            label_visibility="collapsed"
        )
        f_name = st.text_input('ファイル名のうち、\' .pdf \'よりも前の部分を入力',
                             value=f'{file.name[:-4]}_BookFormat',
                             key='name' + str(j))
        if option == '左→右(横書き)':
            muki = "LtoR"
        elif option == '右→左(縦書き)':
            muki = "RtoL"
        pdfforPrint(file, muki, f_name)
