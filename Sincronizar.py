import requests, json, codecs, sys

# VARIABLES API
URL_API = "https://api.itmplatform.com/"
EMPRESA_API = ""
USUARIO_API = ""
CLAVE_API = ""

# VARIABLES GLOBALES
token = ""
listaProyectos = []


### METODO QUE CONENCTA CON EL API, INICIA SESION Y DEVUELVE EL TOKEN DE ACCESO
def iniciar_sesion_api():
    url = URL_API + EMPRESA_API + "/login/" + USUARIO_API + "/" + CLAVE_API

    req = requests.get(url)

    if req.status_code == 200:
        json_body = req.json()
        token = json_body["Token"]
        print "login ok!"
    else:
        print req

    return token


### METODO QUE CONECTA CON EL API Y OBTIENE TODOS LOS PROYECTOS
def obtener_proyectos_api(token):

    if token == "":
        token = iniciar_sesion_api()
        
    url = URL_API + EMPRESA_API + "/projects/?Program.ProgramName=Prog. Transporte"
    headers = {"Token":token}

    req = requests.get(url, headers = headers)

    if req.status_code == 200:
       print "obtener proyectos api ok!"
       proyectos = req.text
    else:
       print req

    return proyectos


### METODO QUE RECORRE LOS PROYECTOS DEVUELTOS POR EL API Y LOS FORMATEA PARA GUARDAR UN ARCHIVO JSON
def procesar_proyectos_api(proyectos):

    # Recorrer el json devuelto del api y transformarlo para usar los datos necesarios
    proyectosJSON = json.loads(proyectos)
    
    nuevoJSON = "function obtenerProyectos() { return ["

    for item in proyectosJSON:
        
        if nuevoJSON != "function obtenerProyectos() { return [":
            nuevoJSON = nuevoJSON + ","
            
        if item["Active"] == True:
            lineaNueva = '{"ProjectId":' + str(item["ProjectId"]) + ',"ProjectName":"' + item["ProjectName"] + '"}'
            nuevoJSON = nuevoJSON + lineaNueva
            listaProyectos.append(item["ProjectId"])

    nuevoJSON = nuevoJSON + '] }'

    # Guardar archivo
    fichero = codecs.open("proyectos.js", "w", encoding="utf-8")
    fichero.write(nuevoJSON)
    fichero.close()
    
    print 'proyectos api procesados ok!'


### METODO QUE DEVUELVE LOS PROYECTOS ALMACENADOS EN LOCAL
def obtener_proyectos_locales():

    try:
        #fichero = codecs.open("proyectos.json", "r", encoding="utf-8")
        fichero = file("proyectos.json", "r")
        #datos = fichero.read()
        #datos = datos[1 : - 1]
        #print datos
        proyectosLocales = json.loads(fichero.read().decode("utf-8"))
        #proyectosLocales = json.loads(datos)
        #print proyectosLocales

        for majorkey, subdict in proyectosLocales.iteritems():
            print majorkey
            
        #for item in proyectosLocales:
        #    print item["ProjectId"]
            
        print "Proyectos locales cargados"            
        return proyectosLocales
        
    except:
        e = sys.exc_info()
        print "Proyectos locales no encontrados: "
        print e
        return None


### METODO QUE CONECTA CON EL API Y OBTIENE TODAS LAS TAREAS DE TODOS LOS PROYECTOS
def obtener_tareas_api(token, proyectos):

    if token == "":
        token = iniciar_sesion_api()

    headers = {"Token":token}

    tareas = ""

    for item in proyectos:      
        url = URL_API + EMPRESA_API + "/project/" + str(item) + "/tasks/"

        req = requests.get(url, headers = headers)

        if req.status_code == 200:
            print "obtener tareas api del proyecto " + str(item) + " ok!"
            tareas = tareas + req.text
        else:
           print req
    
    return tareas


### METODO QUE RECORRE LAS TAREAS DEVUELTAS Y GUARDA LOS DATOS EN LOCAL
def procesar_tareas_api(tareas):

    # Recorrer el json devuelto del api y transformarlo para usar los datos necesarios
    tareas = tareas.replace("][",",")
    tareasJSON = json.loads(tareas)
    print "json convertido"
    
    nuevoTareaResumen = "function obtenerTareasResumen() { return ["
    nuevoTareaNormal = "function obtenerTareas() { return ["

    for item in tareasJSON:
            
        if item["TaskCategory"] == "Summary Task":
            
            if nuevoTareaResumen != "function obtenerTareasResumen() { return [":
                nuevoTareaResumen = nuevoTareaResumen + ", "
                
            lineaNueva = '{"ProjectId": ' + str(item["ProjectId"]) + ', "TaskId": ' + str(item["TaskId"]) + ', "TaskName": "' + item["TaskName"] + '"}'
            nuevoTareaResumen = nuevoTareaResumen + lineaNueva
            
        elif item["TaskCategory"] == "Task":

            if nuevoTareaNormal != "function obtenerTareas() { return [":
                nuevoTareaNormal = nuevoTareaNormal + ", "

            parent = "null"
            if item["ParentTask"] != None:
                parent = str(item["ParentTask"]["ParentTaskId"])

            status = "null"
            if item["TaskStatus"] != None:
                status = str(item["TaskStatus"]["TaskStatusName"])

            name = "null"
            if item["TaskName"] != None:
                name = item["TaskName"].replace('"',"'")

            priority = "null"
            if item["TaskPriority"] != None:
                priority = item["TaskPriority"]["TaskPriorityName"]

            team = "["
            if item["TaskTeam"] != None:
                if item["TaskTeam"]["TaskManagers"] != None:
                    
                    listaResponsables = item["TaskTeam"]["TaskManagers"]
                    for res in listaResponsables:

                        if team != "[":
                            team = team + ", "

                        if res["DisplayName"] != None:
                            team = team + '"' + res["DisplayName"] + '"'
                            
            team = team + "]"
                    
                
            lineaNueva = '{"ProjectId": ' + str(item["ProjectId"]) + ', "TaskId": ' + str(item["TaskId"]) + ', "TaskName": "' + name + '", "ParentTask": ' + parent + ', "TaskStatus": "' + status + '", "TaskPriority": "' + priority + '", "TaskManagers": ' + team + '}'
            nuevoTareaNormal = nuevoTareaNormal + lineaNueva

    nuevoTareaResumen = nuevoTareaResumen + "] }"
    nuevoTareaNormal = nuevoTareaNormal + "] }"

    # Guardar archivo de tareas normales
    fichero = codecs.open("tareas.js", "w", encoding="utf-8")
    fichero.write(nuevoTareaNormal)
    fichero.close()

    # Guardar archivo de tareas resumen
    fichero = codecs.open("tareas_resumen.js", "w", encoding="utf-8")
    fichero.write(nuevoTareaResumen)
    fichero.close()
    
    print 'tareas api procesadas ok!'


### METODO INICIAL DE LA APLICACION
def start():

    # Iniciar Sesion
    token = iniciar_sesion_api()
    
    # Cargar Proyectos
    proyectos = obtener_proyectos_api(token)
    procesar_proyectos_api(proyectos)

    # Cargar Tareas
    tareas = obtener_tareas_api(token, listaProyectos)
    procesar_tareas_api(tareas)
    
start()
print 'fin'
