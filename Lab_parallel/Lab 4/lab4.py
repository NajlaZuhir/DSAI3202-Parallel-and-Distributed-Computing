import random
import time

from queue import Queue
from threading import Thread
from threading import RLock
from threading import Condition

# create a global dictionaries for the latest and average temperatures
latest_temperatures = {}
average_temperatures = {}
counters = 3*[0]
latest_temperatures_lock = RLock()
condition = Condition()


def simulate_sensor(sensor_id: int = 0,
                    queue: Queue = Queue()):
    """
    Generate random temperature readings and put them in a dictionary.
    Parameters:
        - sensor_id (int): Default O. The id of the sensor.
        - queue (Queue): Default Queue(). The queue where to push the temperature values.
    """
    while True:
        global counters
        counters[sensor_id] += 1
        temperature_reading = random.randint(15, 40)
        queue.put((sensor_id, temperature_reading))
        with latest_temperatures_lock:
            latest_temperatures[sensor_id] = temperature_reading
        time.sleep(1)


def process_temperature(queue: Queue = Queue()):
    """
    Calculates the average temperature from the sensor readings.

    Parameters:
        - queue (Queue): default Queue(). A queue of tuples with sensors ans temperature readings.
    """
    while True:
        sensor_id, temperature = queue.get()
        average_temperatures[sensor_id] = \
            ((average_temperatures.get(sensor_id, 0)*(counters[sensor_id]-1) + temperature)) // counters[sensor_id]
        queue.task_done()
        with condition:
            condition.notify()  # Notify every time an average is updated


def initialize_display():
    """
    Initialize the display with fixed labels.
    """
    print("Current temperatures:")
    print("Latest Temperatures:", end='')
    for i in range(3):  # Assuming 3 sensors
        print(f" Sensor {i}: --°C", end='')
    print()  # Move to the next line
    for i in range(1, 4):
        print(f"Sensor {i} Average: ", end='')
        print(" " * 50, end='')  # Placeholder for bars
        print(" --°C")  # Placeholder for average temperature


def update_display():
    """
    Update the display for latest temperatures and the average_temperatures.
    """
    while True:
        with latest_temperatures_lock:
            print("\033[2;0H", end='')  # Move cursor to the start of the latest temperatures
            print("Latest Temperatures:", end='')
            for i in range(3):
                temp = latest_temperatures.get(i, '--')
                print(f" Sensor {i}: {temp}°C", end='')

        # Wait for the condition to update average_temperatures
        with condition:
            condition.wait(timeout=5)  # Wait for an average update or timeout after 5 seconds
            for i in range(1, 4):
                avg_temp = average_temperatures.get(i-1, '--')
                bars = '|' * int(avg_temp) if avg_temp != '--' else ''
                print(f"\033[{4+i};0H", end='')  # Move cursor to start of each average line
                print(f"Sensor {i} Average: {bars:<50} {avg_temp}°C")


if __name__ == "__main__":
    queue = Queue()
    sensors = [Thread(target=simulate_sensor, args=(i, queue)) for i in range(3)]
    for s in sensors:
        s.daemon = True
        s.start()

    processor_thread = Thread(target=process_temperature, args=(queue,), daemon=True)
    processor_thread.start()

    initialize_display()  # Set up the display layout once
    update_display_thread = Thread(target=update_display, daemon=True)
    update_display_thread.start()

    update_display_thread.join()  # Keep the main thread running
