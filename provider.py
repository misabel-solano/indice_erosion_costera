from qgis.core import QgsProcessingProvider
from qgis.PyQt.QtGui import QIcon
import os

from .algoritmo_erosion_costera import HerramientaErosionCostera


class IndiceErosionCosteraProvider(QgsProcessingProvider):

    def loadAlgorithms(self):
        self.addAlgorithm(HerramientaErosionCostera())

    def id(self):
        return "erosion_costera"

    def name(self):
        return "TFM SIG Codigo Abierto"

    def longName(self):
        return self.name()

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(__file__), "icon.png"))