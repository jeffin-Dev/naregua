from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from model import Barbearia

# Inicializar o geocodificador
geolocator = Nominatim(user_agent="wuwigEZtJAkea4q4aiQdP9s2YFHza389EITd-oLdCTI")

# Função para obter coordenadas a partir de um endereço
def get_coordinates(address):
    try:
        # Geocode para obter a localização do endereço
        location = geolocator.geocode(address, timeout=10)
        
        # Verificar se a localização foi encontrada
        if location:
            address = location.address
            return location
        else:
            print(f"Endereço não encontrado: {address}")
            return None
    except Exception as e:
        # Log de erro se ocorrer um problema durante a geocodificação
        print(f"Erro ao obter coordenadas para o endereço {address}: {e}")
        return None


def find_nearby_establishments(user_address, establishment_addresses, initial_radius_km=2.0, max_radius_km=7.0, radius_step_km=3.5):
    # Obter as coordenadas do endereço do usuário
    user_location = get_coordinates(user_address)
    print(f"Coordenadas do usuário: {user_location}")
    
    # Verificar se as coordenadas do usuário foram encontradas
    if user_location is None:
        print("Endereço do usuário não encontrado")
        return []

    nearby_establishments = []
    current_radius_km = initial_radius_km
    
    # Iterar até atingir o raio máximo ou encontrar estabelecimentos
    while current_radius_km <= max_radius_km and not nearby_establishments:
        print(f"Procurando barbearias em um raio de {current_radius_km} km")
        for establishment_address in establishment_addresses:
            # Obter as coordenadas do endereço do estabelecimento
            establishment_location = get_coordinates(establishment_address)
            print(f"Coordenadas da barbearia: {establishment_location}")
            if establishment_location:
                # Calcular a distância entre o usuário e o estabelecimento
                distance = geodesic(
                    (user_location.latitude, user_location.longitude), 
                    (establishment_location.latitude, establishment_location.longitude)
                ).kilometers
                print(f"Distância calculada: {distance} km")
                # Verificar se a distância está dentro do raio atual
                if distance <= current_radius_km:
                    nearby_establishments.append({
                        "address": establishment_address,
                        "distance_km": distance
                    })
        # Aumentar o raio de busca
        current_radius_km += radius_step_km

    # Verificar se algum estabelecimento foi encontrado
    if not nearby_establishments:
        print(f"Nenhuma barbearia encontrada em um raio de até {max_radius_km} km.")
    else:
        # Opcional: ordenar os estabelecimentos encontrados por distância
        nearby_establishments.sort(key=lambda x: x['distance_km'])
        print(f"Barbearias encontradas: {nearby_establishments}")

    return nearby_establishments


def obter_barbearia_e_distancia(barbearias, endereco):
    lista_barbearias_proximas = []
    lista_distancias_barbearia = []
    
    try:
        for barbearia in barbearias:
            
            # Encontrar barbearias dentro de um raio de 5 km
            barbearias_dentro_de_5_km = find_nearby_establishments(endereco, [barbearia.enderecoBarbearia])
            
            print("Estabelecimentos próximos:")
            
            for establish in barbearias_dentro_de_5_km:
                # Adicionar barbearias encontradas à lista de barbearias próximas
                barbearia_proxima = Barbearia.query.filter_by(enderecoBarbearia=establish['address']).first()
                if barbearia_proxima:
                    lista_barbearias_proximas.append(barbearia_proxima)
                    print(f"Barbearia encontrada: {barbearia_proxima.nomeBarbearia} - Endereço: {establish['address']} - Distância: {establish['distance_km']:.2f} km")
                
                    # Adicionar distância à lista de distâncias
                    distancia = "{:.2f}".format(establish['distance_km'])
                    lista_distancias_barbearia.append(distancia)
            
        # Verificar se nenhuma barbearia foi encontrada
        if not lista_barbearias_proximas:
            print('Nenhuma barbearia encontrada no raio de quilometragem.')

    except Exception as e:
        print(e)
        
    # Combinar barbearias e distâncias em uma lista de tuplas
    barbearias_e_distancias = [
        (barbearia_proxima, distancia_proxima) 
        for barbearia_proxima, distancia_proxima in zip(lista_barbearias_proximas, lista_distancias_barbearia)
    ]
    
    print(f"Barbearias e distâncias combinadas: {barbearias_e_distancias}")
    
    return barbearias_e_distancias

