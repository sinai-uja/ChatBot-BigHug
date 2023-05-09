######################################################################## LIBRERIAS
# pip install pyTelegramBotAPI
# pip install openai
# pip install deepl
# pip install pymongo
# pip install schedule

import re
import random
# Files
from config import * # Datos de configuracion
from utils import * # Funciones utiles
from data import * # Datos utiles
# Manejo de hilos
import schedule
from threading import Thread
from time import sleep
# Telegram bot
import telebot # Api de telegram
from telebot.apihelper import ApiTelegramException # Bot bloqueado por user
from telebot import types # Opciones de teclado
from telebot.types import ReplyKeyboardRemove # Eliminar keyboard generos
bot = telebot.TeleBot(API_TOKEN_BOT) # Instancia del bot de Telegram

# OPENAI
import os
import openai
openai.organization = None
openai.api_key = API_TOKEN_AI
# LOG
import logging
logging.basicConfig(filename='bot1.log',level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
# DEEPL
import deepl
translator = deepl.Translator(API_TOKEN_DEEPL)
# MONGODB
from datetime import datetime
from pymongo import MongoClient

######################################################################## CONSTANTES
ULTIMA_VEZ = { 'REMOVED TO MAINTAIN PRIVACY' }
SEGUNDOS_VEZ = {}

######################################################################## VARIABLES
client = MongoClient()
db_data = client["data"] # BBDD de datos
users_col = db_data["usuarios"] # Colección de usuarios
bateria_col = db_data["bateria"] # Colección de mensajes de bateria
db_msgs = client['msgs']   # BBDD de mensajes

user_dict = {}

######################################################################## OPENAI
def gpt(user):
    resp_orginal = openai.Completion.create(
        engine="text-davinci-002",
        prompt=user.text,
        temperature=0.9,
        max_tokens=170,
        top_p=1,
        frequency_penalty=0.7,
        presence_penalty=0.6,
        stop=[user.alias+":"]
    )
    resp_orginal = resp_orginal.choices[0].text
    resp_ = resp_orginal
    
    # Actualizar prompt
    user.text += resp_

    # Si la frase no está completa, se elimina la frase incompleta
    if resp_[len(resp_)-1] not in [".","!","?"]:
        data = re.split(r'[.!?]', resp_)
        x = len(data[-1])
        resp_ = resp_[:-x]

    # Si está completando la respuesta del usuario, se elimina
    if user.bot+":" in resp_: 
        index = resp_.index(user.bot+":")
        x = index + len(user.bot+":")
        logging.warning('PROMPT: %s, OPENAI ORIGINAL: %s OPENAI PROCESADA: %s', user.text, resp_orginal, resp_[x:])
        if resp_[x:] == "":
            logging.warning('PROMPT: %s, OPENAI ORIGINAL: %s OPENAI PROCESADA: %s #TEXTOVACIOOPENAI', user.text, resp_orginal, resp_[x:])
            return "vaya..."
        else:
            return translator.translate_text(resp_[x:], target_lang="ES").text 
    else:
        logging.warning('PROMPT: %s, OPENAI ORIGINAL: %s OPENAI PROCESADA: %s', user.text, resp_orginal, resp_)
        if resp_ == "":
            logging.warning('PROMPT: %s, OPENAI ORIGINAL: %s OPENAI PROCESADA: %s #TEXTOVACIOOPENAI', user.text, resp_orginal, resp_)
            return "vaya..."
        else:
            return translator.translate_text(resp_, target_lang="ES").text

##################################################################
##########################   HANDLE '/start','/empezar'
@bot.message_handler(commands=['start','empezar'])
def start_step(message):

    name = "usuario"
    random.seed(message.chat.id)
    logging.info('ChatID: %d - __USER__: %s #EMPEZAR', message.chat.id, message.text) ##
    
    user = User(name)
    user_dict[message.chat.id] = user
    user.collection_msgs = db_msgs[str(message.chat.id)]
    msg = "Hola, "+ name + bienvenida_msg

    # Comprobar si ya está ese chat_id en la BBDD
    if str(message.chat.id) in db_msgs.list_collection_names():

        # Comprobar si el usuario se registró adecuadamente 
        if users_col.count_documents({ "chat_id": str(message.chat.id)}) != 0:
            # Recoger datos del usuario almacenados en la BBDD
            doc_user = users_col.find_one({'chat_id':str(message.chat.id)})
            user.sex = doc_user['genero']
            user.alias = doc_user['alias']
            user.edad = doc_user['edad']
            user.bot = doc_user['bot']

            logging.info('ChatID: %d - __BOT__: %s #EMPEZAR', message.chat.id, msg+alias_msg) ##
            user.collection_msgs.insert_one({'time' : datetime.now(),'autor' :'bot','msg': [msg, alias_msg]})

            bot.send_message(message.chat.id, msg)
            bot.send_message(message.chat.id, alias_msg)
            bot.register_next_step_handler(message, alias_step)
            return

    # Sino --> Nuevo usuario / no tenemos sus datos
    user.collection_msgs = db_msgs[str(message.chat.id)]
    logging.info('ChatID: %d - __BOT__: %s #EMPEZAR', message.chat.id, msg+bots_msg) ##
    user.collection_msgs.insert_one({'time' : datetime.now(),'autor' : 'bot', 'msg': [msg,bots_msg]})

    bot.send_message(message.chat.id, msg)
    bot.send_message(message.chat.id, bots_msg)

##########################################################
##########################   HANDLE '/ayuda','/help'
@bot.message_handler(commands=['ayuda','help'])
def help_step(message):
    logging.info('ChatID: %d - __USER__: %s #AYUDA', message.chat.id, message.text) ##
    try:
        user = user_dict[message.chat.id]
        
        logging.info('ChatID: %d - __BOT__: %s #AYUDA', message.chat.id, ayuda_msg) ##
        user.collection_msgs.insert_one({'time' : datetime.now(),'autor' : 'user', 'msg' : 'ayuda'})
        user.collection_msgs.insert_one({'time' : datetime.now(),'autor' : 'bot','msgs' : ayuda_msg+bots_msg})

        bot.send_message(message.chat.id, ayuda_msg)
        if user.bot == "":
            bot.send_message(message.chat.id, bots_msg)
    except Exception as e:
        logging.warning('ChatID: %d ERROR %s #AYUDA', message.chat.id, e) ##
        bot.reply_to(message, general_msgErr)

##########################################################
##########################   HANDLE '/Ada','/Hugo','/Big'
@bot.message_handler(commands=['Ada','Hugo','Big'])
def bot_step(message):
    logging.info('ChatID: %d - __USER__: %s #BOTS', message.chat.id, message.text) ##
    try:
        user = user_dict[message.chat.id]
        if message.text == '/Ada':
            user.bot = 'Ada'
            saludo = saludo_ada_msg
        elif message.text == '/Hugo':
            user.bot = 'Hugo'
            saludo = saludo_hugo_msg
        elif message.text == '/Big':
            user.bot = 'Big'
            saludo = saludo_big_msg

        logging.info('ChatID: %d - __BOT__: %s #BOTS', message.chat.id, saludo+presentacion_msg+presentacion2_msg) ##
        user.collection_msgs.insert_one({'time' : datetime.now(),'autor' : 'user','msg':message.text})
        user.collection_msgs.insert_one({'time' : datetime.now(),'autor' : 'bot','msg':[saludo,presentacion_msg,presentacion2_msg]})

        bot.send_message(message.chat.id, saludo)
        bot.send_message(message.chat.id, presentacion_msg)
        bot.send_message(message.chat.id, presentacion2_msg)
        bot.register_next_step_handler(message, alias_step)
    except Exception as e:
        logging.warning('ChatID: %d ERROR %s #BOTS', message.chat.id, e) ##
        bot.reply_to(message, general_msgErr)

##########################################################
########################## GET ALIAS
def alias_step(message):
    logging.info('ChatID: %d - __USER__: %s #ALIAS', message.chat.id, message.text) ##
    try:
        user = user_dict[message.chat.id]
        user.collection_msgs.insert_one({'chat_id' : message.chat.id,'time' : datetime.now(),'autor' : 'user', 'msg' : message.text})
        
        # Si el usuario dice que no tiene alias 
        if message.text == '/noTengoAlias':
            # Si realmente no tiene alias
            if str(message.chat.id) not in db_msgs.list_collection_names():
                logging.info('ChatID: %d - __BOT__: %s #ALIAS', message.chat.id, registro_msg) ##
                user.collection_msgs.insert_one({'chat_id' : message.chat.id,'time' : datetime.now(),'autor' : 'bot','msg' : registro_msg})
                
                bot.send_message(message.chat.id, registro_msg)
                bot.register_next_step_handler(message, new_alias_step)
            # Si sí tiene alias COMPROBAR
            else:
                doc = users_col.find_one({ "chat_id": str(message.chat.id) },{'alias':1,"_id":0})
                # Tiene alias
                if doc != None:
                    logging.info('ChatID: %d - __BOT__: %s #ALIAS', message.chat.id, registro_err) ##
                    user.collection_msgs.insert_one({'chat_id' : message.chat.id,'time' : datetime.now(),'autor' : 'bot','msg' : registro_err})
                    
                    bot.send_message(message.chat.id, registro_err)
                    bot.register_next_step_handler(message, alias_step)
                else:
                    logging.info('ChatID: %d - __BOT__: %s #ALIAS', message.chat.id, registro_msg) ##
                    user.collection_msgs.insert_one({'chat_id' : message.chat.id,'time' : datetime.now(),'autor' : 'bot','msg' : registro_msg})
                    
                    bot.send_message(message.chat.id, registro_msg)
                    bot.register_next_step_handler(message, new_alias_step)

        else:
            alias = message.text

            # Comprobar si está en la BBDD
            doc = users_col.find({ "alias": str(alias) })
            # Si el alias no está en la BBDD
            if len(list(doc)) == 0:
                logging.warning('ChatID: %d - __BOT__: %s #ALIAS', message.chat.id, alias_msgErr) ##
                user.collection_msgs.insert_one({'chat_id' : message.chat.id,'time' : datetime.now(),'autor' : 'bot', 'msg' : alias_msgErr})
                
                bot.reply_to(message, alias_msgErr)
                bot.register_next_step_handler(message, alias_step)

            # Si el alias está en la BBDD
            else:
                user.alias = alias
                doc = users_col.find({ "alias": str(user.alias)})
                # Si ya está registrado
                if len(doc[0]) > 5:
                    inicio_conversacion(message,user)
                    return
                # Si es un nuevo usuario
                else:
                    # Si el usuario tiene alias - HAY QUE ASIGNARLE UN CHAT ID EN LA BBDD
                    users_col.update_one({'alias':user.alias},{"$set":{'chat_id':str(message.chat.id), 'bot':user.bot}})
                    age_msg = 'Genial! '+user.alias+'. ¿Y cuántos años tienes?'

                    logging.info('ChatID: %d - __BOT__: %s #ALIAS', message.chat.id, age_msg) ##
                    user.collection_msgs.insert_one({'chat_id' : message.chat.id,'time' : datetime.now(),'autor' : 'bot', 'msg' : age_msg})

                    bot.reply_to(message, age_msg)
                    bot.register_next_step_handler(message, age_step)
                return
    except Exception as e:
        logging.warning('ChatID: %d ERROR %s #ALIAS', message.chat.id, e) ##
        bot.reply_to(message, general_msgErr)

##########################################################
##########################   NEW ALIAS
def new_alias_step(message):
    logging.info('ChatID: %d - __USER__: %s #NEWALIAS', message.chat.id, message.text) ##

    try:
        user = user_dict[message.chat.id]
        user.collection_msgs.insert_one({'chat_id' : message.chat.id,'time' : datetime.now(),'autor' : 'user', 'msg' : message.text})
        alias = message.text.replace(" ", "")
        # Comprobar que el alias es válido 
        if alias in comandos_list:
            logging.warning('ChatID: %d - ALIAS NO VÁLIDO - Bot: %s #NEWALIAS', message.chat.id, newalias_msgErr) ##
            user.collection_msgs.insert_one({'chat_id' : message.chat.id,'time' : datetime.now(),'autor' : 'bot','msg' : newalias_msgErr})

            msg = bot.reply_to(message, newalias_msgErr)
            bot.register_next_step_handler(msg, new_alias_step)
            return
        # Comprobar si existe en la BBDD
        doc = users_col.find({ "alias": str(alias) })
        # Si el alias no existe en la BBDD, se inserta
        if len(list(doc)) == 0:
            user.alias = alias
            age_msg = "Genial! Tu nuevo alias es: "+str(user.alias)+". Utilízalo para hablar conmigo!😊​\nY...oye, ¿cuántos años tienes?"
            
            logging.info('ChatID: %d - __BOT__: %s #NEWALIAS', message.chat.id, age_msg) ##
            user.collection_msgs.insert_one({'chat_id' : message.chat.id,'time' : datetime.now(),'autor' : 'bot', 'msg' : age_msg})
            users_col.insert_one({'chat_id':str(message.chat.id),'alias' : str(user.alias), 'new':True, "bot":str(user.bot),"temas":[],"patologias":[]})
            
            bot.reply_to(message, age_msg)
            bot.register_next_step_handler(message, age_step)
        # Si el alias ya existe en la BBDD --> ERROR
        else:
            bot.reply_to(message, new_alias_msgErr)

            logging.warning('ChatID: %d - __BOT__: %s #NEWALIAS', message.chat.id, new_alias_msgErr) ##
            user.collection_msgs.insert_one({'chat_id' : message.chat.id,'time' : datetime.now(),'autor' : 'bot', 'msg' : new_alias_msgErr})
            
            bot.register_next_step_handler(message, new_alias_step)
            return

    except Exception as e:
        logging.warning('ChatID: %d ERROR %s #NEWALIAS', message.chat.id, e) ##
        bot.reply_to(message, general_msgErr)

##########################################################
##########################   GET AGE
def age_step(message):
    logging.info('ChatID: %d - __USER__: %s #AGE', message.chat.id, message.text) ##

    try:
        user = user_dict[message.chat.id]
        age = message.text
        user.collection_msgs.insert_one({'chat_id' : message.chat.id,'time' : datetime.now(),'autor' : 'user','msg' : message.text})
        
        # Si la edad introduida no es numérica
        if not age.isdigit():
            logging.warning('ChatID: %d - __BOT__: %s #AGE', message.chat.id, age_msgErr) ##
            user.collection_msgs.insert_one({'chat_id' : message.chat.id,'time' : datetime.now(),'autor' : 'bot','msg' : age_msgErr})

            msg = bot.reply_to(message, age_msgErr)
            bot.register_next_step_handler(msg, age_step)
            return

        # Si la edad introducida no es válida
        elif int(age) < 8 or int(age) > 30:
            logging.warning('ChatID: %d - __BOT__: %s #AGE', message.chat.id, age2_msgErr) ##
            user.collection_msgs.insert_one({'chat_id' : message.chat.id,'time' : datetime.now(),'autor' : 'bot', 'msg' : age2_msgErr})

            msg = bot.reply_to(message,age2_msgErr)
            bot.register_next_step_handler(msg, age_step)
            return

        user.age = age
        logging.info('ChatID: %d - __BOT__: %s #AGE', message.chat.id, genero_msg) ##
        user.collection_msgs.insert_one({'chat_id' : message.chat.id,'time' : datetime.now(),'autor' : 'bot', 'msg' : genero_msg})

        users_col.update_one({ "chat_id": str(message.chat.id) },{ "$set": {"edad":str(age)}})
        
        # Teclado para elección de género identificativo
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for gen in genero_dict:
            markup.add(gen)
        msg = bot.reply_to(message, genero_msg, reply_markup=markup)
        bot.register_next_step_handler(msg, gender_step)

    except Exception as e:
        logging.warning('ChatID: %d ERROR %s - #AGE', message.chat.id, e) ##
        bot.reply_to(message, general_msgErr)

##########################################################
##########################   GET GENDER
def gender_step(message):
    logging.info('ChatID: %d - __USER__: %s #GENDER', message.chat.id, message.text) ##
    try:
        sexo = message.text
        user = user_dict[message.chat.id]
        user.collection_msgs.insert_one({'chat_id' : message.chat.id,'time' : datetime.now(),'autor' : 'user', 'msg' : message.text})
        
        # Si ha pulsado correctamente las opciones
        if str(sexo) == "Masculino" or str(sexo) == "Femenino":
            user.sex = genero_dict[sexo]
            doc = users_col.update_one({ "alias": str(user.alias) },{ "$set": {"genero":user.sex}})
        # Si no ha pulsado las opciones
        else:
            logging.warning('ChatID: %d ERROR __BOT__: %s #GENDER', message.chat.id,genero_msgErr) ##
            user.collection_msgs.insert_one({'chat_id' : message.chat.id,'time' : datetime.now(),'autor' : 'bot', 'msg' : genero_msgErr})
            
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            for gen in genero_dict:
                markup.add(gen)
            msg = bot.reply_to(message, genero_msgErr, reply_markup=markup)
            bot.register_next_step_handler(msg, gender_step)
            return

        inicio_conversacion(message,user)
    except Exception as e:
        logging.warning('ChatID: %d ERROR %s #GENDER', message.chat.id, e) ##
        bot.reply_to(message, general_msgErr)

##########################################################
##########################   INICIO CONVERSACION
def inicio_conversacion(message,user, cambio = False, tema = -1):
    # Extraigo datos de los trastornos del usuario
    logging.info('ChatID: %d - __USER__: %s #INICIO', message.chat.id, message.text) ##
    doc_orig = users_col.find_one({ "alias": str(user.alias) },{"temas":1, "patologias":1})

    # Si ya se han hablado todos los temas
    h = len(doc_orig['temas'])
    if h >= MAX_PATOLOGIAS and tema == -1:
        logging.debug('ChatID: %d - INFO %s #INICIO', message.chat.id, 'Ya se han hablado todos los temas') ##
        cambio_step(message)
        return

    if tema == -1:
        # Sino, nueva conversación
        if user.patologia == 7: # Siempre 'agorafobia' después de 'ataque de pánico'
            user.patologia = 13
        else:
            user.patologia = random.randint(0, MAX_PATOLOGIAS)
            while user.patologia in doc_orig['temas'] or user.patologia == 13:
                user.patologia = random.randint(0,MAX_PATOLOGIAS)
    else:
        user.patologia = int(tema)
    logging.debug('ChatID: %d - TEMA PATOLOGIA: %i #INICIO', message.chat.id, user.patologia) ##
    if user.patologia not in doc_orig['temas']:
        doc = users_col.update_one({ "alias": str(user.alias) },{"$push": {"temas":user.patologia}})

    msg = ""
    # Saludo
    if h > 0 and cambio == False: 
        saludo = random.choice(saludos_list)
        msg += saludo
        bot.send_message(message.chat.id, saludo,reply_markup=ReplyKeyboardRemove())
    
    # Si el usuario no está evaluado y no tiene el triaje del tema
    if len(doc_orig['patologias']) < MAX_PATOLOGIAS+2 and user.patologia not in doc_orig['temas']:
        # Triaje
        logging.debug('ChatID: %d -  TRIAJE', message.chat.id) ##
        if cambio:
            cambio_tema_msg = random.choice(cambio_tema_list)
            bot.send_message(message.chat.id, cambio_tema_msg)
            msg += cambio_tema_msg
        else:
            msg += intro_triaje_msg
            bot.send_message(message.chat.id, intro_triaje_msg,reply_markup=ReplyKeyboardRemove())
        
        msg_triaje, rmarkup = triaje_conver(user)

        logging.info('ChatID: %d - __TRIAJE__: %s #INICIO', message.chat.id, msg +msg_triaje) ##
        user.collection_msgs.insert_one({'chat_id' : message.chat.id,'time' : datetime.now(),'autor' : 'bot-triaje', 'msg' : [msg, msg_triaje]})
        
        bot.send_message(message.chat.id,msg_triaje,reply_markup=rmarkup)
        
    # Si el usuario ya está evaluado
    else:
        user.text, inicio_msg = get_conver(user)
        patologias = users_col.find_one({'chat_id':str(message.chat.id)},{'patologias':1,'_id':0})['patologias']
        for dict in patologias:
            if dict['id_patologia'] == user.patologia:
                eval = dict['tipo']
                break

        user.bateria = bateria_col.find_one({'id':user.patologia},{eval:1,'_id':0})[eval]
        preg_es =  bateria(user)
        user.preg_bateria = preg_es # Conocimiento de la pregunta que se le ha hecho (para saber si debe saltar alerta)
        user.text += translator.translate_text(preg_es, target_lang="EN-US").text
        user.iniciado = True
        
        logging.info('ChatID: %d - __OPENAI__: %s', message.chat.id, inicio_msg + preg_es) ##
        user.collection_msgs.insert_one({'chat_id' : message.chat.id,'time' : datetime.now(),'autor' : 'bot-bateria', 'msg' : [inicio_msg,preg_es]})
        bot.send_message(message.chat.id, inicio_msg)
        bot.send_message(message.chat.id, preg_es)

##########################################################
##########################   HANDLE '/cambioTema'
@bot.message_handler(commands=['cambioTema'])
def cambio_step(message):
    logging.info('ChatID: %d - __USER__: %s #CAMBIO', message.chat.id, message.text) ##
    try:
        user = user_dict[message.chat.id]
        user.collection_msgs.insert_one({'chat_id':message.chat.id,'time':datetime.now(),'autor':'user','msg':message.text})
        user.iteraciones = 0
        user.monosilabos = 0
        logging.info('ChatID: %d - __BOT__: %s #CAMBIO', message.chat.id, temas_msg) ##
        user.collection_msgs.insert_one({'chat_id':message.chat.id,'time':datetime.now(),'autor':'bot','msg':temas_msg})
        bot.send_message(message.chat.id, temas_msg)
        bot.register_next_step_handler(message, temas_step)
    except Exception as e:
        logging.warning('ChatID: %d ERROR %s #CAMBIO', message.chat.id, e) ##
        bot.reply_to(message, general_msgErr)

##########################################################
def temas_step(message):
    logging.info('ChatID: %d - __USER__: %s #TEMAS', message.chat.id, message.text) ##
    try:
        user = user_dict[message.chat.id]
        user.collection_msgs.insert_one({'chat_id':message.chat.id,'time':datetime.now(),'autor':'user','msg':message.text})
        inicio_conversacion(message,user, True, message.text[5:])
    except Exception as e:
        logging.warning('ChatID: %d ERROR %s #TEMAS', message.chat.id, e) ##
        bot.reply_to(message, general_msgErr)

######################################## TRIAJE
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat = call.message.chat
    user = user_dict[chat.id]
    resp = call.data.split('_')[1]

    logging.info('ChatID: %d - __USER__: %s #TRIAJE', chat.id, call.message.text) ##
    user.collection_msgs.insert_one({'chat_id' : chat.id,'time' : datetime.now(),'autor' : 'user', 'msg' : resp, 'patologia':user.patologia})
    user.response_oficial += resp +" "
    if resp == 'S': # Sí
        user.response +='S-'
        bot.answer_callback_query(call.id, "Has marcado Sí")
        logging.info('ChatID: %d - __USER__ %s', chat.id, 'Sí') ##
    elif resp == 'N': # No
        user.response +='N-'
        bot.answer_callback_query(call.id, "Has marcado No")
        logging.info('ChatID: %d - __USER__ %s', chat.id, 'No') ##
    else:
        logging.info('ChatID: %d - __USER__ %s', chat.id, resp) ##
        if int(resp) >= 4:
            user.response +='4-'
        else:
            user.response += str(resp)
        bot.answer_callback_query(call.id, "Has marcado "+ str(resp))

    # Eliminar opciones
    bot.edit_message_reply_markup(chat.id,call.message.id)

    user.triaje_cont +=1
    data = triaje_conver(user)

    # Si hay más preguntas de triaje
    if data != None:
        logging.info('ChatID: %d - __BOT__: %s #TRIAJE', chat.id, data[0]) ##
        user.collection_msgs.insert_one({'chat_id' : chat.id,'time' : datetime.now(),'autor' : 'triaje', 'msg' : data[0]})
        bot.send_message(chat.id,data[0], reply_markup=data[1])
    
    # Si no hay más preguntas de triaje
    else:
        # Se calcula el estado con las formulas correspondientes
        user.triaje_cont = 0
        eval = triaje_eval(user.patologia,user.response[:-1])
        users_col.update_one({'alias':user.alias},{"$push":{'patologias':{'id_patologia':user.patologia,'tipo':eval,"acceso":'triaje',"respuesta":user.response_oficial}}})
        user.response = ""
        user.response_oficial = ""

        # Se inicia la conversacion con una pregunta aleatoria
        user.bateria = bateria_col.find_one({'id':user.patologia},{eval:1,'_id':0})[eval]
        user.text, inicio_msg = get_conver(user)
        bot.send_message(chat.id, inicio_msg)

        preg_es = bateria(user)
        user.preg_bateria = preg_es
        user.text += translator.translate_text(preg_es, target_lang="EN-US").text
        user.iniciado = True

        logging.info('ChatID: %d - __OPENAI__: %s #INICIO', chat.id, inicio_msg+preg_es) ##
        user.collection_msgs.insert_one({'chat_id':chat.id,'time':datetime.now(),'autor':'bot-ia-bateria','msg':[inicio_msg,preg_es]})
        bot.send_message(chat.id, preg_es)

        
##################################################
# RECORDATORIO cuando ha pasado 23 horas sin interactuar con el bot
def schedule_checker():
    while True:
        schedule.run_pending()
        sleep(900) # 15 minutos

def send():
    # Comprobar si hace 23 horas que el usuario no ha hablado con el bot
    logging.warning('ENVIO RECORDATORIO %s ',str(ULTIMA_VEZ)) ##
    for key, value in ULTIMA_VEZ.items():
        if abs(datetime.now().hour - value) == 0:
            logging.warning('ChatID: %d - ENVIO RECORDATORIO %s #TIME', key, value) ##
            msg = random.choice(recordatorio_list)
            if key in user_dict:
                logging.warning('ChatID: %d - ENVIO RECORDATORIO comprobar dic %s #TIME', key, user_dict) ##
                try:
                    bot.send_message(key, msg)
                except ApiTelegramException as e:
                    logging.warning('ChatID: %d - El usuario ha bloqueado al BOT: %s #ERROR ENVIO RECORDATORIO', key,e.description)
                except Exception as e:
                    logging.warning('ChatID: %d ERROR %s #ERROR ENVIO RECORDATORIO', key, e) ##

# Utiliza una función lambda para probar un mensaje. Si la lambda devuelve True, el mensaje es manejado por la función decorada. 
# Como queremos que todos los mensajes sean manejados por esta función, simplemente siempre devolvemos True.
@bot.message_handler(func=lambda m: True)
def echo_all(message):
    try:
        # El usuario intenta cambiar de tema de forma no correcta
        if message.text[:5] == "/Tema":
            bot.reply_to(message, cambio_msgErr)

        # Almacenar mensaje recibido
        user = user_dict[message.chat.id]
        user.colamsgs.append(message.text)

        # Cuando un chat determinado habla con el bot
        if message.chat.id == "REMOVED TO MAINTAIN PRIVACY":
            # Recordatorio por mensaje
            send()
        
        logging.info('ChatID: %d - __USER__: %s #CONVER', message.chat.id, message.text) ##

        # Actualizar la hora del último mensaje
        global ULTIMA_VEZ
        hora = datetime.now().hour
        if hora == 0:
            ULTIMA_VEZ[message.chat.id]  = 23
        else:
            ULTIMA_VEZ[message.chat.id] = hora - 1

        # Comprobar si el usuario ya no ha escrito más en 10 segundos
        global SEGUNDOS_VEZ
        SEGUNDOS_VEZ[message.chat.id] = datetime.now().second
        sleep(10)
        aux = datetime.now().second - 10
        if aux < 0: aux = aux + 60
        if SEGUNDOS_VEZ[message.chat.id] != aux:
            return

        # Analizar y almacenar la cola de mensajes recibidos
        for resp in user.colamsgs:
            palabras = resp.split(' ')
            user.collection_msgs.insert_one({'chat_id' : message.chat.id,'time' : datetime.now(),'autor' : 'user', 'msg' : resp, 'patologia':user.patologia, 'palabras':len(palabras)})
        resp = '. '.join(user.colamsgs)
        user.colamsgs.clear()
        user.iteraciones +=1
        
        # Si ha llegado aquí de forma adecuada
        if user.iniciado:
            
            # COMPROBACIÓN IDEACIÓN SUICIDA - ALERTA
            if user.preg_bateria in suicidio_list:
                for pal in palabras:
                    if pal.lower in suicidio_resp_list:
                        for id in alerta_ids:
                            bot.send_message(id, "ALERTA SUICIDIO \nChat id: "+ str(message.chat.id) + "\nAlias: " + str(user.alias) + "\nHora: " +str(datetime.now()) + "\nPregunta del bot:" + str(user.preg_bateria)+ "\nRespuesta del usuario: "+ str(resp))
                        #bot.send_message(436623886, "ALERTA SUICIDIO \nChat id: "+ str(message.chat.id) + "\nAlias: " + str(user.alias) + "\nHora: " +str(datetime.now()) + "\nPregunta del bot:" + str(user.preg_bateria)+ "\nRespuesta del usuario: "+ str(resp))
                        logging.info('ChatID: %d - #ALERTA SUICIDIO - Alias: %s', message.chat.id,str(user.alias)) ##
                        break

            # Número de veces seguidas que responde con poco texto
            user.monosilabos = user.monosilabos+1 if len(resp.split(' ')) < 4 else 0
            if (user.iteraciones > 5 and resp == "/dimeOtraCosa") or (user.monosilabos >= MAX_MONOSILABOS and resp == "/dimeOtraCosa"):
                user.iteraciones = 0
                user.monosilabos = 0
                user.iteraciones_trast +=5
                # Cambio de trastorno
                if user.iteraciones_trast >= 50 or len(user.bateria) == 0:
                    logging.info('ChatID: %d - CAMBIO DE TRASTORNO #CONVER', message.chat.id) ##
                    user.iteraciones_trast = 0
                    inicio_conversacion(message,user, True)
                    return
                else:
                    # Cambio de pregunta
                    respuesta = bateria(user)
                    user.preg_bateria = respuesta
                    user.text += user.alias+': '+translator.translate_text(resp, target_lang="EN-US").text +" "+ user.bot +': '+translator.translate_text(respuesta, target_lang="EN-US").text 
                    logging.info('ChatID: %d - __OPENAI__: %s #CONVER', message.chat.id, respuesta) ##
                    user.collection_msgs.insert_one({'chat_id' : message.chat.id,'time' : datetime.now(),'autor' : 'bateria', 'msg' : respuesta, 'patologia':user.patologia})
            else:
                # Si ha respondido X veces seguidas con poco texto
                if user.monosilabos == MAX_MONOSILABOS or resp =="/dimeOtraCosa" or resp in ["De nada", "de nada"]:
                    respuesta = monosilabos_msg
                    user.monosilabos = 0
                    if resp == "/dimeOtraCosa":
                        respuesta = dimeotracosa_msg
                    user.text += user.alias+': '+translator.translate_text(resp, target_lang="EN-US").text +" "+ user.bot +': '+monosilabos_EN_msg
                    logging.info('ChatID: %d - _Bot__: %s #CONVER', message.chat.id, respuesta) ##
                    user.collection_msgs.insert_one({'chat_id' : message.chat.id,'time' : datetime.now(),'autor' : 'bot', 'msg' : respuesta, 'patologia':user.patologia})
                else:
                    user.text += user.alias+': '+translator.translate_text(resp, target_lang="EN-US").text +" "+ user.bot +': '
                    respuesta = gpt(user)
                    if user.iteraciones % 5 == 0:
                        respuesta += " (si quieres que cambiemos de tema dime /cambioTema, si quieres que te cuente otra cosa dime /dimeOtraCosa, sino continua la conversación charlando conmigo)"
                    logging.info('ChatID: %d - __OPENAI__: %s #CONVER', message.chat.id, respuesta) ##
                    user.collection_msgs.insert_one({'chat_id' : message.chat.id,'time' : datetime.now(),'autor' : 'ia', 'msg' : respuesta, 'patologia':user.patologia})
        else:
            logging.warning('ChatID: %d - ERROR: El usuario no ha completado las preguntas antes de comenzar la conversación #CONVER', message.chat.id) ##
            respuesta = chat_msgErr
        respuesta = respuesta.replace("usted","tú")
        bot.send_message(message.chat.id, respuesta)
    except Exception as e:
        logging.warning('ChatID: %d - ERROR %s #CONVER', message.chat.id,e) ##
        bot.reply_to(message, 'Pulsa /empezar para comenzar a interactuar.')


bot.enable_save_next_step_handlers(delay=2)

bot.load_next_step_handlers()

#####################################################################
# MAIN 
if __name__ == '__main__':

    print('Iniciando el bot...')
    
    try:
        bot.infinity_polling()
    except Exception as e:
        logging.warning('ERROR %s #INFINITYPOLLING', e) ##
