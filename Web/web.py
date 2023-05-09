# pip install streamlit
# pip install pandas
# pip install pymongo==3.6
# pip install numpy
from PIL import Image
import numpy as np
import base64
import streamlit as st          # Librería para la creación de la web
from pymongo import MongoClient # Librería MongoDB para la conexión con la base de datos
import pandas as pd
from zmq import NULL             # Librería Pandas para la lectura de los ficheros .csv

######################################################################## VARIABLES
client = MongoClient()
db_data = client["data"]            # BBDD de datos
users_col = db_data["usuarios"]     # Colección de usuarios
bateria_col = db_data["bateria"]    # Colección de mensajes de bateria
db_msgs = client["msgs"]            # BBDD de mensajes

lista_total =[]
# Extraer el alias de todos los participantes con su chat id y su bot elegido
alias_list = users_col.find({},{'alias':1,'chat_id':1,'bot':1,'_id':0}) 
alias_chat = {}
alias_bot = {}
for cursor in alias_list:
    if len(cursor) == 3:
        alias_chat[cursor["alias"]] = cursor['chat_id']
        alias_bot[cursor["alias"]] = cursor["bot"]
    else:
        alias_chat[cursor["alias"]] = ""
        alias_bot[cursor["alias"]] = ""

# Construir fichero de ranking
dict = {'Alias':[], 'numpalabras':[],'Bot':[]}

for key,value in alias_chat.items():
    if value != "":
        #data = db_msgs.get_collection(value).aggregate([{"$facet": {'result': [],'total': [{"$group": { '_id': NULL,'title': { "$first": "total" },'num_words': { "$sum": "$palabras" }}}]}},{ "$project": { "total": 1}}])
        data = db_msgs.get_collection(value).aggregate([{"$group":{"_id" : "", "num_words": { "$sum": "$palabras" }}}])
        dict['Alias'].append(key)
        for x in data:
            dict['numpalabras'].append(x['num_words'])
        dict['Bot'].append(alias_bot[key])
    else:
        dict['Alias'].append(key)
        dict['numpalabras'].append(0)
        dict['Bot'].append("-")

df = pd.DataFrame(dict)
df.to_csv('./ranking.csv',index=False)

#####################################################################
## Página web
st.set_page_config(
    layout="centered", page_icon="🤗", page_title="Mejores amigos Big Hug"
)

hide_menu = """
<style>
    .css-18ni7ap.e8zbici2 {
        visibility:hidden;
    }
    footer{
        visibility:hidden;
    }
    .appview-container.css-1wrcr25.egzxvld4{
        background-color:rgba(255, 255, 255, 0.8);
        width: 1200px;
        margin-left: auto;
        margin-right: auto;
    }
    .stTabs.css-0.exp6ofz0 {
        background-color:white;
    }
</style>
"""

# Imagen de fondo
def add_bg_from_local(image_file):
    with open("./img/"+image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url(data:img/{"jpg"};base64,{encoded_string.decode()});
            background-size: cover
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
add_bg_from_local('fondo.jpg')

##########################################
# Cabezera
st.markdown(hide_menu,unsafe_allow_html=True)
col1, col2 = st.columns([1, 4])
with col1:
    st.markdown("[![Logo BigHug](https://bighug.ujaen.es/wp-content/uploads/2022/03/cropped-logo-bighug-e1651147660505.png)](https://bighug.ujaen.es/)")
with col2:
    st.header("Mejores amigos de Big Hug 🤗​")
    st.write("Esta página web muestra un ranking de los mejores amigos de los bots Ada, Hugo y Big. ¡Para ser el mejor amigo, debes conversar mucho con ellos y así ayudarles a entender las emociones humanas!")
    st.markdown('Interactúa con el bot **@Bot_Big_Hug** mediante la App de Telegram ¡Se su mejor amigo/a!')

##########################################
# Contenedor
with st.container():
    
    st.subheader("Ranking global de mejores amigos")

    df = pd.read_csv('./ranking.csv')
    df = df.sort_values(by=['numpalabras'], ascending=False).reset_index()
    df['Posición'] = np.arange(1, len(df)+1)

    alias_ = st.text_input("¡Busca rápidamente tu posición escribiendo tu alias!", "Alias...")
    if st.button('Buscar'):
        row = df.loc[df['Alias'] == alias_]
        if len(row) == 0:
            st.write('Ese alias no existe. Por favor, escribe bien tu alias.')
        else:
            pos = row['Posición'].values[0]
            bot = str(row['Bot'].values[0])
            if bot != "-":
                text = "¡Continua hablando con el bot **" + bot + "** para subir posiciones!"
                if pos in [1,2,3]:
                    text = "¡Lo estás haciendo increible! ¡**" + bot+ "** te considera uno de sus **mejores amigos**!"
                st.markdown('¡Hola, **'+str(alias_) + '**! Te encuentras en la posición número **'+ str(pos)+'**.' )
                
            else:
                text = "¡Empeza a charlar para subir posiciones!"
            st.markdown(text)


    col1, col2 = st.columns([2,1])

    with col1:
        image = Image.open('./img/bot1.png')
        st.write('\n\n\n\n\n\n')
        st.image(image,width=500)

    with col2:
        st.dataframe(df.set_index('Posición')[['Alias','Bot']],500,400)

##########################################
# TABS
st.subheader("¡Elige a tu bot y busca en qué posición estás!")
tab1, tab2, tab3 = st.tabs(["Ada", "Hugo", "Big"])
with tab1:
    st.title("Mejores amigos de Ada 👧​​")
    df_ada = df.loc[df['Bot'] == 'Ada'].sort_values(by=['numpalabras'],ascending=False).reset_index()
    df_ada['Posición'] = np.arange(1, len(df_ada)+1)
    st.table(df_ada.set_index('Posición')['Alias'])

with tab2:
    st.title("Mejores amigos de Hugo 🧑​​​")
    df_hugo = df.loc[df['Bot'] == 'Hugo'].sort_values(by=['numpalabras'],ascending=False).reset_index()
    df_hugo['Posición'] = np.arange(1, len(df_hugo)+1)
    st.table(df_hugo.set_index('Posición')['Alias'])

with tab3:
    st.title("Mejores amigos de Big ​🤖​​​")
    df_big = df.loc[df['Bot'] == 'Big'].sort_values(by=['numpalabras'],ascending=False).reset_index()
    df_big['Posición'] = np.arange(1, len(df_big)+1)
    st.table(df_big.set_index('Posición')['Alias'])
