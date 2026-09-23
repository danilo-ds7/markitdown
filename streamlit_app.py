import io
import os
import tempfile
import zipfile

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


def nombre_md(nombre, usados):
    base = os.path.splitext(nombre)[0] or "documento"
    candidato, i = f"{base}.md", 2
    while candidato in usados:
        candidato, i = f"{base} ({i}).md", i + 1
    usados.add(candidato)
    return candidato


st.set_page_config(page_title="MarkItDown", page_icon="📄", layout="wide")
st.title("⬡ MarkItDown")
st.caption("Convierte documentos a Markdown: PDF · DOCX · XLSX · PPTX · HTML · CSV · JSON · XML · TXT · ZIP · EPUB")

archivos = st.file_uploader(
    "📂 Subir archivos (puedes seleccionar varios a la vez)",
    type=EXTENSIONES,
    accept_multiple_files=True,
)

if not archivos:
    st.info("👆 Sube uno o varios archivos para comenzar.")
    st.stop()

# ── Conversión de todos los archivos ──────────────────────────────────────────
resultados, errores, usados = [], [], set()
barra = st.progress(0.0, text="⏳ Convirtiendo…")
for i, archivo in enumerate(archivos, start=1):
    contenido = archivo.getvalue()
    try:
        texto = convertir(archivo.name, contenido)
        resultados.append({
            "origen": archivo.name,
            "md": nombre_md(archivo.name, usados),
            "texto": texto,
            "tamano": len(contenido),
        })
    except Exception as e:
        errores.append((archivo.name, str(e)))
    barra.progress(i / len(archivos), text=f"⏳ Convirtiendo {i}/{len(archivos)}…")
barra.empty()

for nombre, err in errores:
    st.error(f"❌ {nombre}: {err}")

if not resultados:
    st.stop()

st.success(f"✅ {len(resultados)} de {len(archivos)} archivos convertidos")

# ── Descarga de todo en ZIP ───────────────────────────────────────────────────
buffer = io.BytesIO()
with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
    for r in resultados:
        zf.writestr(r["md"], r["texto"])

st.download_button(
    f"📦 Descargar todos ({len(resultados)}) en ZIP",
    data=buffer.getvalue(),
    file_name="markdown_convertidos.zip",
    mime="application/zip",
    type="primary",
)

st.dataframe(
    [
        {
            "Archivo": r["origen"],
            "Markdown": r["md"],
            "Tamaño": fmt_size(r["tamano"]),
            "Líneas": len(r["texto"].splitlines()),
            "Caracteres": len(r["texto"]),
        }
        for r in resultados
    ],
    width="stretch",
    hide_index=True,
)

# ── Vista previa individual ───────────────────────────────────────────────────
st.subheader("👁 Vista previa")
elegido = st.selectbox(
    "Archivo", resultados, format_func=lambda r: r["origen"], label_visibility="collapsed"
)

st.download_button(
    f"💾 Descargar {elegido['md']}",
    data=elegido["texto"].encode("utf-8"),
    file_name=elegido["md"],
    mime="text/markdown",
)

tab_raw, tab_render = st.tabs(["📄 Raw MD", "✨ Rendered"])
with tab_raw:
    st.code(elegido["texto"], language="markdown")
with tab_render:
    st.markdown(elegido["texto"])
