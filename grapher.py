import logging
import pygal
from pygal.style import Style

# Same as the default pygal style except with a white background.
PJ_STYLE = Style(
    background = '#FFF',
    plot_background = 'rgba(255, 255, 255, 1)',
    foreground = 'rgba(0, 0, 0, .87)',
    foreground_strong = 'rgba(0, 0, 0, 1)',
    foreground_subtle = 'rgba(0, 0, 0, .54)',
    opacity = '.7',
    opacity_hover = '.8',
    transition = '250ms ease-in',
    colors = ('#F44336', '#3F51B5', '#009688', '#FFC107', '#FF5722', '#9C27B0',
              '#03A9F4', '#8BC34A', '#FF9800', '#E91E63', '#2196F3', '#4CAF50',
              '#FFEB3B', '#673AB7', '#00BCD4', '#CDDC39', '#9E9E9E', '#607D8B')
)
GRAPHS_DIR = 'graphs/'

class Grapher:
    def __init__(self):
        self.graphs = []

    def create_graph(self):
        print('create_graph')