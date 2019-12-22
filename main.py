import os

import logging

from biofouling_task.save import save_animation, save_csv

# Настроим логгирование
logger = logging.getLogger('biofouling_task')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

logging.getLogger("matplotlib").setLevel(logging.WARNING)

# Зададим константы
NUM_ITER = 10
STEP = 3600  # с

g = 978  # см/с2
NU = 17890  # см2/с
RO_W = 1.005  # г/см3
RO_F = 1.388  # г/см3
RO_0 = 0.967  # г/см3
R_0 = 0.25  # см


class Particle:
    def __init__(self, ro=RO_0, r=R_0, x=0.0):
        self.ro_0 = ro
        self.r_0 = r
        self.x = x
        d = r * 2

        # плотность частицы
        # k = self.r_0 * (((RO_F - self.ro_0) / (RO_F - RO_W)) ** (1 / 3) - 1)
        k = 1.01
        kk = (self.r_0 ** 3) / ((self.r_0 + k) ** 3)
        ro_sphere = self.ro_0 * kk + RO_F * (1 - kk)
        # безразмерный диаметр частицы
        D = d * ((ro_sphere - RO_W) * g / RO_W / NU ** 2) ** (1 / 3)
        # скорость осаждения
        self.velocity = NU / d * D ** 3 * (38.1 + 0.93 * D ** (12 / 7)) ** (-7 / 8)
        logger.debug(f'Создаем частицу: '
                     f'ro_0 {self.ro_0}, '
                     f'k {k}, ro_sphere {ro_sphere}, '
                     f'D {D}, velocity {self.velocity}')

    def y(self, time):
        return - self.velocity * time


def main():
    logger.debug(
        f'\n'
        f'#############################\n'
        f'Параметры:\n'
        f'  Число итераций:\t{NUM_ITER}\n'
        f'  Шаг итерации, сек:\t{STEP}\n'
        f'#############################'
    )

    # тут можно добвлять частицы с разными параметрами, x это координата по оси x
    particles = [Particle(ro=0.967, r=0.25, x=0),
                 Particle(ro=0.9, r=0.29, x=0.1),
                 Particle(ro=1.0, r=0.2, x=0.2),
                 ]

    logger.debug('Сохраняем анимацию')
    save_animation('result/out.mp4', particles, NUM_ITER, STEP)

    logger.debug('Сохраняем скорости в файл')
    save_csv('result/out.csv', particles)


if __name__ == '__main__':
    main()
