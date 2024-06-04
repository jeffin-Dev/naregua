from geopy.geocoders import Nominatim
from geopy.distance import geodesic

# Inicializar o geocodificador
geolocator = Nominatim(user_agent="wuwigEZtJAkea4q4aiQdP9s2YFHza389EITd-oLdCTI")

# Função para obter coordenadas a partir de um endereço
def get_coordinates(address):
    location = geolocator.geocode(address, timeout=10)
    return location

# Função para encontrar estabelecimentos próximos a partir de uma lista de endereços
def find_nearby_establishments(user_address, establishment_addresses, radius_km=5.0):
    user_location = get_coordinates(user_address)
    
    if user_location is None:
        print("Endereço do usuário não encontrado")
        return []

    nearby_establishments = []

    for establishment_address in establishment_addresses:
        establishment_location = get_coordinates(establishment_address)
        if establishment_location:
            # Calcular a distância apenas se a localização do estabelecimento for encontrada
            distance = geodesic((user_location.latitude, user_location.longitude), (establishment_location.latitude, establishment_location.longitude)).kilometers
            if distance <= radius_km:
                nearby_establishments.append({
                    "address": establishment_address,
                    "distance_km": distance
                })

    return nearby_establishments

# Endereço do usuário
user_address = "Rua Senador Teixeira da Costa, 180, Floramar, Belo Horizonte, Brasil"

# Lista de endereços dos estabelecimentos
establishment_addresses = [
    "Estação São Gabriel, Av. Cristiano Machado,5600,Vila Suzana,Belo Horizonte,MG",
    "Av. José Lopes Muradas,485,Floramar,BH,MG,Brasil",
    "R. José Clemente,Floramar,BH,MG,Brasil"
    # Adicione mais endereços conforme necessário
]

# Encontrar estabelecimentos próximos
nearby_establishments = find_nearby_establishments(user_address, establishment_addresses)

# Resultado
print("Estabelecimentos próximos:")
for establishment in nearby_establishments:
    print(f"Endereço: {establishment['address']} - Distância: {establishment['distance_km']:.2f} km")