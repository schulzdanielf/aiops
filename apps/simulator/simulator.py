import requests
import random
import time

API_URL = "http://app-filmes-service:5000/movies"

def make_request():
    # Define a distribuição das requisições: 70% rápidas, 20% lentas, 10% erros
    request_type = random.choices(
        ["fast", "slow", "error"],
        weights=[80, 10, 10],  # Pesos correspondentes
        k=1  # Número de elementos a serem escolhidos
    )[0]  # Retorna o primeiro (e único) elemento da lista

    if request_type == "fast":
        response = requests.get(API_URL + '?id=1081397')
        print(f"Fast request: {response.status_code}")
    elif request_type == "slow":
        response = requests.get(API_URL + '?genero=Drama')
        print(f"Slow request: {response.status_code}")
    elif request_type == "error":
        response = requests.get(API_URL + "/nonexistent")  # Endpoint inexistente
        print(f"Error request: {response.status_code}")

# Loop para simular as requisições
while True:
    make_request()
    time.sleep(random.uniform(0, 1))