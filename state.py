import logging
import math
from collections import defaultdict

import numpy as np


logger = logging.getLogger('main.%s' % __name__)


def get_velocity(current_velocity, speed_params, W):
    """Возвращает скорость частицы"""
    assert current_velocity.shape[0] == speed_params.shape[0]
    velocity = (speed_params @ W.T + current_velocity) / (1 + speed_params)
    velocity *= 0.01  # переведем из см/с в м/с
    return velocity


def init_state(num_points, current_velocity_func, point_types,
               bounds=None, weights=None, random_state=None, **kwargs):
    """Инициализация состояния системы"""
    x_min, y_min, x_max, y_max = bounds
    x_delta = x_max - x_min
    xmin_, xmax_ = x_min + 0.2 * x_delta, x_min + 0.5 * x_delta
    y_delta = y_max - y_min
    ymin_, ymax_ = y_min + 0.4 * y_delta, y_min + 0.6 * y_delta
    n = np.ceil(np.sqrt(num_points)).astype(int)
    xm, ym = np.meshgrid(np.linspace(xmin_, xmax_, n), np.linspace(ymin_, ymax_, n))
    xy_init = np.vstack([xm.ravel(), ym.ravel()]).T
    random_state.shuffle(xy_init)  # перемешаем, чтобы точки чередовались по типу
    xy_init = xy_init[:num_points]  # отбросим лишние
    types_df = expand_types(point_types)
    speed_params = types_df.speed_param.values.reshape(-1, 1)
    types = types_df.index.values.reshape(-1, 1)
    velocity_init = get_velocity(current_velocity_func(xy_init), speed_params, weights)
    return np.hstack([xy_init, velocity_init, types])


def get_state(states, iteration, current_velocity_func, point_types, step, weights=None, **kwargs):
    """Возвращае текущее состояние по предыдущему"""
    state_prev = states[iteration - 1, :, :]
    xy_prev = state_prev[:, :2]
    velocity_prev = state_prev[:, 2:4]
    xy_cur = xy_prev + step * velocity_prev
    types = state_prev[:, 4].reshape(-1, 1)
    speed_params = expand_types(point_types, types).speed_param.values.reshape(-1, 1)
    velocity_cur = get_velocity(current_velocity_func(xy_cur), speed_params, weights)
    states_cur = np.hstack([xy_cur, velocity_cur, types])
    states[iteration, :, :] = states_cur
    return states


def run(init_state_func,
        num_iter,
        step,
        ):
    """ Запустим расчет"""
    # states - массив [NUM_ITER х NUM_PARTICLES х 5]
    # по последней оси размерностью 5 храним X, Y, Vx, Vy, point_type
    # точки расположены в виде прямоугольника

    num_points = point_types.number.sum()
    states = np.ones([num_iter, num_points, 5], dtype=float) * np.nan
    states[0, :, :] = init_state_func(
        num_points,
        current_velocity_func,
        point_types=point_types,
        **kwargs
    )
    for iteration in range(1, num_iter):
        logger.debug('> Итерация %d / %d', iteration, num_iter)
        states = get_state(
            states,
            iteration,
            current_velocity_func,
            point_types=point_types,
            step=step,
            **kwargs
        )
    return states
