from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from sympy.physics.quantum.circuitplot import matplotlib

matplotlib.use('Qt5Agg')


class MplCanvas(FigureCanvasQTAgg):

    # TODO: figure out why this doesn't work when fig is not named
    # TODO: figure out Python *args
    def __init__(self, parent=None, fig=None, width=5, height=4, dpi=100):
        super(MplCanvas, self).__init__(fig)
