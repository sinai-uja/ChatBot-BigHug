# Librerias
from pymongo import MongoClient # Librería MongoDB para la conexión con la base de datos
import pandas as pd             # Librería Pandas para la lectura de los ficheros .csv
import os
from data import *              # Importar data
from Mensajes import *          # Mensajes de la batería

client = MongoClient()          # Cliente MongoDB

###########################################################
# Insertar datos de los usuarios YA EVALUADOS
df = pd.read_csv('Consentimiento menores.csv')
df = df.fillna("")
db_data = client['data']
lis = []
cont = 0
for index, row in df.iterrows(): 
    arr = []
    if row['trastorno'] != "TRIAJE":
        # Es sano en todas
        if row['codigo'] == "":
            for cont in range(0,MAX_PATOLOGIAS+2):
                arr.append({'id_patologia':cont, 'tipo':'sanos',"acceso":'entrevista'})
        else:
            lista_trastornos = row['codigo'].split(',')
            for cont in range(0,MAX_PATOLOGIAS+2):
                if str(cont) in lista_trastornos:
                    arr.append({'id_patologia':cont, 'tipo':'indicados',"acceso":'entrevista'})
                else:
                    arr.append({'id_patologia':cont, 'tipo':'sanos',"acceso":'entrevista'})
    db_data.usuarios.insert_one({'alias':row['alias'],'estado':row['estado'],'temas':[],'patologias':arr})
    cont+=1
    if row['alias'] not in lis:
        lis.append(row['alias'])
    else:
        print('ALIAS REPETIDO: ',row['alias'])

###########################################################
# Insertar batería de preguntas por patología
carpeta = os.listdir("Mensajes")
lista = list(ficheros_dict.values())
for fichero in carpeta:
    sano = []
    ind = []
    print("Insertando batería del fichero "+ fichero + "...")
    df = pd.read_csv("./Mensajes/"+fichero)
    fich = fichero.split('.')[0]
    for index, row in df.iterrows(): 
        if row['Aplica a sano'] == 'x':
            if row['Aplica a indicada'] == 'x':
                sano.append(row["Texto del mensaje"])
                ind.append(row["Texto del mensaje"])
            else:
                sano.append(row["Texto del mensaje"])
        else: #if row['Aplica  a indicada'] == 'x':
            ind.append(row["Texto del mensaje"])
    db_data.bateria.insert_one({'id':lista.index(fich), 'sanos':sano, 'indicados': ind})