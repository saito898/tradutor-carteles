import streamlit as st
import os
import time
import glob
import cv2
import numpy as np
import pytesseract
from PIL import Image
from gtts import gTTS
from googletrans import Translator


# --------------------------------------------------
# CONFIGURACIÓN
# --------------------------------------------------

st.set_page_config(
    page_title="Traductor de Carteles",
    page_icon="🌎",
    layout="wide"
)


# --------------------------------------------------
# ESTILO DE LA PÁGINA
# --------------------------------------------------

st.markdown("""
<style>

    /* Fondo general */
    .stApp {
        background-color: white;
    }

    /* Líneas onduladas de fondo */
    .stApp::before {
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: 0;

        background:
            radial-gradient(
                ellipse at 10% 20%,
                transparent 0%,
                transparent 40%,
                rgba(11, 31, 58, 0.12) 40.5%,
                transparent 41%
            ),
            radial-gradient(
                ellipse at 90% 80%,
                transparent 0%,
                transparent 38%,
                rgba(52, 152, 219, 0.15) 38.5%,
                transparent 39%
            ),
            radial-gradient(
                ellipse at 80% 20%,
                transparent 0%,
                transparent 42%,
                rgba(231, 76, 60, 0.10) 42.5%,
                transparent 43%
            ),
            radial-gradient(
                ellipse at 20% 85%,
                transparent 0%,
                transparent 40%,
                rgba(46, 204, 113, 0.12) 40.5%,
                transparent 41%
            );
    }

    /* Mantener el contenido por encima de las ondas */
    .main .block-container {
        position: relative;
        z-index: 1;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #0B1F3A;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label {
        color: white;
    }

</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# CARPETA PARA AUDIOS
# --------------------------------------------------

os.makedirs("temp", exist_ok=True)


# --------------------------------------------------
# TRADUCCIÓN + TEXTO A VOZ
# --------------------------------------------------

def text_to_speech(input_language, output_language, text, tld):

    translator = Translator()

    translation = translator.translate(
        text,
        src=input_language,
        dest=output_language
    )

    trans_text = translation.text

    tts = gTTS(
        trans_text,
        lang=output_language,
        tld=tld,
        slow=False
    )

    my_file_name = text[:20].strip()

    if not my_file_name:
        my_file_name = "audio"

    my_file_name = "".join(
        c for c in my_file_name
        if c.isalnum() or c in (" ", "_", "-")
    )

    my_file_name = my_file_name.replace(" ", "_")

    file_path = f"temp/{my_file_name}.mp3"

    tts.save(file_path)

    return my_file_name, trans_text


# --------------------------------------------------
# ELIMINAR AUDIOS ANTIGUOS
# --------------------------------------------------

def remove_files(n):

    mp3_files = glob.glob("temp/*.mp3")

    if len(mp3_files) != 0:

        now = time.time()
        n_days = n * 86400

        for f in mp3_files:

            if os.stat(f).st_mtime < now - n_days:

                os.remove(f)

                print("Deleted:", f)


remove_files(7)


# --------------------------------------------------
# IMAGEN PRINCIPAL
# --------------------------------------------------

try:

    image = Image.open("chibipaises.jfif")

    st.image(
        image,
        width=1920
    )

except FileNotFoundError:

    st.warning(
        "No se encontró la imagen chibipaises.jfif."
    )


# --------------------------------------------------
# TÍTULO
# --------------------------------------------------

st.title(
    "Bienvenido al traductor de carteles para extranjeros"
)

st.subheader(
    "En este lugar usted podrá traducir imágenes "
    "desde su galería o cámara, para facilitar sus viajes."
)


# --------------------------------------------------
# SIDEBAR - PROCESAMIENTO DE CÁMARA
# --------------------------------------------------

with st.sidebar:

    st.subheader("Procesamiento para Cámara")

    filtro = st.radio(
        "Filtro para imagen con cámara",
        ("Sí", "No")
    )


# --------------------------------------------------
# CÁMARA
# --------------------------------------------------

cam_ = st.checkbox("Usar Cámara")

if cam_:

    img_file_buffer = st.camera_input(
        "Toma una Foto"
    )

else:

    img_file_buffer = None


# --------------------------------------------------
# VARIABLE PARA EL TEXTO DETECTADO
# --------------------------------------------------

text = ""


# --------------------------------------------------
# CARGAR IMAGEN DESDE ARCHIVO
# --------------------------------------------------

bg_image = st.file_uploader(
    "Cargar Imagen:",
    type=["png", "jpg", "jpeg"]
)


if bg_image is not None:

    st.image(
        bg_image,
        caption="Imagen cargada.",
        use_container_width=True
    )

    bytes_data = bg_image.getvalue()

    img_cv = cv2.imdecode(
        np.frombuffer(bytes_data, np.uint8),
        cv2.IMREAD_COLOR
    )

    if img_cv is not None:

        img_rgb = cv2.cvtColor(
            img_cv,
            cv2.COLOR_BGR2RGB
        )

        try:

            text = pytesseract.image_to_string(
                img_rgb
            )

            st.write("### Texto detectado:")
            st.write(text)

        except Exception as e:

            st.error(
                f"Error al leer el texto de la imagen: {e}"
            )

    else:

        st.error(
            "No se pudo leer la imagen."
        )


# --------------------------------------------------
# CÁMARA - OCR
# --------------------------------------------------

if img_file_buffer is not None:

    bytes_data = img_file_buffer.getvalue()

    cv2_img = cv2.imdecode(
        np.frombuffer(bytes_data, np.uint8),
        cv2.IMREAD_COLOR
    )

    if cv2_img is not None:

        if filtro == "Sí":

            cv2_img = cv2.bitwise_not(
                cv2_img
            )

        img_rgb = cv2.cvtColor(
            cv2_img,
            cv2.COLOR_BGR2RGB
        )

        try:

            text = pytesseract.image_to_string(
                img_rgb
            )

            st.write("### Texto detectado:")
            st.write(text)

        except Exception as e:

            st.error(
                f"Error al leer el texto de la cámara: {e}"
            )

    else:

        st.error(
            "No se pudo leer la imagen de la cámara."
        )


# --------------------------------------------------
# SIDEBAR - PARÁMETROS DE TRADUCCIÓN
# --------------------------------------------------

with st.sidebar:

    st.subheader("Parámetros de traducción")

    translator = Translator()


    # --------------------------------------------------
    # IDIOMA DE ENTRADA
    # --------------------------------------------------

    in_lang = st.selectbox(
        "Seleccione el lenguaje de entrada de la imagen",
        (
            "Ingles",
            "Español",
            "Bengali",
            "koreano",
            "Mandarin",
            "Japones",
            "Frances",
            "Italiano"
        )
    )

    input_languages = {

        "Ingles": "en",
        "Español": "es",
        "Bengali": "bn",
        "koreano": "ko",
        "Mandarin": "zh-cn",
        "Japones": "ja",
        "Frances": "fr",
        "Italiano": "it"

    }

    input_language = input_languages[in_lang]


    # --------------------------------------------------
    # IDIOMA DE SALIDA
    # --------------------------------------------------

    out_lang = st.selectbox(
        "Seleccione el idioma de salida",
        (
            "Ingles",
            "Español",
            "Bengali",
            "koreano",
            "Mandarin",
            "Japones",
            "Frances",
            "Italiano"
        )
    )

    output_languages = {

        "Ingles": "en",
        "Español": "es",
        "Bengali": "bn",
        "koreano": "ko",
        "Mandarin": "zh-cn",
        "Japones": "ja",
        "Frances": "fr",
        "Italiano": "it"

    }

    output_language = output_languages[out_lang]


    # --------------------------------------------------
    # ACENTO
    # --------------------------------------------------

    english_accent = st.selectbox(
        "Seleccione el acento",
        (
            "Default",
            "India",
            "United Kingdom",
            "United States",
            "Canada",
            "Australia",
            "Ireland",
            "South Africa"
        )
    )

    accents = {

        "Default": "com",
        "India": "co.in",
        "United Kingdom": "co.uk",
        "United States": "com",
        "Canada": "ca",
        "Australia": "com.au",
        "Ireland": "ie",
        "South Africa": "co.za"

    }

    tld = accents[english_accent]


    # --------------------------------------------------
    # MOSTRAR TEXTO
    # --------------------------------------------------

    display_output_text = st.checkbox(
        "Mostrar texto"
    )


    # --------------------------------------------------
    # BOTÓN DE TRADUCIR
    # --------------------------------------------------

    convert_button = st.button(
        "Convertir"
    )


# --------------------------------------------------
# TRADUCIR
# --------------------------------------------------

if convert_button:

    if not text.strip():

        st.warning(
            "No se detectó ningún texto. "
            "Primero carga una imagen o toma una foto."
        )

    else:

        try:

            result, output_text = text_to_speech(
                input_language,
                output_language,
                text,
                tld
            )

            audio_file = open(
                f"temp/{result}.mp3",
                "rb"
            )

            audio_bytes = audio_file.read()

            st.markdown("## 🔊 Tu audio:")

            st.audio(
                audio_bytes,
                format="audio/mp3",
                start_time=0
            )

            audio_file.close()


            if display_output_text:

                st.markdown(
                    "## Texto de salida:"
                )

                st.write(
                    output_text
                )


        except Exception as e:

            st.error(
                f"Ocurrió un error durante la traducción: {e}"
            )
