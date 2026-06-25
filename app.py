import streamlit as st
import fitz  # PyMuPDF
import io
import zipfile
from datetime import datetime  # <-- Librería para obtener la fecha del sistema

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Generador de Firmas", layout="centered")

st.title("📝 Firmador de PDFs Automático")
st.write("Sube uno o varios PDFs, confirma la fecha y descarga tus archivos listos.")

# --- OBTENER FECHA ACTUAL AUTOMÁTICAMENTE ---
# Toma la fecha del día de hoy y le da el formato DD/MM/AAAA
fecha_hoy = datetime.now().strftime("%d/%m/%Y")

# --- 1. MODIFICA LA FECHA AQUÍ (Se pre-llena con la fecha de hoy) ---
fecha_personalizada = st.text_input("Fecha a colocar:", value=fecha_hoy)

# Botón para subir múltiples archivos
archivos_subidos = st.file_uploader("Selecciona los PDFs", type="pdf", accept_multiple_files=True)

# --- 2. LÓGICA AL PRESIONAR EL BOTÓN ---
if st.button("Procesar y Firmar Documentos"):
    if not archivos_subidos:
        st.warning("⚠️ Por favor, sube al menos un PDF para empezar.")
    else:
        # Creamos un archivo ZIP en memoria para empaquetar los resultados
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for archivo in archivos_subidos:
                # Leer el PDF desde la subida web
                doc = fitz.open(stream=archivo.read(), filetype="pdf")
                firma_insertada = False
                
                for pagina in doc:
                    instancias_texto = pagina.search_for("Nombre:")
                    
                    if instancias_texto:
                        rect_ancla = instancias_texto[0]
                        x_base = rect_ancla.x0
                        y_base = rect_ancla.y0

                        # --- INSERTAR TEXTOS ---
                        offset_x_texto = x_base + 60 
                        pagina.insert_text((offset_x_texto, y_base + 10), "Xavier Wer", fontsize=11, color=(0, 0, 0))
                        pagina.insert_text((offset_x_texto, y_base + 25), "SLC TRADE", fontsize=11, color=(0, 0, 0))
                        pagina.insert_text((offset_x_texto, y_base + 40), fecha_personalizada, fontsize=11, color=(0, 0, 0))

                        # --- INSERTAR IMÁGENES ---
                        try:
                            # Coordenadas de firma y sello fijadas
                            rect_firma = fitz.Rect(x_base - 10, y_base - 80, x_base + 110, y_base - 30)
                            pagina.insert_image(rect_firma, filename="firma.png")

                            rect_sello = fitz.Rect(x_base + 160, y_base - 5, x_base + 260, y_base + 45)
                            pagina.insert_image(rect_sello, filename="sello.png")
                            
                            firma_insertada = True
                        except Exception as e:
                            st.error(f"Error con las imágenes en {archivo.name}: Asegúrate de que estén en el repositorio. Detalle: {e}")
                        
                        break 
                
                # Guardar el PDF modificado en memoria
                pdf_bytes = doc.write()
                doc.close()
                
                if firma_insertada:
                    # Añadir al ZIP
                    zip_file.writestr(f"firmado_{archivo.name}", pdf_bytes)
                else:
                    st.warning(f"No se encontró la etiqueta 'Nombre:' en: {archivo.name}")

        # --- 3. BOTÓN DE DESCARGA ---
        st.success("✅ ¡Proceso completado con éxito!")
        st.download_button(
            label="📥 Descargar todos los PDFs firmados (.zip)",
            data=zip_buffer.getvalue(),
            file_name="documentos_firmados.zip",
            mime="application/zip"
        )