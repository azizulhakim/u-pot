import xml.etree.ElementTree as ET
import re
import requests

url = 'http://10.0.0.158:49154/upnp/control/basicevent1'
soapaction = 'urn:Belkin:service:basicevent:1'

filecontent = ''
print(soapaction)
with open('eventservice.xml', 'r') as content_file:
    filecontent = content_file.read()

xmlstring = re.sub(' xmlns="[^"]+"', '', filecontent, count=1)
root = ET.fromstring(xmlstring)

stateVariables = {}
serviceStateTable = root[2]
for stateVariable in serviceStateTable.findall('stateVariable'):
    stateVariables[stateVariable.findall('name')[0].text.lower()] = stateVariable.findall('defaultValue')[0].text
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

actionlist = root[1]
for action in actionlist.findall('action'):
    name = action.findall('name')[0].text
    if name.startswith('Get'):
        headers = {'content-type': 'text/xml', 'soapaction': '"' + soapaction + "#" + name + '"'}
        body = '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">' + '<s:Body>' + '<u:' + name + ' xmlns:u="' + soapaction + '">' + '</u:' + name + '>' + '</s:Body>' + '</s:Envelope>'
        #print(body)
        response = requests.post(url, data = body, headers = headers)
        #print(response.content)

        if response.status_code == 200:
            responseXML = ET.fromstring(response.content)
            bodyXML = responseXML.findall('{http://schemas.xmlsoap.org/soap/envelope/}Body')[0]
            #print(ET.tostring(bodyXML))
            payloadKey = '{urn:Belkin:service:basicevent:1}' + name + "Response"
            payload = bodyXML.findall(payloadKey)[0]
            for child in payload:
                stateVariables[child.tag.lower()] = child.text
                if stateVariables[child.tag.lower()] == None:
                    stateVariables[child.tag.lower()] = ""


print(stateVariables)


# gupnp_service_action_set (action,
#                             "ResultStatus", G_TYPE_BOOLEAN, status,
#                             NULL);

# gupnp_service_action_get (action,
#                             "newTargetValue", G_TYPE_BOOLEAN, &target,
#                             NULL);


for action in actionlist.findall('action'):
    name = action.findall('name')[0].text
    out = 'G_MODULE_EXPORT void {}_cb(GUPnPService *service, GUPnPServiceAction *action, G_GNUC_UNUSED gpointer user_data);'
    print(out.format(name))

for action in actionlist.findall('action'):
    name = action.findall('name')[0].text
    print('G_MODULE_EXPORT void ' + name + "_cb(GUPnPService *service, GUPnPServiceAction *action, G_GNUC_UNUSED gpointer user_data) {")
    print("    g_print(\"" + name + "_cb received\");")

    if name in actionArgumentMap.keys():
        for actionargument in actionArgumentMap[name]:
            argument = actionargument['name']
            relatedStateVariable = actionargument['relatedStateVariable']

            if relatedStateVariable not in stateVariables.keys():
                continue

            value = stateVariables[relatedStateVariable]

            if actionargument['direction'] == 'out':# and name.startswith("Get"):
                # argument = actionargument['name']
                # relatedStateVariable = actionargument['relatedStateVariable']
                # value = stateVariables[relatedStateVariable]
                out = 'gupnp_service_action_set (action, "{}", G_TYPE_STRING, "{}", NULL);'
                print(out.format(argument, value))

            elif actionargument['direction'] == 'in':# and name.startswith("Set"):
                # argument = actionargument['name']
                # relatedStateVariable = actionargument['relatedStateVariable']
                # value = stateVariables[relatedStateVariable]
                out = 'gupnp_service_action_get (action, "{}", G_TYPE_STRING, {}, NULL);'
                print(out.format(argument, relatedStateVariable))

    print('    gupnp_service_action_return (action);')
    print("}\n")

for action in actionlist.findall('action'):
    name = action.findall('name')[0].text
    out = 'g_signal_connect(GUPNP_SERVICE(basiceventService), "action-invoked::{}", G_CALLBACK({}_cb), NULL);'
    print(out.format(name, name))

for statevariable, value in stateVariables.items():
    print("char[100] " + statevariable + " = \"" + value + "\";")
