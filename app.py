import streamlit as st
import pandas as pd
import datetime
import google.generativeai as genai

# Configuración principal de la página web
st.set_page_config(page_title="Plataforma de Control de Gastos", layout="wide")

# Inicializar la base de datos persistente en sesión
if "gastos_db" not in st.session_state:
    st.session_state.gastos_db = pd.DataFrame(columns=[
        "N°", "N° PARTIDA", "FECHA E.", "N° SERIE", "N° CORRELATIVO", 
        "RUC", "RAZON SOCIAL", "CANT.", "UNID", "DESCRIPCIÓN", 
        "PRECIO UNIT", "V.V.", "IGV", "TOTAL"
    ])

st.title("🏗️ Plataforma Integrada de Control de Gastos e Inteligencia Artificial")

tabs = st.tabs(["📝 Registro de Gastos (Victoria)", "📊 Panel de Análisis e IA"])

# ---------------------------------------------------------
# PESTAÑA 1: MÓDULO DE REGISTRO (VICTORIA)
# ---------------------------------------------------------
with tabs[0]:
    st.subheader("Carga de Comprobantes - Administración")
    
    with st.form("form_registro", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            partida = st.text_input("N° PARTIDA", placeholder="Ej. 01.01.02")
            fecha_e = st.date_input("FECHA E.", datetime.date.today())
            serie = st.text_input("N° SERIE", placeholder="Ej. F001")
            correlativo = st.text_input("N° CORRELATIVO", placeholder="Ej. 0001234")
            
        with col2:
            ruc = st.text_input("RUC", max_chars=11, placeholder="11 dígitos")
            razon_social = st.text_input("RAZON SOCIAL")
            cantidad = st.number_input("CANT.", min_value=0.0, step=1.0, value=1.0)
            unid = st.selectbox("UNID", ["GLB", "M3", "KG", "UND", "M2", "ML", "VIAJE", "BOLSA", "HORA"])
            
        with col3:
            descripcion = st.text_area("DESCRIPCIÓN", placeholder="Detalle del bien o servicio...")
            precio_unit = st.number_input("PRECIO UNIT (sin IGV)", min_value=0.0, step=0.10)
            
            # CÁLCULOS AUTOMÁTICOS EN TIEMPO REAL
            vv_calc = round(cantidad * precio_unit, 2)
            igv_calc = round(vv_calc * 0.18, 2)
            total_calc = round(vv_calc + igv_calc, 2)
            
            st.markdown("---")
            st.markdown(f"**V.V. (Valor Venta Subtotal):** S/ {vv_calc:,.2f}")
            st.markdown(f"**IGV (18%):** S/ {igv_calc:,.2f}")
            st.markdown(f"**TOTAL:** S/ {total_calc:,.2f}")

        submit = st.form_submit_button("💾 Guardar Registro de Gasto")

    if submit:
        num_reg = len(st.session_state.gastos_db) + 1
        nuevo_registro = {
            "N°": num_reg,
            "N° PARTIDA": partida,
            "FECHA E.": str(fecha_e),
            "N° SERIE": serie,
            "N° CORRELATIVO": correlativo,
            "RUC": ruc,
            "RAZON SOCIAL": razon_social,
            "CANT.": cantidad,
            "UNID": unid,
            "DESCRIPCIÓN": descripcion,
            "PRECIO UNIT": precio_unit,
            "V.V.": vv_calc,
            "IGV": igv_calc,
            "TOTAL": total_calc
        }
        st.session_state.gastos_db = pd.concat([st.session_state.gastos_db, pd.DataFrame([nuevo_registro])], ignore_index=True)
        st.success(f"¡Comprobante N° {num_reg} guardado correctamente en la base de datos!")

    st.divider()
    st.subheader("Cuadro de Gastos Registrados")
    st.dataframe(st.session_state.gastos_db, use_container_width=True)

# ---------------------------------------------------------
# PESTAÑA 2: MÓDULO DE ANÁLISIS E INTELIGENCIA ARTIFICIAL
# ---------------------------------------------------------
with tabs[1]:
    st.subheader("Panel de Inteligencia Operativa y Auditoría")
    
    if st.session_state.gastos_db.empty:
        st.info("El cuadro de gastos aún no tiene datos. Victoria debe registrar comprobantes en la pestaña anterior para iniciar el análisis.")
    else:
        # Métricas resumidas de control financiero
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Comprobantes", len(st.session_state.gastos_db))
        c2.metric("Valor Venta Total (V.V.)", f"S/ {st.session_state.gastos_db['V.V.'].sum():,.2f}")
        c3.metric("IGV Acumulado", f"S/ {st.session_state.gastos_db['IGV'].sum():,.2f}")
        c4.metric("Monto Total General", f"S/ {st.session_state.gastos_db['TOTAL'].sum():,.2f}")

        st.divider()

        api_key = st.text_input("Ingresa tu Gemini API Key para ejecutar el análisis:", type="password")

        if st.button("🤖 Ejecutar Auditoría e Informe con IA"):
            if not api_key:
                st.error("Por favor ingresa una API Key válida de Gemini para realizar el análisis.")
            else:
                try:
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel("gemini-1.5-pro")

                    datos_csv = st.session_state.gastos_db.to_csv(index=False)

                    prompt_maestro = f"""
                    ROL Y OBJETIVO:
                    Actúas como un Especialista en Control de Costos y Auditor Financiero de Obra/Proyectos. Tu objetivo es procesar la tabla de gastos registrada por Administración, validar la consistencia aritmética de cada comprobante, consolidar los montos acumulados por número de partida y generar un informe analítico ejecutivo.

                    TABLA DE GASTOS REGISTRADOS:
                    {datos_csv}

                    TAREAS DE LA IA:
                    1. AUDITORÍA Y VALIDACIÓN ARITMÉTICA:
                       - Verifica fila por fila que (CANT. * PRECIO UNIT) sea igual a V.V.
                       - Verifica que (V.V. * 0.18) sea igual a IGV y que V.V. + IGV sea igual a TOTAL.
                       - Si identificas cualquier discrepancia en los montos de algún comprobante (ej. Factura N° SERIE - N° CORRELATIVO), repórtalo en una sección de "Alertas de Inconsistencia".

                    2. RESUMEN EJECUTIVO GENERAL:
                       - Muestra los totales acumulados del periodo evaluado: Valor Venta (V.V.), IGV Total y Monto TOTAL.

                    3. CONSOLIDADO POR N° DE PARTIDA:
                       - Agrupa todos los gastos por el campo "N° PARTIDA".
                       - Genera una tabla resumen con las columnas: [N° PARTIDA | Subtotal V.V. | Subtotal IGV | Subtotal TOTAL | % de Incidencia Financiera].

                    4. ANÁLISIS DE PROVEEDORES E INSUMOS CLAVE:
                       - Identifica los proveedores principales (RAZON SOCIAL / RUC) de mayor volumen de gasto.
                       - Detecta variaciones o compras relevantes evaluando los precios unitarios (PRECIO UNIT) y las unidades de medida (UNID).

                    5. CONCLUSIÓN Y RECOMENDACIONES TÉCNICAS:
                       - Un párrafo breve con conclusiones clave de control de costos, señalando cuál es la partida de mayor gasto y si existe alguna concentración de riesgo.
                    """

                    with st.spinner("La IA está auditando los registros y calculando la consolidación por partida..."):
                        response = model.generate_content(prompt_maestro)
                        st.markdown("### 📋 Informe de Auditoría y Control de Costos")
                        st.markdown(response.text)
                except Exception as e:
                    st.error(f"Error al conectar con la API de IA: {e}")
