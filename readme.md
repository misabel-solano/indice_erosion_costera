# Herramienta de Índice de Erosión Costera (QGIS Plugin)

Plugin de QGIS desarrollado como parte de un **Trabajo Fin de Máster (TFM)** en SIG de código abierto.

Este plugin implementa una herramienta para calcular un **Índice de Erosión Costera** combinando información de pendiente del terreno y distancia a la línea de costa.

---

## Funcionalidad

La herramienta calcula un índice de erosión costera mediante los siguientes pasos:

1. Cálculo de la pendiente a partir de un MDT
2. Rasterización de la línea de costa
3. Cálculo de distancia a la costa
4. Reclasificación de pendiente
5. Reclasificación de distancia a costa
6. Cálculo del índice final mediante cálculo raster

El resultado es un **raster de índice de erosión costera**.

---

## Parámetros de entrada

El algoritmo requiere los siguientes datos:

- **Línea de costa** (vector lineal)
- **MDT** (Modelo Digital del Terreno)
- **Provincia** (vector poligonal)
- **Umbral de pendiente baja**
- **Umbral de pendiente media**

---

## Resultado

El plugin genera:

- **Raster del índice de erosión costera**

---
# Autor: María Isabel Solano Sanz
## TFM Máster SIG de Código Abierto, Geoinnova.