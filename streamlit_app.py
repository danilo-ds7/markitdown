import os
import tempfile

import streamlit as st
from markitdown import MarkItDown

EXTENSIONES = [
    "pdf", "docx", "xlsx", "xls", "pptx", "html", "htm", "csv",
    "json", "xml", "txt", "md", "zip", "epub", "msg",
]


@st.cache_resource
def get_converter():
    return MarkItDown()


def fmt_size(b):
    for u in ("B", "KB", "MB", "GB"):
        if b < 1024:
            return f"{b:.1f} {u}"
        b /= 1024
    return f"{b:.1f} TB"


@st.cache_data(show_spinner=False)
def convertir(nombre, contenido):
    ext = os.path.splitext(nombre)[1]
    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
        tmp.write(contenido)
        ruta = tmp.name
    try:
        return get_converter().convert(ruta).text_content
    finally:
        os.remove(ruta)


st.set_page_config(page_title="MarkItDown", page_icon="📄", layout="wide")
st.title("⬡ MarkItDown")
st.caption("Convierte documentos a Markdown: PDF · DOCX · XLSX · PPTX · HTML · CSV · JSON · XML · TXT · ZIP · EPUB")

archivo = st.file_uploader("📂 Subir archivo", type=EXTENSIONES)

if archivo is None:
    st.info("👆 Sube un archivo para comenzar.")
    st.stop()

contenido = archivo.getvalue()
try:
    with st.spinner("⏳ Convirtiendo…"):
        texto = convertir(archivo.name, contenido)
except Exception as e:
    st.error(f"❌ Error al convertir {archivo.name}: {e}")
    st.stop()

base = os.path.splitext(archivo.name)[0] or "documento"

c1, c2, c3, c4 = st.columns(4)
c1.metric("Archivo", archivo.name)
c2.metric("Tamaño", fmt_size(len(contenido)))
c3.metric("Líneas", f"{len(texto.splitlines()):,}")
c4.metric("Caracteres", f"{len(texto):,}")

st.download_button(
    "💾 Descargar .md",
    data=texto.encode("utf-8"),
    file_name=f"{base}.md",
    mime="text/markdown",
    type="primary",
)

tab_raw, tab_render = st.tabs(["📄 Raw MD", "✨ Rendered"])
with tab_raw:
    st.code(texto, language="markdown")
with tab_render:
    st.markdown(texto)
