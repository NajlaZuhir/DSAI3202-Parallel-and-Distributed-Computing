# celery_app.py

from celery import Celery
from genetic_algorithms_functions import calculate_fitness
import pandas as pd


app = Celery('shortest_route',
             broker='redis://localhost:6379/0',
             backend='redis://localhost:6379/0')  # Specify the result backend

app.conf.update(
    task_serializer='msgpack',
    result_serializer='msgpack',
    accept_content=['msgpack', 'application/json'],
)

@app.task(bind=True)
def calculate_fitness_async(self, routes):
    if not hasattr(self, 'distance_matrix'):
        self.distance_matrix = pd.read_csv('city_distances.csv').values
    return [calculate_fitness(route, self.distance_matrix) for route in routes]




