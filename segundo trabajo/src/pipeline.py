"""
Módulo de Procesamiento y Validación Epidemiológica de Zoonosis (MINSA)
========================================================================

Este módulo implementa el pipeline de ingesta, depuración, consolidación
y reconciliación de datos epidemiológicos para la vigilancia de zoonosis.
Cumple con las prácticas de Aseguramiento de la Calidad de Procesos y
Productos (PPQA) y Verificación (VER) del estándar CMMI Nivel 3.

Autor: Auditor de Calidad & Ingeniero Senior de Software
Organización: Universidad Nacional de San Agustín (UNSA)
Proyecto: Panviz-Zoonosis-CMMI
Versión: 1.0.0
"""

from pathlib import Path
from typing import List, Optional, Tuple, Union
import numpy as np
import pandas as pd

# Columnas oficiales obligatorias según la norma técnica del MINSA
COLUMNAS_OBLIGATORIAS: List[str] = [
    "id",
    "departamento",
    "provincia",
    "distrito",
    "enfermedad",
    "ano",
    "semana",
    "edad",
    "tipo_edad",
    "sexo",
]

# Valores permitidos para codificación epidemiológica estándar
TIPOS_EDAD_PERMITIDOS: List[str] = ["A", "M", "D"]  # Años, Meses, Días
SEXOS_PERMITIDOS: List[str] = ["M", "F"]
RANGO_SEMANA_MIN: int = 1
RANGO_SEMANA_MAX: int = 53
RANGO_ANO_MIN: int = 2000
RANGO_ANO_MAX: int = 2026
EDAD_MAX_PERMISIBLE: int = 120


def cargar_datos(ruta_archivo: Union[str, Path] = "data/datos_zoonosis.csv") -> pd.DataFrame:
    """
    Carga el dataset epidemiológico desde un archivo CSV aplicando codificación UTF-8
    y valida la integridad estructural de las cabeceras requeridas.

    Cumple con el requerimiento R01 y la Acción Correctiva NC-01 para garantizar
    la lectura correcta de caracteres especiales y tildes (ej. Junín, San Martín, Huánuco).

    Args:
        ruta_archivo (Union[str, Path]): Ruta relativa o absoluta del archivo CSV a procesar.
            Por defecto 'data/datos_zoonosis.csv'.

    Returns:
        pd.DataFrame: DataFrame de pandas con los datos crudos cargados.

    Raises:
        FileNotFoundError: Si el archivo especificado no existe en el sistema de archivos.
        ValueError: Si faltan columnas requeridas según la especificación MINSA.
        Exception: Ante fallos generales de I/O o formato corrupto del CSV.
    """
    path_obj = Path(ruta_archivo)
    if not path_obj.exists():
        raise FileNotFoundError(
            f"[ERROR CMMI-VER] No se encontró el dataset en la ruta especificada: '{path_obj.resolve()}'"
        )

    # Nota de Auditoría CMMI (NC-01): Se fuerza 'utf-8-sig' para tolerar BOM de Windows/Excel
    try:
        df: pd.DataFrame = pd.read_csv(path_obj, encoding="utf-8-sig")
    except UnicodeDecodeError:
        df = pd.read_csv(path_obj, encoding="utf-8")

    # Limpieza de espacios en blanco en los nombres de columnas
    df.columns = [col.strip().lower() for col in df.columns]

    columnas_faltantes = [col for col in COLUMNAS_OBLIGATORIAS if col not in df.columns]
    if columnas_faltantes:
        raise ValueError(
            f"[ERROR CMMI-VER] Estructura de datos no conforme. Columnas ausentes: {columnas_faltantes}"
        )

    return df


def validar_datos(
    df: pd.DataFrame,
    ruta_rechazos: Optional[Union[str, Path]] = "data/rechazos.csv",
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Evalúa la conformidad de cada registro contra las reglas de calidad de datos epidemiológicos.
    Separa los registros conformes (válidos) de los no conformes (rechazados),
    documentando la causa raíz técnica de cada rechazo para trazabilidad CMMI.

    Reglas de Calidad Evaluadas:
      - RC01: Edad no vacía y convertible a número entero no negativo y <= 120.
      - RC02: Tipo de edad dentro del catálogo normativo MINSA ('A', 'M', 'D').
      - RC03: Semana epidemiológica en rango válido [1, 53].
      - RC04: Año epidemiológico en rango operacional [2000, 2026].
      - RC05: Sexo biológico válido ('M', 'F').
      - RC06: Campos geográficos no nulos ni vacíos.

    Args:
        df (pd.DataFrame): Dataset crudo cargado en memoria.
        ruta_rechazos (Optional[Union[str, Path]]): Ruta donde se persistirán las filas
            rechazadas. Si es None, no se escribe a disco.

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]:
            - df_validos: Registros que aprobaron todas las reglas de calidad.
            - df_rechazados: Registros desestimados, con columna 'motivo_rechazo'.
    """
    filas_validas: List[dict] = []
    filas_rechazadas: List[dict] = []

    for _, row in df.iterrows():
        fila_dict = row.to_dict()
        motivos: List[str] = []

        # Validación 1: Geografía y campos textuales esenciales
        for campo in ["departamento", "provincia", "distrito", "enfermedad"]:
            val_campo = fila_dict.get(campo)
            if pd.isna(val_campo) or str(val_campo).strip() == "":
                motivos.append(f"Campo geográfico/epidemiológico '{campo}' nulo o vacío")

        # Validación 2: Edad
        val_edad = fila_dict.get("edad")
        if pd.isna(val_edad) or str(val_edad).strip() == "":
            motivos.append("Edad no especificada o nula")
        else:
            try:
                edad_num = float(val_edad)
                if np.isnan(edad_num):
                    motivos.append("Edad con formato no numérico")
                elif edad_num < 0:
                    motivos.append(f"Edad negativa ({edad_num}) fuera de límites permisibles")
                elif edad_num > EDAD_MAX_PERMISIBLE:
                    motivos.append(f"Edad ({edad_num}) excede límite fisiológico ({EDAD_MAX_PERMISIBLE})")
                else:
                    # Normalización a entero para registros válidos
                    fila_dict["edad"] = int(edad_num)
            except (ValueError, TypeError):
                motivos.append(f"Edad '{val_edad}' no convertible a entero")

        # Validación 3: Tipo de Edad
        val_tipo_edad = fila_dict.get("tipo_edad")
        if pd.isna(val_tipo_edad) or str(val_tipo_edad).strip() == "":
            motivos.append("Tipo de edad nulo o ausente")
        else:
            tipo_edad_str = str(val_tipo_edad).strip().upper()
            if tipo_edad_str not in TIPOS_EDAD_PERMITIDOS:
                motivos.append(
                    f"Tipo de edad '{val_tipo_edad}' inválido (requerido: {', '.join(TIPOS_EDAD_PERMITIDOS)})"
                )
            else:
                fila_dict["tipo_edad"] = tipo_edad_str

        # Validación 4: Semana Epidemiológica
        val_semana = fila_dict.get("semana")
        if pd.isna(val_semana) or str(val_semana).strip() == "":
            motivos.append("Semana epidemiológica nula")
        else:
            try:
                semana_num = int(val_semana)
                if not (RANGO_SEMANA_MIN <= semana_num <= RANGO_SEMANA_MAX):
                    motivos.append(
                        f"Semana epidemiológica {semana_num} fuera de rango [{RANGO_SEMANA_MIN}, {RANGO_SEMANA_MAX}]"
                    )
                else:
                    fila_dict["semana"] = semana_num
            except (ValueError, TypeError):
                motivos.append(f"Semana epidemiológica '{val_semana}' no numérica")

        # Validación 5: Año
        val_ano = fila_dict.get("ano")
        if pd.isna(val_ano) or str(val_ano).strip() == "":
            motivos.append("Año epidemiológico nulo")
        else:
            try:
                ano_num = int(val_ano)
                if not (RANGO_ANO_MIN <= ano_num <= RANGO_ANO_MAX):
                    motivos.append(
                        f"Año {ano_num} fuera del rango histórico/actual permitido [{RANGO_ANO_MIN}, {RANGO_ANO_MAX}]"
                    )
                else:
                    fila_dict["ano"] = ano_num
            except (ValueError, TypeError):
                motivos.append(f"Año epidemiológico '{val_ano}' no numérico")

        # Validación 6: Sexo
        val_sexo = fila_dict.get("sexo")
        if pd.isna(val_sexo) or str(val_sexo).strip() == "":
            motivos.append("Sexo biológico nulo")
        else:
            sexo_str = str(val_sexo).strip().upper()
            if sexo_str not in SEXOS_PERMITIDOS:
                motivos.append(
                    f"Sexo '{val_sexo}' no admitido (valores permitidos: {', '.join(SEXOS_PERMITIDOS)})"
                )
            else:
                fila_dict["sexo"] = sexo_str

        # Clasificación CMMI: Conforme vs No Conforme
        if motivos:
            fila_dict["motivo_rechazo"] = "; ".join(motivos)
            filas_rechazadas.append(fila_dict)
        else:
            filas_validas.append(fila_dict)

    df_validos = pd.DataFrame(filas_validas, columns=COLUMNAS_OBLIGATORIAS)
    cols_rechazos = COLUMNAS_OBLIGATORIAS + ["motivo_rechazo"]
    df_rechazados = pd.DataFrame(filas_rechazadas, columns=cols_rechazos)

    # Persistencia de auditoría para trazabilidad CMMI
    if ruta_rechazos is not None:
        path_rechazos = Path(ruta_rechazos)
        path_rechazos.parent.mkdir(parents=True, exist_ok=True)
        df_rechazados.to_csv(path_rechazos, index=False, encoding="utf-8-sig")

    return df_validos, df_rechazados


def consolidar(df_validos: pd.DataFrame) -> pd.DataFrame:
    """
    Agrupa y consolida los casos epidemiológicos válidos por 'departamento' y 'semana'.

    Calcula la métrica de agregación 'total_casos' para alimentar los tableros
    de control y vigilancia del MINSA.

    Args:
        df_validos (pd.DataFrame): Conjunto de datos depurados y aprobados por la fase de validación.

    Returns:
        pd.DataFrame: Resumen tabular agrupado con columnas:
            ['departamento', 'semana', 'total_casos'], ordenado de forma ascendente.
    """
    if df_validos.empty:
        return pd.DataFrame(columns=["departamento", "semana", "total_casos"])

    df_consolidado = (
        df_validos.groupby(["departamento", "semana"], as_index=False)
        .size()
        .rename(columns={"size": "total_casos"})
    )

    df_consolidado = df_consolidado.sort_values(
        by=["departamento", "semana"], ascending=[True, True]
    ).reset_index(drop=True)

    return df_consolidado


def verificar_reconciliacion(
    df_validos: pd.DataFrame, df_consolidado: pd.DataFrame
) -> bool:
    """
    Ejecuta el control de reconciliación cuantitativa y balance de masa de datos (Data Integrity Check).

    Comprueba que la sumatoria aritmética de casos en el dataset consolidado
    sea exactamente idéntica al número cardinal de registros válidos procesados:
        sum(df_consolidado['total_casos']) == len(df_validos)

    Este control garantiza cero pérdidas o duplicidades durante la transformación (ETL).

    Args:
        df_validos (pd.DataFrame): Registros válidos antes de la agregación.
        df_consolidado (pd.DataFrame): Registros agrupados post-agregación.

    Returns:
        bool: True si la reconciliación es perfecta (diferencia == 0), False si existe discrepancia.
    """
    conteo_validos: int = len(df_validos)
    if df_consolidado.empty:
        suma_consolidada: int = 0
    else:
        suma_consolidada = int(df_consolidado["total_casos"].sum())

    return conteo_validos == suma_consolidada


def ejecutar_pipeline(
    ruta_entrada: Union[str, Path] = "data/datos_zoonosis.csv",
    ruta_rechazos: Union[str, Path] = "data/rechazos.csv",
) -> dict:
    """
    Función orquestadora de alto nivel del pipeline completo para consumo del frontend y tests.

    Returns:
        dict: Diccionario estructurado con las métricas clave, DataFrames y estado de reconciliación.
    """
    df_crudo = cargar_datos(ruta_entrada)
    df_validos, df_rechazados = validar_datos(df_crudo, ruta_rechazos=ruta_rechazos)
    df_consolidado = consolidar(df_validos)
    reconciliacion_exitosa = verificar_reconciliacion(df_validos, df_consolidado)

    total_crudo = len(df_crudo)
    total_validos = len(df_validos)
    total_rechazados = len(df_rechazados)
    suma_consolidado = int(df_consolidado["total_casos"].sum()) if not df_consolidado.empty else 0
    diferencia_reconciliacion = total_validos - suma_consolidado

    return {
        "df_crudo": df_crudo,
        "df_validos": df_validos,
        "df_rechazados": df_rechazados,
        "df_consolidado": df_consolidado,
        "total_crudo": total_crudo,
        "total_validos": total_validos,
        "total_rechazados": total_rechazados,
        "suma_consolidado": suma_consolidado,
        "diferencia_reconciliacion": diferencia_reconciliacion,
        "reconciliacion_exitosa": reconciliacion_exitosa,
    }

