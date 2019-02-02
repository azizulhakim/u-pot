from xmlreader import XmlReader
from action import Action
import xml.etree.ElementTree as ET
import requests

# Represents the Service of an UPnP-based IoT Device
class Service(object):
    def __init__(self, host, service):
        self.host = host
        self.serviceType = service.find("./serviceType").text
        self.serviceId = service.find("./serviceId").text
        self.controlURL = service.find("./controlURL").text
        self.eventSubURL = service.find("./eventSubURL").text
        self.SCPDURL = service.find("./SCPDURL").text
        self.name = self.SCPDURL.replace("/", "").replace(".xml", "")

        try:
            r = requests.get(host + self.SCPDURL)
            r.encoding = 'utf-8'
            content = r.text

            xmlreader = XmlReader()
            xmlcontent = xmlreader.stripNamespaceFromXml(content)

            root = ET.fromstring(xmlcontent)
            self.major = root.find("./specVersion/major").text
            self.minor = root.find("./specVersion/minor").text

            self.stateVariables = self.extractStateVariables(root)
            self.actions = self.extractActions(root)
            self.createHttpReq()

            # print(self.stateVariables)
        except Exception as ex:
            print('failed to parse: ', self.SCPDURL)
            print(ex)

    def extractStateVariables(self, root):
        stateVariables = {}
        for stateVariable in root.findall('./serviceStateTable/stateVariable'):
            try:
                stateVariables[stateVariable.find('./name').text.lower()] = stateVariable.find('./defaultValue').text
                if stateVariables[stateVariable.find('./name').text.lower()] == None:
                    stateVariables[stateVariable.find('./name').text.lower()] = ""
            except:
                stateVariables[stateVariable.find('./name').text.lower()] = ""

        return stateVariables


    def extractActions(self, root):
        actions = []
        for action in root.findall('./actionList/action'):
            actions.append(Action(action))

        return actions

    def createHttpReq(self):
        for action in self.actions:
            if action.name.lower().startswith('get'):
                soapaction = '"' + self.serviceType + "#" + action.name + '"'
                headers = {'content-type': 'text/xml', 'soapaction': soapaction}
                body = '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">' + '<s:Body>' + '<u:' + action.name + ' xmlns:u="' + self.serviceType + '">' + '</u:' + action.name + '>' + '</s:Body>' + '</s:Envelope>'
                url = self.host + self.controlURL

                response = requests.post(url, data = body, headers = headers)

                if response.status_code == 200:
                    responseXML = ET.fromstring(response.content)
                    bodyXML = responseXML.findall('{http://schemas.xmlsoap.org/soap/envelope/}Body')[0]
                    payloadKey = '{' + self.serviceType + '}' + action.name + "Response"

                    payload = bodyXML.findall(payloadKey)[0]

                    for child in payload:
                        self.stateVariables[child.tag.lower()] = child.text
                        if self.stateVariables[child.tag.lower()] == None:
                            self.stateVariables[child.tag.lower()] = ""
