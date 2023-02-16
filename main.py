import os
from time import sleep
import logging
import sqlite3 as sq
from datetime import datetime

from config import *

# Создаём папку для хранения логов
if not os.path.isdir("logs"):
    os.mkdir("logs")

# Получаем путь к папке логов
LOGS_PATH = os.path.join(os.path.dirname(__file__), 'logs')

# Константа секунды
SECOND = 1

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    filename=os.path.join(LOGS_PATH, 'logs.log'),
    # Можно указать "а", тогда будет добавлять
    # в конец файла, а не записывать заново
    filemode="w",
    format="%(asctime)s %(levelname)s %(message)s",
    encoding='utf-8'
)


def write_to_database(message):
    """Записывает сообщение в базу данных.
    :parameter message: Сообщение для записи в базу данных."""

    # Подключаемся к базе данных
    con = sq.connect(os.path.join(LOGS_PATH, 'kettle_logs.sqlite'))
    with con:
        # Создаем таблицу
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS messages(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message TEXT NOT NULL,
                date TEXT);
            """)
        # Записываем сообщение в таблицу
        con.execute(
            "INSERT INTO messages (message, date) VALUES(?, ?)",
            (message, str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        )


class Kettle:
    """Описывается класс Kettle.

    Описание работы чайника:

        1. В чайник можно налить воду с помощью метода pour_water().
            Если попытаться налить больше чем максимальный чайника,
            то будет выведено сообщение: "Слишком много воды".
        2. Воду в чайнике можно вскипятить с помощью метода turn_on.
            Если в чайнике есть вода, вызывается метод boiling().
            Если воды нет, то будет выведено сообщение: "Налейте в чайник воду."
            Во время кипения, каждую секунду будет выводиться
            сообщение о текущей температуре воды.
        3. После того как температура воды достигает максимальной,
            чайник автоматически останавливается, вызывается метод boiled().
            Он вызывает метод stop().
        4. Метод stop() означает, что чайником воспользовались,
            температура сбрасывается к комнатной,
            а количество воды становится равно 0
            и чайник можно либо выключить, либо им воспользоваться ещё раз.
        5. Чайник можно выключить с помощью метода turn_off().
            Вызов этого метода останавливает работу программы.

    Атрибуты
    --------
    max_temp : int
        максимальная температура воды в чайнике
    volume : float
        максимальное количество воды в чайнике (л.)
    boiling_time : int
        время закипания воды в чайнике (сек.)"""

    # Начальная температура воды
    START_TEMP = 24
    # Начальное количество воды в чайнике
    WATER_AMOUNT = 0.0

    def __init__(self, max_temp, volume, boiling_time):
        self.max_temp = max_temp
        self.volume = volume
        self.boiling_time = boiling_time

    @staticmethod
    def write_and_print_message(message):
        """Метод выводит сообщение в консоль,
        записывает в логи и базу данных.
        :parameter message: Сообщение для вывода и записи."""

        print(message)
        logging.info(message)
        write_to_database(message)

    def pour_water(self):
        """Метод добавления воды в чайник."""

        try:
            # Ввод количества налитой в чайник воды
            water_amount = float(
                input(f"Количество воды (не более {self.volume} л): ")
            )
            # Если вводимое число меньше нуля, вызываем ошибку
            if water_amount < 0:
                raise ValueError
            # Проверяем, что при попытке налить воду
            # не будет превышаться максимальный объём
            # чайника, если да выводим сообщение с предупреждением
            if self.WATER_AMOUNT + water_amount <= self.volume:
                self.WATER_AMOUNT += water_amount
                message = f"В чайнике {self.WATER_AMOUNT:2.1f} л воды."
                self.write_and_print_message(message)
            else:
                print("Слишком много воды.")
        # Если ввод строка или меньше нуля,
        # выводим сообщение с предупреждением и записываем в лог
        except Exception as e:
            print("Количество воды должно быть положительным числом.")
            logging.error(f"Количество воды должно "
                          f"быть положительным числом. "
                          f"Ошибка: {e}")

    def turn_on(self):
        """Метод включения чайника."""

        # Если в чайнике нет воды, выводим сообщение
        # если есть, то вызываем метод кипячения воды
        if self.WATER_AMOUNT == 0:
            print("Налейте в чайник воду.")
        else:
            message = "Чайник включен."
            self.write_and_print_message(message)
            # Вызываем метод кипячения воды
            self.boiling()

    def turn_off(self):
        """Метод выключения чайника."""

        message = "Чайник выключен."
        self.write_and_print_message(message)

    def boiling(self):
        """Метод закипания воды в чайнике."""

        # Находим разницу температур
        temp_diff = self.max_temp - self.START_TEMP
        # Пока температура воды не стала больше максимальной кипятим воду
        while self.START_TEMP < self.max_temp:
            message = f"Температура: {self.START_TEMP:2.1f}"
            self.write_and_print_message(message)
            self.START_TEMP += temp_diff / self.boiling_time
            sleep(SECOND)

        # Когда вода закипела вызываем метод окончания кипения
        self.boiled()

    def boiled(self):
        """Метод остановки кипения чайника."""

        message = "Чайник вскипел."
        self.write_and_print_message(message)
        # Вызываем метод завершения работы чайника
        self.stop()

    def stop(self):
        """Метод завершения работы чайника."""

        # Устанавливаем начальные значения
        self.START_TEMP = 24
        self.WATER_AMOUNT = 0.0
        message = "Чайник использован. Вода израсходована."
        self.write_and_print_message(message)


if __name__ == "__main__":
    """Запускаем программу."""

    # Инициализируем экземпляр класса с параметрами
    # MAX_TEMP - максимальная температура воды
    # VOLUME - максимальное количество воды в чайнике
    # BOILING_TIME - время закипания воды в чайнике
    kettle = Kettle(MAX_TEMP, VOLUME, BOILING_TIME)

    # Словарь команд. Формата <команда>: <метод чайника>
    commands = {
        "1": kettle.pour_water,
        "2": kettle.turn_on,
        "3": kettle.turn_off,
    }

    cmd = None

    try:
        # Пока не введена команда выключения чайника, просим выбрать действие
        while cmd != "3":
            cmd = input(
                "Введите команду. 1 - налить воду, "
                "2 - вскипятить, 3 - выключить: "
            )
            # Если команда есть в списке, вызываем метод
            if cmd in commands:
                commands[cmd]()
    # Если программа была завершена принудительно, выключаем чайник
    except KeyboardInterrupt:
        kettle.turn_off()
