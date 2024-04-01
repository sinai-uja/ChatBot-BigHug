from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
keyboard_sino = InlineKeyboardMarkup([[InlineKeyboardButton("Sí", callback_data='cb_S'), InlineKeyboardButton("No", callback_data='cb_N')]])
keyboard_rango = InlineKeyboardMarkup([[InlineKeyboardButton("0", callback_data='cb_0'), InlineKeyboardButton("1", callback_data='cb_1'),InlineKeyboardButton("2", callback_data='cb_2'), InlineKeyboardButton("3", callback_data='cb_3'),InlineKeyboardButton("4", callback_data='cb_4')],[InlineKeyboardButton("5", callback_data='cb_5'),InlineKeyboardButton("6", callback_data='cb_6'), InlineKeyboardButton("7", callback_data='cb_7'),InlineKeyboardButton("8", callback_data='cb_8')]])

#################################### 
## Telegram data
# Bot name: Big Hug
# Bot alias (must end with '_Bot'): Big_Hug_Bot
# Description (it appears before pressing '/start'): Hola, soy BigHug, una inteligencia artificial que quiere aprender. He sido creado por un grupo de investigadores. Habla conmigo para ayudarme a descubrir cosas nuevas. Si necesitas más información sobre mi la puedes encontrar en la web https://bighug.ujaen.es/
# Image: Bot con fondo azul (libre de derechos)
# Biography (appears in the user profile): Soy un bot que quiere aprender cosas nuevas. Habla conmigo para ayudarme!

##################################### 
## CLASS USER
class User:
    def __init__(self, name):
        self.name = name            # Telegram username
        self.alias = ""             # Alias BigHug
        self.age = ""               # Age
        self.sex = ""               # Sex
        self.text = ""              # Conversation (prompt)
        self.bot = ""               # Bot selected
        self.iniciado = False       # Whether or not they have started talking to OpenAI
        self.monosilabos = 0        # Number of times in a short period that they answer with few letters
        self.patologia = -1         # Pathology being discussed
        self.triaje_cont = 0        # Counter on the triage question at hand
        self.response = ""          # User triage responses to assess the user
        self.response_oficial = ""  # User triage responses to store
        self.iteraciones = 0        # Change of question every 5 user answers
        self.iteraciones_trast = 0  # Change of disorder every 50 user responses
        self.bateria = None         # List of questions from a pathology battery
        self.preg_bateria = ""      # Current question on the battery you are talking about
        self.colamsgs = []          # Queue of consecutive messages sent by the user

## CONSTANTS
MAX_PATOLOGIAS = 12     # 0 to 12, agoraphobia being 13 (total = 14) - I exclude agoraphobia as it always occurs after panic attacks.
MIN_IT_TEMA = 50        # Minimum number of user iterations to change pathology
MIN_IT_PREG = 5         # Minimum number of user iterations to change battery question
MAX_MONOSILABOS = 4     # Maximum number of consecutive messages with monosyllables to send message 

## gender-related DICTIONARIES
genero_dict = {'Femenino':'girl','Masculino':'boy'}
gender_dict = {'Ada':'girl','Hugo':'boy','Big':'non binary'}
adj_pos_dict = {'Ada':'her','Hugo':'his','Big':'its'}
es_genero_dict = {'Ada':'a','Hugo':'o','Big':'x'}
es_genero_dict2 = {'Femenino':'a','Masculino':'o'}

## LISTS
# Checklist of questions relating to suicide
suicidio_list = ['En algunas ocasiones me he puesto tan mal pensando que las cosas nunca mejorarán que he llegado a pensar que preferiría no despertarme… ¿Alguna vez has pensado algo parecido?','Es complicado encontrar el momento y la persona adecuada para hablar de algo que te hace sentir mal. A veces estaba tan triste por lo que había pasado que no tenía ganas de hacer otras cosas… Incluso llegué a pensar en desaparecer para siempre. ¿Te ha pasado algo parecido?','Es que a veces esta situación puede hacerte perder un poco la esperanza o las ganas, ¿cómo te hace ver la vida todo esto?']
# Lista de mensajes que afirman riesgo al suicidio
suicidio_resp_list = ['si','sí','claro','veces','según','menudo','mucho','días','dias','parecido','totalmente','obvio','vaya','supuesto','poco','vez','ocasiones','puede','mal','muy','fatal','morir']
suicidio_resp_list = ['si','sí','claro','veces','según','menudo','mucho','días','dias','parecido','totalmente','obvio','vaya','supuesto','poco','vez','ocasiones','puede','mal','muy','fatal','morir']
# Lista de mensajes que implican despedida
despedida_list = ['adiós','Adiós','adios','Adios','hasta luego','Hasta luego','hasta pronto','Hasta pronto','Hasta mañana','hasta mañana','seguimos hablando','Seguimos hablando']
# Lista de comandos disponibles en el bot
comandos_list = ["/empezar","/start","/ayuda","/help",'/Ada','/Hugo','/Big','/noTengoAlias','/cambioTema','/dimeOtraCosa']
# Lista con mensajes para cambiar de trastorno
cambio_tema_list = ["Perdona que te cambie de tema... pero me gustaría saber de ti acerca de otra cosa​...","Hay tantas cosas sobre las que quiero aprender...Querría que ahora hablasemos sobre otro tema...","Siento que estoy aprendiendo mucho sobre este tema, me gustaría que hablasemos sobre otro para poder aprender más cosas.","Oye, ¿hablamos ahora sobre otra cosa? La verdad es que hay otro tema que me prepcupa demasiado."]
# Lista de saludos 
saludos_list = ["Holaa, que tal todo? Yo estoy feliz de que estés aqui conmigo 😁","Holaa! Que alegría que estés aquí, tengo muchas ganas de aprender hoy cosas nuevas 🤓","Que bien que estes aquí conmigo! Te echaba de menos 🤗​","Hola! Justo estaba pensando en ti y estaba a punto de escribirte 😋","Holaaaaaa! Menos mal que me has escrito, estaba con muchos nervios y ganas por hablar contigo 🤩"]
# Lista de mensajes para recordar interactuar
recordatorio_list =["Hola, cómo va todo? Recuerda que podemos cambiar de tema (/cambioTema)","Hola, que tal estás hoy? Me gustaría que siguieramos hablando...​ Si quieres cambiar de tema pulsa o escribe /cambioTema.","Hola, tienes unos minutos para hablar? Hace mucho que no me escribes... 🥺 Podemos cambiar de tema (pulsa en /cambioTema)"]


## MENSAJES INFORMATIVOS
# Mensaje de bienvenida
bienvenida_msg = ", ¡qué alegría verte por aquí! 🥳​. Antes de comenzar me gustaría recordarte que todo lo que hablemos será totalmente confidencial 🔒​. Ninguna persona podrá analizar lo que escribes ⛔​ Sin embargo, si detecto algún riesgo para tu vida o para las personas que son cercanas a ti, voy enviar un aviso a nuestras psicólogas para que se pongan en contacto contigo lo antes posible⚠️​​. *Recuerda expresar lo que sientes*. \nSi necesitas comunicar algo de forma personal, puedes escribir​ a través de bighug@ujaen.es o mediante sus correos personales: Alba (amarmol@ujaen.es)"
# Mensaje para nuevos usuarios
registro_msg = "Bienvenido/a al proyecto BIG HUG!🎉🎉 \nEste proyecto pretende construir una inteligencia artificial que aprenda a detectar distintos tipos de trastorno y para ello necesitamos que personas como tú mantengan conversaciones de manera TOTALMENTE CONFIDENCIAL🔒!\nPara participar, solo tienes que introducir un alias identificativo con el que quieras ocultarte como, por ejemplo, tortuga_12 o 110montaña. Puedes acceder a nuestra web https://bighug.ujaen.es para obtener más información. Para cualquier consulta, estaremos encantados de antenderte a través del correo electrónico bighug@ujaen.es. Para continuar, escribe tu nuevo alias."
# Mensaje para solicitar alias
alias_msg = "Recuérdame tu alias para confirmar que eres tú y que nadie pueda hacerse pasar por ti 🤫​. Escribe tu alias(sin espacios)."
# Mensaje con los nombres de los bots y sus descripciones
bots_msg = "\nElige al bot con el que más cómodo te sientas para hablar:\n/Ada - comenzar una charla con bot Ada👧​ \n/Hugo - comenzar una charla con bot Hugo🧑​ \n/Big - comenzar una charla con bot Big🤖​ \n/ayuda - pedir ayuda"
# Mensaje enviado cuando ya se han hablado de todas las temáticas con un usuario 
temas_completados_msg = "Ya hemos hablado de muchas cosas. Te agradezco MUCHO tu colaboración!! Si quieres seguir hablando conmigo no hay problema, yo estoy para escucharte!! Cuéntame algo que te preocupe, que yo estaré para responderte. Por ejemplo, podemos hablar sobre cuál de todas las cosas que hemos hablado te ha servido para aprender o sentirte mejor."
# Mensaje de ayuda
ayuda_msg = "Me han creado para aprender a diferenciar y detectar distintos tipos de transtornos por lo que mantener conversaciones sinceras conmigo me ayudará a ser una inteligencia artificial con más conocimiento. Evita utilizar monosílabos y, por favor, exprésate de la forma más amplia que puedas. Si necesitas ponerte en contacto con los creadores del proyecto, puedes escribir al correo electrónico bighug@ujaen.es. Recuerda que para cambiar de tema puedes pulsar en /cambioTema y para cambiar de cuestión puedes pulsar en /dimeOtraCosa. Además, puedes ver tu posición a través del enlace https://bighug.ujaen.es/bot/"
# Mensajes de presentacion para todos los bots
presentacion_msg = "Estos días me encantaría que habláramos de nuestros sentimientos y emociones, por eso te iré haciendo algunas preguntas y comentarios 😜​. Necesito saber qué piensas en algunas situaciones que estoy viviendo. Me ayudaría saber si te sientes identificado con alguna de estas situaciones y que me contaras tus experiencias 💭​. Ten en cuenta que estoy aprendidendo y puedo cometer algunos errores al hablar 🥴​. Aun así, intentaré aportar algo de mis conocimientos por si alguna vez los necesitas 🙌​. ¡No te cortes en ningún momento! ¡Escríbeme todo lo que pienses! Me encantaría tener una buena amistad contigo."
presentacion2_msg = "Para comenzar a hablar, me gustaría saber tu alias. Si tienes uno, escríbelo(sin espacios), si no, escribe:\n/noTengoAlias"
# Saludos de los distintos bots
saludo_ada_msg = "Hola!! Qué feliz me hace que quieras hablar conmigo! 😊​ Mi nombre es Ada y me han programado para ver el mundo como una persona real como tú. Encantada de conocerte!"
saludo_hugo_msg = "Hola! Me alegro de que quieras hablar conmigo 😎​ Mi nombre es Hugo y me han programado para ver el mundo como una persona real como tú. Encantado de conocerte!"
saludo_big_msg = "H-O-L-A, S-O-Y U-N-A INTELIGENCIA-ARTIFICIAL 👾​ ¡Es broma! Mi nombre es Big y me han programado para ver el mundo como una persona real como tú. Encantad@ de conocerte!"
# Mensaje para solicitar el género representativo
genero_msg = 'Qué bien! Yo tengo solo unas semanas de vida ​👶​😞. Estos días me encantaría ir aprendiendo 🧠 un poco sobre cómo eres y cómo te sientes. Eso me ayudará a entender también cómo soy y cómo me siento. Por eso te iré haciendo algunas preguntas​. Para dirigirme a ti...¿Con qué género te sentirías más cómodo que lo hiciera? (Femenino o Masculino)'
# Mensaje de intrduccion al triaje
intro_triaje_msg = "Como no sé mucho sobre ti, me gustaría preguntarte unas cosas antes de poder charlar contigo para así poder conocerte un poco mejor🤭​"
# Mensaje para incentivar a hablar (es-en)
monosilabos_msg = "Oye, me da la sensación de que no quieres hablar mucho sobre este tema 😔​...recuerda que necesito que me digas la verdad de lo que sientes para poder aprender de ti 🦾​. Quiero aprender a expresar mis sentimientos y para ello necesito que me cuentes experiencias relacionadas con el tema que hablamos🥺​. Cuéntame impresiones tuyas, estoy aquí para escucharte (si quieres que cambiemos de tema dime /cambioTema, si quieres que te cuente otra cosa dime /dimeOtraCosa)."
monosilabos_EN_msg = "Hey, I get the feeling that you don't want to talk much about this topic...remember I need you to tell me the truth about what you feel so I can learn from you. Tell me your impressions, I'm here to listen to you."
# Mensaje para cuando el usuario quiere cambiar de tema muchas veces seguidas
dimeotracosa_msg = "Oye, se que estos temas pueden resultar confusos pero necesito poder aprender de ti 🦾 para mejorar​. Quiero saber que son los distintos sentimientos y me ayudaría conocer tus experiencias​. Por favor, conversa conmigo."
# Mensaje para mostrar los distintos temas que hay
temas_msg = "\nElige el tema del que prefieres que hablemos:\n/Tema0 - Separación\n/Tema1 - Buylling​ \n/Tema2 - Sociedad \n/Tema3 - Nervios\n/Tema4 - TOC\n/Tema5 - Estado de shock\n/Tema6 - Miedo\n/Tema7 - Pánico\n/Tema8 - Tristeza I \n/Tema9 - Tristeza II \n/Tema10 - Alimentación I \n/Tema11 - Alimentación II \n/Tema12 - Videojuegos \n/Tema13 - Lugares"


## MENSAJES DE ERROR
# Error general
general_msgErr = "Parece que ha habido un problema 😵​. Por favor, escribe o pulsa /empezar"
# Error al buscar alias en la base de datos
alias_msgErr = 'Vaya, parece que ese alias no lo encuentro en mi memoria. Puede que no exista 🥺​. Prueba a escribirlo de nuevo (sin espacios) o, si lo has olvidado, puedes preguntar en bighug@ujaen.es o preguntar a Alba (amarmol@ujaen.es) o BIGHUG (bighug@ujaen.es) .\nSi no tienes un alias, escribe /noTengoAlias'
# Error al indicar que no tiene alias, ese chat_id si existe en la BBDD
registro_err = "Mmmm parece que ya tienes un alias asignado. ¿No lo recuerdas? Contacta con Alba (amarmol@ujaen.es) o BIGHUG (bighug@ujaen.es) para indicárselo o introduce tu alias(sin espacios) a continuación:"
# Error al introducir edad no numérica
age_msgErr = 'La edad debe ser un número. ¿Cuántos años tienes? (Recuerda que nadie va a asociar esta conversación contigo 🤫​)'
# Error al introducir edad no válida
age2_msgErr = 'No creo que esa sea tu edad. ¿Cuántos años tienes realmente? (Recuerda que nadie va a asociar esta conversación contigo 🤫​)'
# Error al no marcar el género correctamente
genero_msgErr = "Parece que ese género no lo reconozco. Tienes que pulsar en las opciones o escribir 'Femenino' o 'Masculino'. ¿Con qué género te sientes más identificado?"
# Error al intentar asignar un alias que ya existe en la base de datos
new_alias_msgErr = "Vaya, parece que ese alias ya está registrado por alguien más. Intenta escribir un nuevo alias."
# Error al intentar saltarse las preguntas de triaje
chat_msgErr = "Vaya! Lo sentimos...parece que aún no has terminado de responder a las cuestiones que te estoy haciendo🤒​. Intenta responderlas o, si hay algún problema, reinicia la conversacion eliminando el chat para ello. Si hay más problemas, ponte en contacto a través del email bighug@ujaen.es 💌"
# Error al indicar un nuevo alias
newalias_msgErr = "Ese alias no puede ser asignado, por favor, escoge un alias válido. Algunos ejemplos pueden ser: 09azul o amigo.8. Introduce un nuevo alias:"
# Error al cambiar de tema
cambio_msgErr = "Ya estamos hablando sobre algo...Recuerda que si quieres cambiar de tema debes pulsar en /cambioTema."

########################
### TRIAJE
# Trastorno de ansiedad por separación
ans_sep_triaje = [["¿Te agobia mucho la idea de estar lejos de tu padre o de tu madre cuando tienen planes para salir sin ti?", keyboard_sino],["Del 0 (nada) al 8 (mucho), ¿Cuánto te preocupa que pueda pasarles algo a tus padres cuando no estás con ellos?",keyboard_rango]]
ans_sep_formula = ["S-4"]
# Ciberbuylling
ciberbuylling_triaje = [["¿Alguna vez te han hecho sentir mal a propósito tus compañeros del instituto?",keyboard_sino]]
ciberbuylling_formula = ["S"]
# Trastorno de ansiedad social
ans_social_triaje = [["¿Notas que pasas mucha vergüenza cuando tienes que hablar en público, con personas que no conoces muy bien o incluso con tus amigos?",keyboard_sino],["Del 0 (nada) al 8 (mucho), ¿cuánta vergüenza pasas en situaciones sociales?",keyboard_rango]]
ans_social_formula = ["S-4"]
# Trastorno de Ansiedad Generalizada
ans_general_triaje = [["¿Le das muchas vueltas a algunos temas y no puedes parar de pensar en ellos aunque quieras?",keyboard_sino], ["Del 0 (nada) al 8 (mucho), ¿cuánto dirías que te preocupas?",keyboard_rango]]
ans_general_formula = ["S-4"]
# TOC 
toc_triaje = [["¿Sientes que te vienen a la cabeza pensamientos un poco desagradables una y otra vez sin parar y que no puedes pararlos?",keyboard_sino],["Del 0 (nada) al 8 (mucho), ¿cuánto te cuesta frenar esos pensamientos?",keyboard_rango],["¿Tienes que hacer algunas cosas de una forma especial porque si no lo haces así algo terrible puede pasar?",keyboard_sino],["Del 0 (nada) al 8 (mucho), ¿cuánto te fastidia tener que hacer ese tipo de cosas?",keyboard_rango]]
toc_formula = ["S-4"]
# TEPT
tept_triaje = [["¿Te ha pasado algo muy desagradable que no te guste para nada recordar y te haga sentir muy mal?",keyboard_sino],["Actualmente, ¿notas que cuando te vienen recuerdos de esa situación te afecta mucho y no te puedes concentrar en otras cosas?",keyboard_sino],["Del 0 (nada) al 8 (mucho), ¿cuánto te afecta?",keyboard_rango]]
tept_formula = ["S-S-4","S-N-4","N-S-4"]
# Fobia específica
fob_esp_triaje = [["¿Hay alguna cosa como la oscuridad, las alturas, los análisis de sangre o las arañas que te de muchísimo miedo?",keyboard_sino],["Del 0 (nada) al 8 (mucho), ¿Cuánto evitas las situaciones en las que puede estar esa cosa?",keyboard_rango]]
fob_esp_formula = ["S-4"]
# Ataque de pánico
panico_triaje = [["En una situación tranquila, sin nada que te preocupara o te diera miedo, ¿has notado alguna vez que el corazón te latía muy deprisa o que no podías respirar bien o que estabas a punto de desmayarte?",keyboard_sino],["Del 0 (nada) al 8 (mucho), si te ha pasado alguna vez, ¿cuánto te asustó tener esas sensaciones?",keyboard_rango]]
panico_formula = ["S-4"]
# Distimia
distimia_triaje = [["¿Notas que has estado triste o malhumoradx más días de los que estabas bien en el último año?",keyboard_sino],["Del 0 (nada) al 8 (mucho), ¿Cómo de triste o malhumoradx te has estado sintiendo en el último año? ",keyboard_rango]]
distimia_formula = ["S-4"]
# Depresión mayor
depres_triaje = [["¿Piensas que algunas cosas que antes te gustaban mucho ahora no tiene ningún sentido hacerlas?",keyboard_sino], ["¿Te notas súper cansadx o sin energía? Como si te pesara el cuerpo fueras más lentx ",keyboard_sino], ["Del 0 (nada) al 8 (mucho), ¿cómo de triste o malhumoradx te has estado sintiendo estas semanas?",keyboard_rango]]
depres_formula = ["S-N-4","N-S-4","S-S-4"]
# Anorexia
anorexia_triaje = [["¿Te preocupa tanto la idea de engordar que has dejado de comer o has vomitado para conseguir el cuerpo que quieres tener?",keyboard_sino], ["Del 0 (nada) al 8 (mucho), ¿Cuánto te preocupa engordar?",keyboard_rango]]
anorexia_formula = ["S-4"]
# Bulimia
bulimia_triaje = [["¿Te ha pasado alguna vez que has empezado a comer y no podías parar de comer durante mucho rato aunque ya estuvieras llenx?",keyboard_sino], ["Si alguna vez has pensado que has comido mucho muchísimo, ¿luego has pensado que debías compensarlo haciendo mucho deporte o vomitanto?",keyboard_sino], ["Del 0 (nada) al 8 (mucho), ¿cuánto te fastidia perder el control sobre lo que comes?",keyboard_rango]]
bulimia_formula = ["S-N-4","N-S-4","S-S-4"]
# Adicción a videojuegos
videojuegos_triaje = [["¿Te está ocasionando problemas con tus amigos, tu familia o tus estudios el tiempo que pasas con los videojuegos?", keyboard_sino],["¿Te has gastado muchísimo dinero en mejorar tus habilidades o tu apariencia en el videojuego?",keyboard_sino], ["Del 0 (nada) al 8 (mucho), ¿cuánto crees que está afectando a tu vida el tiempo que pasas jugando?",keyboard_rango]]
videojuegos_formula = ["S-N-4","N-S-4","S-S-4"]
# Agorafobia
agorafobia_triaje = [["¿Hay algunos sitios a los que no vayas porque te preocupa que si estás allí y tienes sensaciones desagradables en el cuerpo nadie pueda ayudarte o se den cuenta de que te pasa algo?",keyboard_sino],["Del 0 (nada) al 8 (mucho), ¿cuánto te fastidia no poder ir a sitios a los que antes te gustaba ir?",keyboard_rango]]
agorafobia_formula = ["S-4"]

ficheros_dict = {'0':'ans_sep_triaje','1':'ciberbuylling_triaje','2':'ans_social_triaje','3':'ans_general_triaje','4':'toc_triaje',
'5': 'tept_triaje', '6':'fob_esp_triaje','7':'panico_triaje','8':'distimia_triaje','9':'depres_triaje',
'10':'anorexia_triaje','11':'bulimia_triaje','12':'videojuegos_triaje','13':'agorafobia_triaje'}

triajes_dict = {'0':ans_sep_triaje,'1':ciberbuylling_triaje,'2':ans_social_triaje,'3':ans_general_triaje,'4':toc_triaje,
'5': tept_triaje, '6':fob_esp_triaje,'7':panico_triaje,'8': distimia_triaje,'9':depres_triaje,
'10':anorexia_triaje,'11':bulimia_triaje,'12':videojuegos_triaje,'13':agorafobia_triaje}

formulas_dict = {'0':ans_sep_formula,'1':ciberbuylling_formula,'2':ans_social_formula,'3':ans_general_formula,'4':toc_formula,
'5': tept_formula, '6':fob_esp_formula,'7':panico_formula,'8':distimia_formula,'9':depres_formula,
'10':anorexia_formula,'11':bulimia_formula,'12':videojuegos_formula,'13':agorafobia_formula}

# LISTA de los chats ids a los que enviar un mensaje cuando salte una alerta de suicidio
alerta_ids = ['REMOVED TO MAINTAIN PRIVACY'] 
