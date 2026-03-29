from qgis.core import (
    QgsProcessingAlgorithm,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterRasterLayer,
    QgsProcessingParameterVectorLayer,
    QgsProcessingParameterNumber,
    QgsProcessingParameterRasterDestination,
    QgsProcessing
)

import processing
from qgis.PyQt.QtGui import QIcon
import os


class HerramientaErosionCostera(QgsProcessingAlgorithm):

    LINEA_COSTA = "linea_costa"
    MDT = "mdt_entrada"
    PROVINCIA = "provincia"
    UMBRAL_BAJO = "umbral_pendiente_baja"
    UMBRAL_MEDIO = "umbral_pendiente_media"
    OUTPUT = "indice_erosion_final"

    def initAlgorithm(self, config=None):

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.LINEA_COSTA,
                "Linea de costa",
                [QgsProcessing.TypeVectorLine]
            )
        )

        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.MDT,
                "MDT entrada"
            )
        )

        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.PROVINCIA,
                "Provincia",
                [QgsProcessing.TypeVectorPolygon]
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.UMBRAL_BAJO,
                "Umbral pendiente baja",
                type=QgsProcessingParameterNumber.Double,
                defaultValue=10
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.UMBRAL_MEDIO,
                "Umbral pendiente media",
                type=QgsProcessingParameterNumber.Double,
                defaultValue=30
            )
        )

        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.OUTPUT,
                "Indice erosion final"
            )
        )

    def processAlgorithm(self, parameters, context, feedback):

        results = {}

        mdt = self.parameterAsRasterLayer(parameters, self.MDT, context)

        # Pendiente
        slope = processing.run(
            "native:slope",
            {
                'INPUT': mdt,
                'Z_FACTOR': 1,
                'OUTPUT': 'TEMPORARY_OUTPUT'
            },
            context=context,
            feedback=feedback
        )

        # Reclasificar pendiente
        slope_reclass = processing.run(
            "native:reclassifybytable",
            {
                'INPUT_RASTER': slope['OUTPUT'],
                'RASTER_BAND': 1,
                'TABLE': [
                    0, parameters[self.UMBRAL_BAJO], 1,
                    parameters[self.UMBRAL_BAJO], parameters[self.UMBRAL_MEDIO], 2,
                    parameters[self.UMBRAL_MEDIO], 90, 3
                ],
                'NO_DATA': -9999,
                'RANGE_BOUNDARIES': 0,
                'DATA_TYPE': 5,
                'OUTPUT': 'TEMPORARY_OUTPUT'
            },
            context=context,
            feedback=feedback
        )

        # Rasterizar línea de costa
        coast = processing.run(
            "gdal:rasterize",
            {
                'INPUT': parameters[self.LINEA_COSTA],
                'BURN': 1,
                'UNITS': 1,
                'WIDTH': 5,
                'HEIGHT': 5,
                'EXTENT': mdt.extent(),
                'OUTPUT': 'TEMPORARY_OUTPUT'
            },
            context=context,
            feedback=feedback
        )

        # Distancia a costa
        distancia = processing.run(
            "gdal:proximity",
            {
                'INPUT': coast['OUTPUT'],
                'VALUES': '1',
                'UNITS': 0,
                'DATA_TYPE': 5,
                'OUTPUT': 'TEMPORARY_OUTPUT'
            },
            context=context,
            feedback=feedback
        )

        # Reclasificar distancia
        dist_reclass = processing.run(
            "native:reclassifybytable",
            {
                'INPUT_RASTER': distancia['OUTPUT'],
                'RASTER_BAND': 1,
                'TABLE': [
                    0, 1000, 1,
                    1000, 5000, 2,
                    5000, 9999999, 3
                ],
                'NO_DATA': -9999,
                'RANGE_BOUNDARIES': 0,
                'DATA_TYPE': 5,
                'OUTPUT': 'TEMPORARY_OUTPUT'
            },
            context=context,
            feedback=feedback
        )

        # Sumar pendiente + distancia
        suma = processing.run(
            "gdal:rastercalculator",
            {
                'INPUT_A': slope_reclass['OUTPUT'],
                'BAND_A': 1,
                'INPUT_B': dist_reclass['OUTPUT'],
                'BAND_B': 1,
                'FORMULA': 'A+B',
                'RTYPE': 5,
                'OUTPUT': 'TEMPORARY_OUTPUT'
            },
            context=context,
            feedback=feedback
        )

        # Rasterizar provincia (máscara)
        provincia_raster = processing.run(
            "gdal:rasterize",
            {
                'INPUT': parameters[self.PROVINCIA],
                'BURN': 1,
                'UNITS': 1,
                'WIDTH': 5,
                'HEIGHT': 5,
                'EXTENT': mdt.extent(),
                'OUTPUT': 'TEMPORARY_OUTPUT'
            },
            context=context,
            feedback=feedback
        )

        # Aplicar máscara
        final = processing.run(
            "gdal:rastercalculator",
            {
                'INPUT_A': suma['OUTPUT'],
                'BAND_A': 1,
                'INPUT_B': provincia_raster['OUTPUT'],
                'BAND_B': 1,
                'FORMULA': 'A*B',
                'RTYPE': 5,
                'OUTPUT': parameters[self.OUTPUT]
            },
            context=context,
            feedback=feedback
        )

        results[self.OUTPUT] = final['OUTPUT']

        return results

    def name(self):
        return "indice_erosion_costera"

    def displayName(self):
        return "Indice Erosion Costera"

    def group(self):
        return "TFM SIG Codigo Abierto"

    def groupId(self):
        return "tfm_sig"
    
    def icon(self):
        return QIcon(os.path.join(os.path.dirname(__file__), "icon.png"))
    
    def shortHelpString(self):
        return """
<h2>Índice de Erosión Costera</h2>

<h3>Descripción</h3>
<p>
Este algoritmo calcula un índice de erosión costera combinando la pendiente del terreno
y la distancia a la línea de costa. El resultado final se limita mediante una máscara
provincial.
</p>

<h3>Parámetros de entrada</h3>
<ul>
<li><b>Línea de costa:</b> capa de líneas de la costa.</li>
<li><b>MDT:</b> modelo digital del terreno.</li>
<li><b>Provincia:</b> máscara de la zona terrestre.</li>
<li><b>Umbral pendiente baja:</b> límite inferior de clasificación.</li>
<li><b>Umbral pendiente media:</b> límite intermedio de clasificación.</li>
</ul>

<h3>Metodología</h3>
<ol>
<li>Cálculo de pendiente.</li>
<li>Reclasificación de pendiente.</li>
<li>Cálculo de distancia a costa.</li>
<li>Reclasificación de distancia.</li>
<li>Suma de variables.</li>
<li>Aplicación de máscara provincial.</li>
</ol>

<h3>Salida</h3>
<p>
Raster final del índice de erosión costera.
</p>

<h3>Autor</h3>
<p>
María Isabel Solano Sanz
</p>
"""

    def createInstance(self):
        return HerramientaErosionCostera()