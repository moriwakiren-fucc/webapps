import time
import io
import os
from pypdf import PdfReader, PdfWriter
import streamlit as st

st.title("PDF ページ毎→印刷用冊子形式")
def pdfforPrint(org_pdf, muki, f_name, hyoushi=False, ura=False):
    if muki != "RtoL" and muki != "LtoR":
        st.error("エラー")
    # 元PDFを読み込み
    reader = PdfReader(org_pdf)
    pgs = len(reader.pages)

    # 4の倍数になるように追加する白紙枚数
    whs = 4 - pgs // 4
    if hyoushi:
        whs = whs - 1
    if whs == 4:
        whs = 0

    # 一時的に白紙追加後のPDFを作成
    writer_wh = PdfWriter()
    for page in reader.pages:
        writer_wh.add_page(page)

    # 白紙ページを追加
    if hyoushi:
        blank_page = writer_wh.insert_blank_page(
            width=reader.pages[0].mediabox.width,
            height=reader.pages[0].mediabox.height,
            index = 1
        )
        if ura and whs <= 0:
            whs = whs + 4
    if whs > 0:
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
    return pdf_buffer, new_name
    # pdf_buffer.close()
paths = []
st.header('PDFアップロード')
files = st.file_uploader("", type="pdf", accept_multiple_files=True)
st.header('処理済みPDFダウンロード')
for j, file in enumerate(files):
    
    if file is not None:
        st.subheader(file.name)
        if '外国語' in file.name:
            idx = 0
        elif '国語' in file.name:
            idx = 1
        else:
            idx = 0
        f_name = st.text_input('ファイル名のうち、\' .pdf \'よりも前の部分を入力',
                             value=f'{file.name[:-4]}_BookFormat',
                             key = 'name' + str(j))
        option = st.radio(
            '向きを指定',
            ('左→右(横書き)', '右→左(縦書き)'),
            index = idx,
            key = 'muki' + str(j)
        )
        hyoushi = st.checkbox('表紙を追加',
                              key = 'hyoushi' + str(j))
        ura = st.checkbox('最終ページを必ず白紙にする',
                          key = 'ura' + str(j))
        text=""
        if option == '左→右(横書き)':
            muki = "LtoR"
        elif option == '右→左(縦書き)':
            muki = "RtoL"
        if hyoushi and ura:
            text = "表紙が追加され、最終ページが白紙になりました。"
        elif hyoushi:
            text = "表紙が追加されました。"
        elif ura:
            text = "最終ページが白紙になりました。"
        else:
            text = "PDF処理が完了しました。"
        container = st.container()
        container.write('')
        l = []
        with st.status("処理中", expanded=False) as status:
            l = []
            time.sleep(3)
            l = pdfforPrint(file, muki, f_name, hyoushi, ura)
            time.sleep(0.2)
            status.update(label="処理が完了しました", state="complete")
        with container:
            if l:
                st.download_button(
                    label='ダウンロード',
                    data=l[0],
                    file_name=l[1],
                    mime='application/pdf',
                    key = 'download' + str(j)
                )
    st.divider()
