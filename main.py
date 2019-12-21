import os

# os.environ['PROJ_LIB'] = '/home/etsu/miniconda2/envs/particles/share/proj'
os.environ['PROJ_LIB'] = 'C:\Anaconda\Library\share'
import logging
import pandas as pd
from scipy.interpolate import LinearNDInterpolator
from pyproj import transform

from particles.save import save_animation, save_csv
from particles.state import *
from particles.utils import transform_states, get_point_types, type_colors, Continent

# Настроим логгирование
logger = logging.getLogger('main')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

# Зададим константы
NUM_ITER = 24 * 4
STEP = 3600  # с
SEED = 42

g = 978  # см/с2
NU = 17890  # см2/с
RO_W = 1.005  # г/см3
RO_F = 1.388  # г/см3
RO_0 = 0.967  # г/см3
R_0 = 0.25  # см


class Particle:
    def __init__(self, ro, radius):
        self.ro_0 = ro
        self.r_0 = radius
        d = radius * 2

        # плотность частицы
        ro = self.r_0 * (((RO_F - self.ro_0) / (RO_F - RO_W)) ** (1 / 3) - 1)
        ro_sphere = (self.ro_0 - RO_F) * R_0 ** 3 / (self.r_0 + ro) ** 3 + RO_F
        # безразмерный диаметр частицы
        D = d * ((ro_sphere / RO_W - 1) * g / NU ** 2) ** (1 / 3)
        # скорость осаждения
        self.velocity = NU / d * D ** 3 * (38.1 + 0.93 * D ** (12 / 7)) ** (-7 / 8)

    def x(self, step):
        return self.velocity * step


def main():
    logger.debug(
        f'#############################\n'
        f'Параметры:\n'
        f'  Число итераций:\t{NUM_ITER}\n'
        f'  Шаг итерации, сек:\t{STEP}\n'
        f'#############################'.format(NUM_ITER, STEP)
    )



    logger.debug('Сохраняем анимацию')
    save_animation('out1.mp4', lonlat, current_velocity, states, point_types, NUM_ITER, STEP)

    logger.debug('Сохраняем результаты в файл')
    save_csv('out1.csv', states, point_types, bounds_lonlat)


if __name__ == '__main__':
    main()
