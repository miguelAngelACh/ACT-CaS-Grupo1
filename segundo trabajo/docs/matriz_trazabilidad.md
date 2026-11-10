# Matriz de Trazabilidad de Requisitos (RTM)
## Proyecto: Panviz-Zoonosis-CMMI
### Estándar: CMMI-DEV v2.0 / Nivel de Madurez 3 (Defined)
**Áreas de Práctica:** Gestión de Requisitos (REQM), Verificación (VER), Aseguramiento de Calidad de Procesos y Productos (PPQA)  
**Institución:** Universidad Nacional de San Agustín (UNSA) — Escuela Profesional de Ciencia de la Computación  
**Asignatura:** Calidad de Software  
**Fecha de Emisión:** 09/11/2026  
**Versión del Documento:** 1.0.0  
**Responsable:** Auditor Líder de Calidad & Ingeniero Senior de Software  

---

## 1. Propósito y Alcance
El propósito de la presente Matriz de Trazabilidad de Requisitos (RTM, por sus siglas en inglés) es garantizar la bidireccionalidad y consistencia integral entre los requerimientos funcionales y de calidad del sistema de vigilancia epidemiológica de zoonosis (MINSA), los componentes de arquitectura e implementación en código fuente (`src/pipeline.py`, `app.py`), y la batería de pruebas automatizadas de verificación (`tests/test_pipeline.py`), en conformidad con las metas específicas del área de proceso **CMMI-VER (Verification)** y **CMMI-REQM (Requirements Management)**.

---

## 2. Matriz de Trazabilidad Bidireccional

| ID Requisito | Descripción del Requisito Funcional / Calidad | Componente de Diseño / Código Fuente | Prueba Automatizada (Pytest) | Criterio de Aceptación CMMI (VER) | Estado de Verificación |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **R01** | **Ingesta e Integridad Estructural del Dataset:** Carga del archivo CSV de vigilancia epidemiológica validando existencia y presencia exacta de las 10 columnas normadas por el MINSA (`id, departamento, provincia, distrito, enfermedad, ano, semana, edad, tipo_edad, sexo`), garantizando lectura UTF-8 sin alteración de caracteres con diacríticos. | [`src/pipeline.py`](file:///d:/UNSA/2026_B/CALIDAD%20DE%20SOFTWARE/segundo%20trabajo/src/pipeline.py#L38-L82)<br>`cargar_datos()` | [`tests/test_pipeline.py`](file:///d:/UNSA/2026_B/CALIDAD%20DE%20SOFTWARE/segundo%20trabajo/tests/test_pipeline.py#L27-L38)<br>`test_columnas_csv()`<br>`test_encoding_tildes_nc01()` | El archivo contiene 20 registros, 10 columnas obligatorias y preserva nombres con tildes (`Junín`, `San Martín`, `Huánuco`) sin errores de decodificación. | **APROBADO** ✅ |
| **R02** | **Depuración y Registro de No Conformidades:** Filtrado y separación automática de registros no conformes (5 filas inválidas) generando un archivo de auditoría (`data/rechazos.csv`) con trazabilidad explícita del motivo del descarte (edad vacía/negativa, tipo_edad erróneo, fecha/semana anómala). | [`src/pipeline.py`](file:///d:/UNSA/2026_B/CALIDAD%20DE%20SOFTWARE/segundo%20trabajo/src/pipeline.py#L85-L208)<br>`validar_datos()` | [`tests/test_pipeline.py`](file:///d:/UNSA/2026_B/CALIDAD%20DE%20SOFTWARE/segundo%20trabajo/tests/test_pipeline.py#L41-L67)<br>`test_validacion_rechazos()` | Identificación unívoca de las 5 filas defectuosas (IDs 6, 11, 14, 17, 20), generación del archivo físico de rechazos y persistencia de 15 filas aptas. | **APROBADO** ✅ |
| **R03** | **Consolidación Epidemiológica Multidimensional:** Agrupación y sumarización de los casos válidos por `departamento` y `semana` epidemiológica para generar la métrica agregada `total_casos`. | [`src/pipeline.py`](file:///d:/UNSA/2026_B/CALIDAD%20DE%20SOFTWARE/segundo%20trabajo/src/pipeline.py#L211-L238)<br>`consolidar()` | [`tests/test_pipeline.py`](file:///d:/UNSA/2026_B/CALIDAD%20DE%20SOFTWARE/segundo%20trabajo/tests/test_pipeline.py#L90-L109)<br>`test_consolidado_no_vacio()` | Tabla resultante no vacía, con esquema `['departamento', 'semana', 'total_casos']` y total acumulado equivalente a los 15 casos aptos. | **APROBADO** ✅ |
| **R04** | **Control Cuantitativo de Reconciliación (Zero-Loss):** Verificación matemática estricta de balance de masa de datos: $\sum \text{total\_casos}_{\text{consolidado}} == \text{Total Registros Válidos}$, retornando estado booleano de integridad. | [`src/pipeline.py`](file:///d:/UNSA/2026_B/CALIDAD%20DE%20SOFTWARE/segundo%20trabajo/src/pipeline.py#L241-L265)<br>`verificar_reconciliacion()` | [`tests/test_pipeline.py`](file:///d:/UNSA/2026_B/CALIDAD%20DE%20SOFTWARE/segundo%20trabajo/tests/test_pipeline.py#L70-L87)<br>`test_reconciliacion()` | Retorno estricto de `True` cuando la diferencia es 0, y detección oportuna de inconsistencia (`False`) ante cualquier desviación inducida. | **APROBADO** ✅ |
| **R05** | **Interfaz Gráfica de Supervisión y Métricas:** Dashboard interactivo moderno en Streamlit con visualización ejecutiva en 4 tarjetas métricas (Total, Válidos, Rechazados, Reconciliación = 0) y doble pestaña analítica (Consolidado y Rechazos). | [`app.py`](file:///d:/UNSA/2026_B/CALIDAD%20DE%20SOFTWARE/segundo%20trabajo/app.py)<br>`main()` | Inspección visual / Pruebas funcionales de interfaz | Despliegue responsivo wide-layout, activación bajo botón "Procesar Dataset", renderizado de métricas y tablas dinámicas sin excepciones de runtime. | **APROBADO** ✅ |

---

## 3. Cobertura de Verificación y Métricas de Calidad
- **Total de Requisitos Normados:** 5 (100% de cobertura de código y pruebas).
- **Pruebas Automatizadas Ejecutadas:** 5 casos de prueba unitaria.
- **Tasa de Aprobación de Pruebas (Pass Rate):** 100% (5/5 pruebas exitosas).
- **Control de Defectos Residuales:** 0 defectos abiertos.

---

## 4. Firmas de Conformidad

| Rol CMMI | Nombre y Apellidos | Firma / V°B° |
| :--- | :--- | :---: |
| **Auditor Líder de Calidad (PPQA)** | Mg. Auditor de Calidad CMMI L3 | *Revisado y Conforme* |
| **Líder Técnico de Desarrollo (TS)** | Ing. Senior de Software | *Implementado y Verificado* |

