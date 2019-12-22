import logging

import matplotlib.animation as animation
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def save_animation(filename, particles, num_iter, step):
    # создаем рисунок
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.set_xlim((-1, 1))
    ax.set_ylim((-10, 5))

    ax.set_xlabel('x, м')
    ax.set_ylabel('y, м')

    lines = [ax.plot([], [], color='r', linestyle='', marker='o')[0] for _ in particles]

    # инициализация линий для анимации
    def init():
        for line in lines:
            line.set_data([], [])
        return lines

    # обновлении линий на каждой итерации
    def update(frame_num):
        logger.debug('Рисуем кадр %s / %s', frame_num, num_iter)
        ax.set_title('{}, час'.format(frame_num * step // 3600))

        for particle, line in zip(particles, lines):
            x, y = particle.x, particle.y(frame_num * step)
            line.set_data(x, y)
        return lines

    # создадим и сохраним анимацию
    ani = animation.FuncAnimation(
        fig,
        update,
        frames=num_iter - 1,
        init_func=init,
        interval=100,
        blit=True,
    )
    ani.save(filename, writer=animation.FFMpegFileWriter(bitrate=-1))
    logger.debug('Создан файл %s' % filename)


def save_csv(filename, particles):
    import csv

    with open(filename, mode='w') as f:
        writer = csv.writer(f, delimiter=',')

        writer.writerow(['particle', 'velocity'])
        for i, particle in enumerate(particles):
            writer.writerow([i, particle.velocity])
    logger.debug('Создан файл %s' % filename)
