import math

from qgis.core import QgsProcessingLayerPostProcessorInterface


class LayerRenamer(QgsProcessingLayerPostProcessorInterface):

    def __init__(self, layer_name: str):
        self.name = layer_name
        super().__init__()

    def postProcessLayer(self, layer, context, feedback):
        layer.setName(self.name)


def round_down_float_to_3_decimals(num: float) -> float:
    return math.floor(num * 1000) / 1000


def round_down_float_to_5_decimals(num: float) -> float:
    return math.floor(num * 100000) / 100000
