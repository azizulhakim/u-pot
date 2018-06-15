import xml.etree.ElementTree as ET
import re
import requests

url = 'http://10.0.0.158:49154/upnp/control/basicevent1'
soapaction = 'urn:Belkin:service:basicevent:1'

filecontent = ''
with open('eventservice.xml', 'r') as content_file:
    filecontent = content_file.read()

xmlstring = re.sub(' xmlns="[^"]+"', '', filecontent, count=1)
root = ET.fromstring(xmlstring)

stateVariables = {}
serviceStateTable = root[2]
for stateVariable in serviceStateTable.findall('stateVariable'):
    stateVariables[stateVariable.findall('name')[0].text] = stateVariable.findall('defaultValue')[0].text.lower()
    #print("char[40] " + stateVariable.findall('name')[0].text + " = \"" + stateVariable.findall('defaultValue')[0].text + "\";")


actionlist = root[1]
actionArgumentMap = {}
for action in actionlist.findall('action'):
    actionName = action.findall('name')[0].text
    if len(action.findall('argumentList')) > 0:
        argumentlist = action.findall('argumentList')[0]
        key = "argument"
        if len(argumentlist.findall(key)) == 0:
            argumentlist = action
            key = "argumentList"

        arguments = []
        for argument in argumentlist.findall(key):
            argumentName = argument.findall('name')[0].text
            relatedStateVariable = argument.findall('relatedStateVariable')[0].text.lower()
            direction = argument.findall('direction')[0].text
            arguments.append({ 'name': argumentName, 'relatedStateVariable': relatedStateVariable, 'direction': direction })

        #print(arguments)
        actionArgumentMap[actionName] = arguments

print(actionArgumentMap)

# actionlist = root[1]
# for action in actionlist.findall('action'):
#     name = action.findall('name')[0].text
#     if name.startswith('Get'):
#         headers = {'content-type': 'text/xml', 'soapaction': '"' + soapaction + "#" + name + '"'}
#         body = '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">' + '<s:Body>' + '<u:' + name + ' xmlns:u="' + soapaction + '">' + '</u:' + name + '>' + '</s:Body>' + '</s:Envelope>'
#         #print(body)
#         response = requests.post(url, data = body, headers = headers)
#         #print(response.content)
#
#         if response.status_code == 200:
#             responseXML = ET.fromstring(response.content)
#             bodyXML = responseXML.findall('{http://schemas.xmlsoap.org/soap/envelope/}Body')[0]
#             #print(ET.tostring(bodyXML))
#             payloadKey = '{urn:Belkin:service:basicevent:1}' + name + "Response"
#             payload = bodyXML.findall(payloadKey)[0]
#             for child in payload:
#                 stateVariables[child.tag] = child.text
#                 if stateVariables[child.tag] == None:
#                     stateVariables[child.tag] = ""
#
#
# print(stateVariables)
#
#
# for statevariable, value in stateVariables.items():
#     print("char[100] " + statevariable + " = \"" + value + "\";")
