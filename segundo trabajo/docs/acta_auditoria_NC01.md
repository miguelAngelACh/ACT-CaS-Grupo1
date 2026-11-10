# Acta de No Conformidad y Acción Correctiva (NC-01)
## Auditoría Interna de Calidad de Software — CMMI Nivel 3 (PPQA / CAR)

---

### 1. Datos Generales de la Auditoría

| Parámetro | Detalle de Registro |
| :--- | :--- |
| **Código de Hallazgo:** | **NC-2026-PPQA-001** (Identificador: **NC-01**) |
| **Proyecto:** | Panviz-Zoonosis-CMMI (Sistema de Vigilancia Epidemiológica MINSA) |
| **Área de Proceso CMMI:** | **PPQA** (Process and Product Quality Assurance) & **CAR** (Causal Analysis and Resolution) |
| **Nivel de Madurez:** | Nivel 3: Definido (*Defined*) |
| **Fecha de Hallazgo:** | 09 de Noviembre de 2026 |
| **Auditor Responsable:** | Auditor Líder de Calidad de Software (CMMI Institute Certified Associate) |
| **Responsable de Solución:** | Equipo de Desarrollo Backend & Arquitectura de Datos |
| **Clasificación del Hallazgo:** | **No Conformidad Mayor (Mayor Defect)** — Integridad de Datos |
| **Estado:** | **CERRADA Y VERIFICADA** ✅ |

---

### 2. Descripción de la No Conformidad (Hallazgo)
Durante el ciclo de pruebas de integración de la ingesta de datos epidemiológicos procedentes de diversas Direcciones Regionales de Salud (DIRESA), se detectó que:

> **Hallazgo Específico:**  
> *"El sistema fallaba al leer acentos en los departamentos (ej. Junín) por no usar `utf-8-sig`."*

#### Evidencia Objetiva Recolectada:
1. En entornos de ejecución bajo sistema operativo Microsoft Windows, la función estándar de lectura utilizaba la codificación predeterminada del sistema (`cp1252` / `ANSI`).
2. Al procesar el archivo CSV generado en herramientas de análisis epidemiológico o Microsoft Excel, los nombres de los departamentos que contienen tildes o caracteres diacríticos en español sufrían corrupción de caracteres (*mojibake*) o excepciones del tipo:
   ```text
   UnicodeDecodeError: 'charmap' codec can't decode byte 0x81 in position 14: character maps to <undefined>
   ```
   O en su defecto, departamentos como **Junín** eran leídos incorrectamente como `JunÃ­n`, **San Martín** como `San MartÃ­n`, y **Huánuco** como `HuÃ¡nuco`, generando agrupaciones duplicadas o fallas de validación geográfica en el consolidado.

---

### 3. Análisis de Causa Raíz (Metodología de los 5 Porqués - CAR)

1. **¿Por qué fallaba la lectura de acentos en departamentos como Junín?**  
   *Porque el DataFrame interpretaba los bytes con una tabla de caracteres errónea.*
2. **¿Por qué se utilizaba una tabla de caracteres errónea?**  
   *Porque la invocación de `pd.read_csv()` en el módulo de ingesta no especificaba explícitamente el parámetro `encoding`.*
3. **¿Por qué no se especificaba dicho parámetro en el código fuente inicial?**  
   *Porque en pruebas de laboratorio en plataformas UNIX/macOS el encoding predeterminado es UTF-8 sin BOM, ocultando el defecto presente en entornos Windows.*
4. **¿Por qué ocurrió corrupción al exportar datasets oficiales del MINSA/Excel?**  
   *Porque Excel y herramientas gubernamentales en Windows anteponen comúnmente una firma BOM (`\xef\xbb\xbf`) al inicio del flujo UTF-8.*
5. **Causa Raíz Determinada:**  
   *Omisión de la política de codificación universal forzada (`utf-8-sig`) en los lineamientos de codificación de la Solución Técnica (TS) y falta de pruebas de verificación automatizadas sobre caracteres diacríticos (VER).*

---

### 4. Plan de Acción y Tratamiento del Defecto

#### 4.1. Acción de Contención Inmediata
- Notificación al equipo de desarrollo y suspensión temporal de la homologación del pipeline en ambientes de prueba.

#### 4.2. Acción Correctiva (Solución Definitiva)
- **Implementación Técnica:** Se actualizó el código fuente de [`src/pipeline.py`](file:///d:/UNSA/2026_B/CALIDAD%20DE%20SOFTWARE/segundo%20trabajo/src/pipeline.py#L38-L75) en la función `cargar_datos()` para forzar explícitamente la lectura con codificación `utf-8-sig`:
  ```python
  # Implementación de la Acción Correctiva NC-01
  try:
      df: pd.DataFrame = pd.read_csv(path_obj, encoding="utf-8-sig")
  except UnicodeDecodeError:
      df = pd.read_csv(path_obj, encoding="utf-8")
  ```
- **Resultado:** Se garantiza compatibilidad total con archivos UTF-8 estándar, archivos con marca BOM generados por Microsoft Windows/Excel, y retención impecable de tildes peruanas (Junín, Huánuco, San Martín).

#### 4.3. Acción Preventiva (Garantía de No Recurrencia)
- **Automatización de Pruebas de Regresión:** Se incorporó en la suite de Pytest ([`tests/test_pipeline.py`](file:///d:/UNSA/2026_B/CALIDAD%20DE%20SOFTWARE/segundo%20trabajo/tests/test_pipeline.py#L112-L125)) el caso de prueba unitaria especializado `test_encoding_tildes_nc01()`.
- **Regla en Estándar de Codificación (Coding Guideline):** Se estipuló que todo módulo de I/O de archivos de texto o CSV en el proyecto debe emplear obligatoriamente `encoding="utf-8-sig"`.

---

### 5. Verificación de Eficacia y Cierre de la Auditoría

| Ítem de Verificación | Método de Validación | Resultado Observado | Estado |
| :--- | :--- | :--- | :---: |
| Lectura de registro `Junín` | Ejecución de `test_encoding_tildes_nc01` | Cadena idéntica a "Junín" | Conforme ✅ |
| Lectura de registro `San Martín` | Inspección de memoria y prueba Pytest | Cadena idéntica a "San Martín" | Conforme ✅ |
| Lectura de registro `Huánuco` | Inspección de memoria y prueba Pytest | Cadena idéntica a "Huánuco" | Conforme ✅ |
| Suite completa de pruebas | `pytest -v tests/test_pipeline.py` | 5/5 Pruebas Exitosas (100%) | Conforme ✅ |

#### Dictamen Final del Auditor Líder (CMMI PPQA):
> *"Habiéndose ejecutado las pruebas de regresión automatizadas de forma exitosa y comprobando la correcta visualización de caracteres diacríticos tanto en la capa de datos como en la interfaz gráfica Streamlit, se declara la No Conformidad NC-01 como **CERRADA SATISFACTORIAMENTE**."*

---

### 6. Cuadro de Firmas

| Responsabilidad | Nombre y Cargo | Fecha de Firma | Firma |
| :--- | :--- | :---: | :---: |
| **Auditor Líder de Calidad** | Mg. Auditor CMMI Nivel 3 (PPQA) | 09/11/2026 | *Firma Digital Aprobada* |
| **Líder de Desarrollo Backend** | Ing. Senior de Software (TS) | 09/11/2026 | *Firma Digital Aprobada* |
| **Gerente de Calidad de Software** | Director de QA & Gobernanza | 09/11/2026 | *V°B° Institucional* |

