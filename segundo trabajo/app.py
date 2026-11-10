"""
Panviz Perú - Vigilancia Epidemiológica de Zoonosis
=====================================================
Interfaz Gráfica de Usuario (GUI) construida con Streamlit.
Diseñada para supervisión epidemiológica y aseguramiento de la calidad
conforme a los estándares CMMI Nivel 3 (PPQA, VER, CAR).

Autor: Equipo de Calidad de Software & Auditoría CMMI (UNSA)
Fecha: 2026
"""

from pathlib import Path
import streamlit as st
import pandas as pd
from src.pipeline import ejecutar_pipeline, COLUMNAS_OBLIGATORIAS

# -----------------------------------------------------------------------------
# Configuración Global de la Página (Streamlit Wide Layout)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Panviz Perú - Vigilancia Epidemiológica de Zoonosis",
    page_icon="🇵🇪",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------------------
# Estilos CSS Personalizados para Capturas Profesionales (Informe Académico)
# -----------------------------------------------------------------------------
st.markdown(
    """
    <style>
    /* Estilo del contenedor principal */
    .main-title-container {
        background: linear-gradient(135deg, #0d3b66 0%, #001e3d 100%);
        padding: 24px 30px;
        border-radius: 12px;
        color: #ffffff;
        margin-bottom: 25px;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.15);
    }
    .main-title-container h1 {
        color: #ffffff !important;
        font-size: 2.1rem;
        font-weight: 700;
        margin-bottom: 6px;
    }
    .main-title-container p {
        color: #e0e6ed;
        font-size: 1.05rem;
        margin-bottom: 0px;
    }
    .badge-cmmi {
        display: inline-block;
        background-color: #00a86b;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.82rem;
        font-weight: 600;
        letter-spacing: 0.5px;
        margin-top: 10px;
    }
    .badge-minsa {
        display: inline-block;
        background-color: #d90429;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.82rem;
        font-weight: 600;
        letter-spacing: 0.5px;
        margin-top: 10px;
        margin-left: 8px;
    }
    /* Estilos para las tarjetas de métricas */
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 16px 20px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.04);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 14px rgba(0,0,0,0.08);
    }
    div[data-testid="stMetric"] label {
        font-weight: 600;
        color: #475569 !important;
    }
    /* Botón principal de procesamiento */
    .stButton > button {
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
        color: white;
        font-size: 1.15rem;
        font-weight: 700;
        padding: 14px 28px;
        border-radius: 10px;
        border: none;
        box-shadow: 0 4px 12px rgba(2, 132, 199, 0.35);
        transition: all 0.25s ease;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #0369a1 0%, #075985 100%);
        box-shadow: 0 6px 18px rgba(2, 132, 199, 0.45);
        transform: scale(1.01);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Barra Lateral (Sidebar) con Trazabilidad y Metadatos CMMI
# -----------------------------------------------------------------------------
with st.sidebar:
    st.image(
        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cc/Escudo_de_la_UNSA.png/240px-Escudo_de_la_UNSA.png",
        width=110,
    )
    st.markdown("### 🏛️ Panviz-Zoonosis-CMMI")
    st.caption("**Sistema de Vigilancia Epidemiológica & Calidad**")

    st.markdown("---")
    st.markdown("#### 📋 Cumplimiento de Estándares")
    st.markdown("- **Estándar:** CMMI-DEV v2.0")
    st.markdown("- **Nivel Objetivo:** Nivel 3 (Definido)")
    st.markdown("- **Áreas de Práctica:**")
    st.markdown("  - `PPQA`: Aseguramiento de Calidad")
    st.markdown("  - `VER`: Verificación (Pytest)")
    st.markdown("  - `REQM`: Gestión de Requisitos")
    st.markdown("  - `CAR`: Análisis Causal y Resolución")

    st.markdown("---")
    st.markdown("#### 📁 Archivos del Sistema")
    st.markdown("- `data/datos_zoonosis.csv` (Entrada)")
    st.markdown("- `data/rechazos.csv` (Auditoría)")
    st.markdown("- `docs/matriz_trazabilidad.md`")
    st.markdown("- `docs/acta_auditoria_NC01.md`")

    st.markdown("---")
    st.info("💡 **Consejo Académico:** Haz clic en **Procesar Dataset** para generar las métricas y tablas requeridas para el informe.")

# -----------------------------------------------------------------------------
# Cabecera Principal (Banner Institucional)
# -----------------------------------------------------------------------------
st.markdown(
    """
    <div class="main-title-container">
        <h1>🇵🇪 Panviz Perú - Vigilancia Epidemiológica de Zoonosis</h1>
        <p>Sistema Automatizado de Control de Calidad, Ingesta, Limpieza y Reconciliación de Datos (MINSA - CDC Perú)</p>
        <span class="badge-cmmi">AUDITORÍA CMMI NIVEL 3 APROBADA</span>
        <span class="badge-minsa">NORMA TÉCNICA MINSA</span>
    </div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Estado de Sesión (Session State)
# -----------------------------------------------------------------------------
if "resultados" not in st.session_state:
    st.session_state["resultados"] = None

# -----------------------------------------------------------------------------
# Botón Grande de Procesamiento
# -----------------------------------------------------------------------------
col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
with col_btn2:
    btn_procesar = st.button("🚀 Procesar Dataset", use_container_width=True)

if btn_procesar:
    with st.spinner("Ejecutando pipeline de calidad y reconciliación de datos..."):
        try:
            resultados = ejecutar_pipeline(
                ruta_entrada="data/datos_zoonosis.csv",
                ruta_rechazos="data/rechazos.csv",
            )
            st.session_state["resultados"] = resultados
            st.toast("Pipeline ejecutado exitosamente sin discrepancias.", icon="✅")
        except Exception as e:
            st.error(f"Error crítico en el pipeline: {str(e)}")

# -----------------------------------------------------------------------------
# Renderizado de Métricas y Tablas
# -----------------------------------------------------------------------------
if st.session_state["resultados"] is not None:
    res = st.session_state["resultados"]

    st.markdown("---")
    st.markdown("### 📈 Panel de Control de Calidad y Métricas de Ingesta")

    # 4 Tarjetas Métricas Requeridas
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric(
            label="Total Registros",
            value=res["total_crudo"],
            delta="Dataset Bruto",
            help="Total de filas cargadas desde 'data/datos_zoonosis.csv'.",
        )
    with m2:
        pct_validos = (res["total_validos"] / res["total_crudo"]) * 100
        st.metric(
            label="Registros Válidos",
            value=res["total_validos"],
            delta=f"{pct_validos:.1f}% Conformes",
            delta_color="normal",
            help="Registros que cumplen todas las reglas de calidad técnica y epidemiológica.",
        )
    with m3:
        pct_rechazos = (res["total_rechazados"] / res["total_crudo"]) * 100
        st.metric(
            label="Registros Rechazados",
            value=res["total_rechazados"],
            delta=f"{pct_rechazos:.1f}% Descartados",
            delta_color="inverse",
            help="Registros no conformes enviados a 'data/rechazos.csv' con motivo documentado.",
        )
    with m4:
        # Reconciliación: Debe ser 0 (Diferencia = Válidos - Casos Consolidados)
        dif_rec = res["diferencia_reconciliacion"]
        st.metric(
            label="Reconciliación (Debe ser 0)",
            value=dif_rec,
            delta="Balance Exacto (0 pérdidas)" if dif_rec == 0 else "Discrepancia detectada",
            delta_color="normal" if dif_rec == 0 else "inverse",
            help="Diferencia matemática: Total Válidos - Suma Total de Casos Consolidados.",
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Mensaje de conformidad de reconciliación
    if res["reconciliacion_exitosa"]:
        st.success(
            f"🎯 **Control de Reconciliación APROBADO (Zero-Data-Loss):** "
            f"El número de registros válidos ({res['total_validos']}) es exactamente igual "
            f"a la sumatoria de casos consolidados ({res['suma_consolidado']}). Diferencia: **0**."
        )
    else:
        st.error("⚠️ Control de reconciliación FALLIDO: Se detectaron pérdidas o duplicidades.")

    # -------------------------------------------------------------------------
    # Pestañas de Visualización (st.tabs)
    # -------------------------------------------------------------------------
    tab_consolidado, tab_rechazos = st.tabs(["📊 Consolidado", "⚠️ Rechazos"])

    # Pestaña 1: Consolidado
    with tab_consolidado:
        st.subheader("Casos Epidemiológicos Validados y Consolidados")
        st.markdown(
            "Datos agregados por **Departamento** y **Semana Epidemiológica**, listos para reporte oficial:"
        )

        df_con = res["df_consolidado"]
        st.dataframe(
            df_con,
            use_container_width=True,
            column_config={
                "departamento": st.column_config.TextColumn("Departamento", width="medium"),
                "semana": st.column_config.NumberColumn("Semana Epidemiológica", format="%d"),
                "total_casos": st.column_config.ProgressColumn(
                    "Total Casos",
                    format="%d casos",
                    min_value=0,
                    max_value=int(df_con["total_casos"].max()) if not df_con.empty else 10,
                ),
            },
            hide_index=True,
        )

        col_c1, col_c2 = st.columns([2, 1])
        with col_c1:
            st.markdown("#### 🗺️ Distribución de Casos por Departamento")
            resumen_dept = df_con.groupby("departamento")["total_casos"].sum()
            st.bar_chart(resumen_dept)

        with col_c2:
            st.markdown("#### 📥 Exportar Consolidado")
            csv_con = df_con.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
            st.download_button(
                label="⬇️ Descargar Consolidado (CSV)",
                data=csv_con,
                file_name="consolidado_zoonosis.csv",
                mime="text/csv",
                use_container_width=True,
            )
            st.caption("Formato UTF-8 con BOM compatible con Microsoft Excel y PowerBI.")

    # Pestaña 2: Rechazos
    with tab_rechazos:
        st.subheader("Registros No Conformes y Trazabilidad de Motivos")
        st.markdown(
            "Registros que no superaron los controles de calidad CMMI-VER y fueron desestimados para proteger la integridad del análisis:"
        )

        df_rec = res["df_rechazados"]
        st.dataframe(
            df_rec,
            use_container_width=True,
            column_config={
                "id": st.column_config.NumberColumn("ID", width="small", format="%d"),
                "departamento": st.column_config.TextColumn("Departamento"),
                "enfermedad": st.column_config.TextColumn("Enfermedad"),
                "motivo_rechazo": st.column_config.TextColumn(
                    "Motivo Técnico del Rechazo (CMMI-PPQA)",
                    width="large",
                ),
            },
            hide_index=True,
        )

        col_r1, col_r2 = st.columns([2, 1])
        with col_r1:
            st.markdown("#### 🔍 Detalle de Hallazgos Detectados")
            for _, fila in df_rec.iterrows():
                st.markdown(
                    f"- **Fila ID {fila['id']}** ({fila['departamento']} - {fila['enfermedad']}): "
                    f"`{fila['motivo_rechazo']}`"
                )

        with col_r2:
            st.markdown("#### 📥 Exportar Registro de Rechazos")
            csv_rec = df_rec.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
            st.download_button(
                label="⬇️ Descargar Rechazos (CSV)",
                data=csv_rec,
                file_name="rechazos_auditoria.csv",
                mime="text/csv",
                use_container_width=True,
            )
            st.caption("Archivo de evidencia auditable para el comité de calidad (CMMI CAR).")

else:
    # Estado inicial antes de hacer clic en "Procesar Dataset"
    st.markdown("---")
    st.info(
        "👋 **Bienvenido al Sistema de Vigilancia Epidemiológica Panviz.** "
        "El dataset `data/datos_zoonosis.csv` se encuentra cargado y listo para ser validado. "
        "Presione el botón **'Procesar Dataset'** en la parte superior para iniciar la ejecución del pipeline."
    )

    # Vista previa del dataset crudo
    with st.expander("👁️ Vista previa del Dataset Sintético Inicial (20 Registros)", expanded=True):
        df_preview = pd.read_csv("data/datos_zoonosis.csv", encoding="utf-8-sig")
        st.dataframe(df_preview, use_container_width=True, hide_index=True)
        st.caption("Dataset con 15 registros conformes y 5 registros con no conformidades inducidas para prueba de auditoría.")

# -----------------------------------------------------------------------------
# Pie de Página Institucional
# -----------------------------------------------------------------------------
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #64748b; font-size: 0.88rem; padding: 10px;">
        <strong>Panviz-Zoonosis-CMMI</strong> | Proyecto de Calidad de Software — UNSA 2026<br>
        Alineado con el Modelo de Madurez <strong>CMMI Nivel 3</strong> (PPQA, VER, REQM, CAR)
        y la Norma Técnica de Vigilancia Epidemiológica de Zoonosis (MINSA Perú).
    </div>
    """,
    unsafe_allow_html=True,
)

