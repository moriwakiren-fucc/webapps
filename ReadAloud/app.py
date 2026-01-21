import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Read Aloud (Browser TTS)")

st.title("📢 Read Aloud（ブラウザTTS）")

text = st.text_area("読み上げテキスト", height=200)

if st.button("読み上げ"):
    html = f"""
    <html>
    <body>
        <script>
            const text = `{text}`;
            const utterance = new SpeechSynthesisUtterance(text);

            utterance.lang = "ja-JP";
            utterance.rate = 1.0;
            utterance.pitch = 1.0;

            window.speechSynthesis.cancel();
            window.speechSynthesis.speak(utterance);
        </script>
    </body>
    </html>
    """
    components.html(html, height=0)
