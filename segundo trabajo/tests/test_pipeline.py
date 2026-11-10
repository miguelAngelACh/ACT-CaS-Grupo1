"""
Pruebas Automatizadas de Calidad y Verificación (CMMI Nivel 3 - VER)
=====================================================================

Suite de pruebas unitarias implementadas con Pytest para validar la
integridad del pipeline de vigilancia epidemiológica de Zoonosis.

Trazabilidad de Requisitos:
  - R01 -> test_columnas_csv, test_encoding_tildes_nc01
  - R02 -> test_validacion_rechazos
  - R03 -> test_consolidado_no_vacio
  - R04 -> test_reconciliacion
"""

from pathlib import Path
import pytest
import pandas as pd

from src.pipeline import (
    cargar_datos,
    validar_datos,
    consolidar,
    verificar_reconciliacion,
    COLUMNAS_OBLIGATORIAS,
)

# Ruta estándar del dataset sintético
RUTA_DATASET = Path("data/datos_zoonosis.csv")
RUTA_RECHAZOS = Path("data/rechazos.csv")


def test_columnas_csv():
    """
    [REQ-01 | CMMI-VER] Comprueba que el archivo CSV cargado contenga
    todas las columnas oficiales exigidas por la norma técnica del MINSA.
    """
    df = cargar_datos(RUTA_DATASET)
    assert df is not None, "El DataFrame retornado no debe ser nulo."
    assert len(df) == 20, f"Se esperaban 20 filas en el dataset sintético, se encontraron {len(df)}."

    for col in COLUMNAS_OBLIGATORIAS:
        assert col in df.columns, f"La columna obligatoria '{col}' no está presente en el DataFrame."


def test_validacion_rechazos():
    """
    [REQ-02 | CMMI-VER] Comprueba que el motor de reglas de calidad detecte
    exactamente las 5 filas inválidas predefinidas y mantenga 15 válidas.
    Verifica además que el archivo de auditoría 'data/rechazos.csv' se genere
    correctamente con la columna 'motivo_rechazo'.
    """
    df = cargar_datos(RUTA_DATASET)
    df_validos, df_rechazados = validar_datos(df, ruta_rechazos=RUTA_RECHAZOS)

    # Verificación cardinal
    assert len(df_validos) == 15, f"Se esperaban 15 registros válidos, pero se obtuvieron {len(df_validos)}."
    assert len(df_rechazados) == 5, f"Se esperaban exactamente 5 registros rechazados, pero se obtuvieron {len(df_rechazados)}."

    # Verificación de IDs con no conformidad esperada (6, 11, 14, 17, 20)
    ids_rechazados_esperados = {6, 11, 14, 17, 20}
    ids_obtenidos = set(df_rechazados["id"].astype(int))
    assert ids_obtenidos == ids_rechazados_esperados, (
        f"Discrepancia en IDs rechazados. Esperados: {ids_rechazados_esperados}, Obtenidos: {ids_obtenidos}"
    )

    # Verificación de persistencia del archivo de auditoría
    assert RUTA_RECHAZOS.exists(), "El archivo 'data/rechazos.csv' debe existir tras la validación."
    df_rechazados_disco = pd.read_csv(RUTA_RECHAZOS, encoding="utf-8-sig")
    assert "motivo_rechazo" in df_rechazados_disco.columns, "Debe registrarse el motivo de rechazo."
    assert df_rechazados_disco["motivo_rechazo"].notna().all(), "Todos los rechazos deben tener motivo documentado."


def test_reconciliacion():
    """
    [REQ-04 | CMMI-VER] Comprueba que la función de reconciliación cuantitativa
    devuelva True cuando el balance de masa sea exacto (cero pérdidas).
    Adicionalmente, valida que detecte desbalances si se altera el consolidado.
    """
    df = cargar_datos(RUTA_DATASET)
    df_validos, _ = validar_datos(df, ruta_rechazos=None)
    df_consolidado = consolidar(df_validos)

    # Reconciliación nominal (debe ser True)
    es_reconciliado = verificar_reconciliacion(df_validos, df_consolidado)
    assert es_reconciliado is True, "La reconciliación de datos debe ser True para datos consistentes."

    # Prueba de control de calidad negativa: Simular alteración / pérdida de datos
    df_consolidado_alterado = df_consolidado.copy()
    df_consolidado_alterado.loc[0, "total_casos"] += 99  # Inyectar desbalance artificial
    es_reconciliado_falso = verificar_reconciliacion(df_validos, df_consolidado_alterado)
    assert es_reconciliado_falso is False, "La reconciliación debe fallar (False) si se detecta desbalance."


def test_consolidado_no_vacio():
    """
    [REQ-03 | CMMI-VER] Comprueba que el consolidado contenga datos agrupados,
    las columnas esperadas ('departamento', 'semana', 'total_casos') y que la
    suma acumulada coincida exactamente con los 15 registros válidos.
    """
    df = cargar_datos(RUTA_DATASET)
    df_validos, _ = validar_datos(df, ruta_rechazos=None)
    df_consolidado = consolidar(df_validos)

    assert not df_consolidado.empty, "El DataFrame consolidado no debe estar vacío."
    columnas_esperadas = {"departamento", "semana", "total_casos"}
    assert set(df_consolidado.columns) == columnas_esperadas, (
        f"Columnas consolidadas incorrectas. Esperadas: {columnas_esperadas}, Obtenidas: {set(df_consolidado.columns)}"
    )

    total_casos_sumados = df_consolidado["total_casos"].sum()
    assert total_casos_sumados == 15, (
        f"La suma total de casos consolidados debe ser 15, pero fue {total_casos_sumados}."
    )


def test_encoding_tildes_nc01():
    """
    [NC-01 | CMMI-PPQA & CAR] Verifica que los nombres de departamentos con tildes
    y caracteres en español (Junín, San Martín, Huánuco) se lean fielmente sin
    corrupción de caracteres (evitando problemas de codificación cp1252 / latin-1).
    """
    df = cargar_datos(RUTA_DATASET)
    departamentos = set(df["departamento"].unique())

    assert "Junín" in departamentos, "El departamento 'Junín' con tilde no fue leído correctamente."
    assert "San Martín" in departamentos, "El departamento 'San Martín' con tilde no fue leído correctamente."
    assert "Huánuco" in departamentos, "El departamento 'Huánuco' con tilde no fue leído correctamente."

