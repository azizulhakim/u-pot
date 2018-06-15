import xml.etree.ElementTree as ET
import re

class XmlReader(object):
    def readXML(self, xmlPath):
        xmlcontent = ''
        with open(xmlPath, 'r') as content_file:
            xmlcontent = content_file.read()
        return xmlcontent

    def stripNamespaceFromXml(self, xmlcontent):
        xmlcontent = re.sub(' xmlns="[^"]+"', '', xmlcontent, count=1)

        return xmlcontent
