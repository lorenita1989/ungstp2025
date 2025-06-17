# capa de servicio/lógica de negocio

from app.layers.utilities.card import Card
from ..transport import transport
from ...config import config
from ..persistence import repositories
#from ..utilities import translator
from ..utilities import *
from django.contrib.auth import get_user

import requests


# función que devuelve un listado de cards. Cada card representa una imagen de la API de Pokemon
def getAllImages():
    # debe ejecutar los siguientes pasos:
    # 1) traer un listado de imágenes crudas desde la API (ver transport.py)
    # 2) convertir cada img. en una card.
    # 3) añadirlas a un nuevo listado que, finalmente, se retornará con todas las card encontradas.
    #pass
    lista_imagenes=[]
    lista_card=[]
    
    # maximo de lista de imagenes a consultar, por eemplo MAX = 30
    itemsmaximos=5
    
    # punto 1, cargar lista imagenes crudas, segun el maximo soictado (en este caso 30)    
    for id in range(1,itemsmaximos):
        peticion=requests.get(config.STUDENTS_REST_API_URL+ str(id))
        
        if not peticion.ok:
            print(f"[services.py]: error al obtener datos para el id: {id}, continua con el siguiente")
            continue

        raw_data = peticion.json()

        if 'front_default' in raw_data['sprites'] and raw_data['sprites']['front_default'] != 'Not found.':
            #print(f"[services.py]: Pokémon con id {id} encontrado. se agrega a la lista")
            lista_imagenes.append(raw_data['sprites']['front_default'])
    
    # Punto 2: generamos el objeto CARD - con cada Pokemon encontrado
    # segun la definicion de objeto CARD en UTILITIES,cargamos los paramentros de la clase
            nombre=raw_data['name']
            altura=int(raw_data['height'])
            base=int(raw_data['base_experience'])
            peso=int(raw_data['weight'])
            imgurl=raw_data['sprites']['front_default']
            idPokemon=int(raw_data['id'])
            usuario=None
            
            lista_tipos=[]
            for idTipo in range(0,len(raw_data['types'])):
                auxTipos=raw_data['types'][idTipo]['type']['name']
                lista_tipos.append(auxTipos)
            
            #CARD_PEKEMON
            
            CARD_PEKEMON=Card(nombre,int(altura),int(base),int(peso),imgurl,lista_tipos,usuario,int(idPokemon))
            
    
    # Punto 3:  guarda en lista card
            lista_card.append(CARD_PEKEMON)
    
    return lista_card

# función que filtra según el nombre del pokemon.
def filterByCharacter(name):
    filtered_cards = []

    for card in getAllImages():
        # debe verificar si el name está contenido en el nombre de la card, antes de agregarlo al listado de filtered_cards.
        if card.__getNamePokemon__(name):
            filtered_cards.append(card)

    return filtered_cards

# función que filtra las cards según su tipo.
def filterByType(type_filter):
    filtered_cards = []

    for card in getAllImages():
        # debe verificar si la casa de la card coincide con la recibida por parámetro. Si es así, se añade al listado de filtered_cards.
        
        if card.__getTypePokemon__(type_filter):
            filtered_cards.append(card)

    return filtered_cards

# añadir favoritos (usado desde el template 'home.html')
def saveFavourite(request):
    fav = '' # transformamos un request en una Card (ver translator.py)
    fav.user = get_user(request) # le asignamos el usuario correspondiente.

    return repositories.save_favourite(fav) # lo guardamos en la BD.

# usados desde el template 'favourites.html'
def getAllFavourites(request):
    if not request.user.is_authenticated:
        return []
    else:
        user = get_user(request)

        favourite_list = [] # buscamos desde el repositories.py TODOS Los favoritos del usuario (variable 'user').
        mapped_favourites = []

        for favourite in favourite_list:
            card = '' # convertimos cada favorito en una Card, y lo almacenamos en el listado de mapped_favourites que luego se retorna.
            mapped_favourites.append(card)

        return mapped_favourites

def deleteFavourite(request):
    favId = request.POST.get('id')
    return repositories.delete_favourite(favId) # borramos un favorito por su ID

#obtenemos de TYPE_ID_MAP el id correspondiente a un tipo segun su nombre
def get_type_icon_url_by_name(type_name):
    type_id = config.TYPE_ID_MAP.get(type_name.lower())
    if not type_id:
        return None
    return transport.get_type_icon_url_by_id(type_id)