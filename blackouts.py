import requests
from requests.auth import HTTPDigestAuth
import json
import urllib3
import collections
import sys
import os
import time
import ConfigParser
import commands
import time
import datetime
import base64

server = ""
token = ""
encoded = ""
epass = ""
blackout_name = ""
#Clase que representa una Applicacion
class App(object):
    def __init__(self, id, name):
        self.id = id
        self.name = name

class Env(object):
    def __init__(self, id, name, calendarId):
        self.id = id
        self.name = name
        self.calendarId = calendarId
#metodo obtiene todas las apps, retorna objeto con id y name de aplicacion
def get_apps():
    url = server + "/rest/deploy/application/"
    
    print 'base64 encoded: ' + epass
    
    #r = requests.get('<MY_URI>', headers={'Authorization': 'TOK:<MY_TOKEN>'})
    headers = {'Authorization': 'Basic '+ ':' + epass}
    #resp = requests.get(url,headers=headers, verify=False)
    resp = requests.get(url, verify=False, headers=headers)
    
    
    #e5760a4d-b28e-452a-bd69-3bbe4812a01f
  
    
    data = resp.json()
    apps = []
    appsList = []
    for app in data:
      f = App(app["id"], app["name"])
      
      appsList.append(f)
 
    return appsList

#metodo para obtener los ambientes de una app
def get_environments(app):
    
    url = server + "/rest/deploy/application/"+app+"/environments/false"
    headers = {'Authorization': 'Basic '+ ':' + epass}
    resp = requests.get(url, verify=False, headers=headers)
    data = resp.json()
    envList = []
    for env in data:
        e = Env(env["id"], env["name"], env["calendarId"])
        envList.append(e)
 
    return envList
        
   
def add_blackouts(calendarId, inicio, fin):
    print "agregar blackouts"
    #headers = {"Content-Type": "application/json"}
    headers = {'Authorization': 'Basic '+ ':' + epass}
    data = {
            "name": blackout_name,
            "startDate": inicio,
            "startTime": "1970-01-01T12:00:00.000Z",
            "endDate": fin,
            "endTime": "1970-01-01T12:00:00.000Z",
            "calendarId": calendarId
            }
            
    url = server + "/rest/deploy/schedule/blackout"
    #resp = requests.put(url, verify=False, auth=('admin', '3htp.com2017'))
    response = requests.put(url, data=json.dumps(data), headers=headers, verify=False, auth=('admin', '3htp.com2017'))
    
    if response.status_code == 200:
        print "Blackout Agregado Correctamente"
    else:
        print "ERROR al crear Blackout"
        print response.status_code
        print(response.text)
   
def delete_blackouts(env_id):
    print "Quitar BlackOut"
    headers = {'Authorization': 'Basic '+ ':' + epass}
    #url = server + "/rest/deploy/schedule/calendar/environment/"+ env_id+"/1524970800000/1527998399999"    
    url = server + "/rest/deploy/schedule/calendar/environment/"+ env_id+"/0000000000000/9999999999999"
    resp = requests.get(url, verify=False, headers=headers)
    data = resp.json()
    blackouts = data["blackouts"]
    for blackout in blackouts:
        print "blackout " + blackout["id"]
        #headers = {'content-type': 'application/json'}
        headers = {'Authorization': 'Basic '+ ':' + epass}
        url_blackout = server + "/rest/deploy/schedule/blackout/"+blackout["id"]
        #resp = requests.delete(url_blackout, verify=False, auth=('admin', '3htp.com2017'))
        response = requests.delete(url_blackout,  headers=headers, verify=False)
        if response.status_code == 200:
            print "Blackout Eliminado Correctamente"
        else:
            print "ERROR al Eliminar Blackout"
            print response.status_code
            print(response.text)

def parse_fecha(fecha):
 
  time_tuple = time.strptime(fecha, "%Y-%m-%d %H:%M:%S")
  timestamp = time.mktime(time_tuple)
  ini=  (timestamp * 1000)
  return ini  
#metodo para leer secciones
def ConfigSectionMap(section):
    dict1 = {}
    options = Config.options(section)
    for option in options:
        try:
            dict1[option] = Config.get(section, option)
            if dict1[option] == -1:
                DebugPrint("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1
########################
# Main script
#########################

urllib3.disable_warnings()
print "Leer archivo INI"
    
file_conf=sys.argv[1]
print file_conf
#leer archivo de propiedades
Config = ConfigParser.ConfigParser()
try:
	Config.read([file_conf])
except:
	print  "Error al buscar archivo providers.ini"
	sys.exit(1)
    
Config.sections()
#Leer parametros desde archivo Ini
server = ConfigSectionMap("default_config")['url_server']
blackout_name = ConfigSectionMap("default_config")['blackout_name']
fecha_inicio = ConfigSectionMap("default_config")['fecha_inicio']
fecha_fin = ConfigSectionMap("default_config")['fecha_fin']
token = ConfigSectionMap("default_config")['token']
habilitar = ConfigSectionMap("default_config")['habilitar']
print server
print blackout_name
print fecha_inicio
print fecha_fin
print token
#encode token
epass = base64.b64encode('PasswordIsAuthToken' + ':' + token )
print habilitar

#parse date to timestamp
inicio = parse_fecha(fecha_inicio)
fin = parse_fecha(fecha_fin)

print inicio 
print fin

apps = get_apps()

for app in apps:
    envs = get_environments(app.id)
    print "################. "+ app.name+". #####################" 
    for env in envs:
        print "AMBIENTE   : " + env.name
        print "AMBIENTE-ID: " + env.id
        print "CALENDAR-ID: " + env.calendarId
        if habilitar == "true":
            add_blackouts(env.calendarId, inicio, fin)
        else:
            delete_blackouts(env.id)

