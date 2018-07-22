from xmlreader import XmlReader
from service import Service
import xml.etree.ElementTree as ET
import urllib.request
import requests

class Device(object):
    def __init__(self, host, path):
        self.host = host
        self.path = path

        content = requests.get(host +  path).content.decode('ASCII')

        xmlreader = XmlReader()
        # xmlcontent = xmlreader.readXML(self.deviceDescriptorPath)
        xmlcontent = xmlreader.stripNamespaceFromXml(content)
        #print(xmlcontent)

        root = ET.fromstring(xmlcontent)
        self.major = root.find("./specVersion/major").text
        self.minor = root.find("./specVersion/minor").text

        self.deviceType = root.find("./device/deviceType").text
        self.friendlyName = root.find("./device/friendlyName").text
        self.manufacturer = root.find("./device/manufacturer").text
        self.manufacturerURL = root.find("./device/manufacturerURL").text
        self.modelDescription = root.find("./device/modelDescription").text
        self.modelName = root.find("./device/modelName").text
        self.modelNumber = root.find("./device/modelNumber").text
        self.modelURL = root.find("./device/modelURL").text
        self.serialNumber = root.find("./device/serialNumber").text
        self.udn = root.find("./device/UDN").text
        #self.upc = root.find("./device/UPC").text
        #self.macAddress = root.find("./device/macAddress").text
        #self.firmwareVersion = root.find("./device/firmwareVersion").text
        #self.iconVersion = root.find("./device/iconVersion").text
        #self.binaryState = root.find("./device/binaryState").text
        #self.presentationURL = root.find("./device/presentationURL").text

        self.iconList = []
        for icon in root.findall("./device/iconList/icon"):
            self.iconList.append({
                'mimeType': icon.find("./mimetype").text,
                'width': icon.find("./width").text,
                'height': icon.find("./height").text,
                'depth': icon.find("./depth").text,
                'url': icon.find("./url").text
            })

        self.serviceList = self.extractServices(root)
        self.generateServiceCode()

    def extractServices(self, root):
        print(root)
        serviceList = []
        for service in root.findall("./device/serviceList/service"):
            serviceList.append(Service(self.host, service))

        return serviceList

    def generateServiceCode(self):
        print("#include <libgupnp/gupnp.h>")
        print("#include <stdlib.h>")
        print("#include <gmodule.h>")
        print("#include <locale.h>")
        print("")

        for service in self.serviceList:
            for statevariable, value in service.stateVariables.items():
                valueLength = str(len(value) + 5)
                print("char " + statevariable + "[" + valueLength + "] = \"" + value + "\";")
        print("")

        for service in self.serviceList:
            for action in service.actions:
                name = action.name
                out = 'G_MODULE_EXPORT void {}_cb(GUPnPService *service, GUPnPServiceAction *action, G_GNUC_UNUSED gpointer user_data);'
                print(out.format(name))


        print("")
        print(' // ---------------------------------------- Callback Functions ---------------------------------------------------')

        for service in self.serviceList:
            for action in service.actions:
                name = action.name
                print('G_MODULE_EXPORT void ' + name + "_cb(GUPnPService *service, GUPnPServiceAction *action, G_GNUC_UNUSED gpointer user_data) {")
                print('    g_print("' + name + '_cb received\\n");')

                for argument in action.arguments:
                    relatedStateVariable = argument['relatedStateVariable']

                    if relatedStateVariable not in service.stateVariables.keys():
                        continue

                    value = service.stateVariables[relatedStateVariable]

                    if argument['direction'] == 'out':# and name.startswith("Get"):
                        # argument = actionargument['name']
                        # relatedStateVariable = actionargument['relatedStateVariable']
                        # value = stateVariables[relatedStateVariable]
                        out = '    gupnp_service_action_set (action, "{}", G_TYPE_STRING, {}, NULL);'
                        print(out.format(argument['name'], relatedStateVariable))

                    elif argument['direction'] == 'in':# and name.startswith("Set"):
                        # argument = actionargument['name']
                        # relatedStateVariable = actionargument['relatedStateVariable']
                        # value = stateVariables[relatedStateVariable]
                        out = '    gupnp_service_action_get (action, "{}", G_TYPE_STRING, {}, NULL);'
                        print(out.format(argument['name'], relatedStateVariable))

                print('    gupnp_service_action_return (action);')
                print("}\n")


        # make main function now
        print("int \nmain(G_GNUC_UNUSED int argc, G_GNUC_UNUSED char **argv)")
        print("{")
        print("  GOptionContext *optionContext;")
        print("  GMainLoop *main_loop;")
        print("  GError *error = NULL;")
        print("  GUPnPContext *context;")
        print("  GUPnPRootDevice *upnpDevice;")
        for service in self.serviceList:
            out = '  GUPnPServiceInfo *{}Service;'
            print(out.format(service.name))

        print("")

        print("  printf(\"%d\\n\", argc);")
        print("  if (argc != 3) {")
        print("    printf(\"Usage: ./light-server INTERFACE PORT\\n\");")
        print("    exit(1);")
        print("  }")
        print("")
        print("  char* interfacename = argv[1];")
        print("  int port = atoi(argv[2]);")

        print("  setlocale(LC_ALL, \"en_US.utf8\");")

        print("  GString *gs = g_string_new(\"abc\");")
        print("  g_print(\"%s\\n\", gs->str);")

        print("\n\n\n")
        print("  /* Create the UPnP context */")
        print("  context = gupnp_context_new (interfacename, port, &error);")
        print("  if (error) {")
        print("    g_printerr (\"Error creating the GUPnP context: %s\\n\",")
        print("    error->message);")
        print("    g_error_free (error);")
        print("    return EXIT_FAILURE;")
        print("  }")

        print("  //////// UPnP Device Start ///////////////////////////")
        print("  upnpDevice = gupnp_root_device_new (context, \"setup.xml\", \".\", &error);")
        print("  if (error != NULL) {")
        print("    g_printerr (\"Error creating the GUPnP root device: %s\\n\",")
        print("            error->message);")

        print("    g_error_free (error);")

        print("    return EXIT_FAILURE;")
        print("  }")
        print("  gupnp_root_device_set_available (upnpDevice, TRUE);")

        print("")
        for service in self.serviceList:
            out = '  {}Service = gupnp_device_info_get_service(GUPNP_DEVICE_INFO (upnpDevice), "{}");'
            print(out.format(service.name, service.serviceType))

        print("")
        print(' // ------------------------------ Enable Services -------------------------------------------------------')

        for service in self.serviceList:
            for action in service.actions:
                name = action.name
                out = '  g_signal_connect(GUPNP_SERVICE({}Service), "action-invoked::{}", G_CALLBACK({}_cb), NULL);'
                print(out.format(service.name, name, name))

        print("")
        print("  /* Run the main loop */")
        print("  main_loop = g_main_loop_new (NULL, FALSE);")
        print("  g_main_loop_run (main_loop);")

        print("  /* Cleanup */")
        print("  g_main_loop_unref (main_loop);")
        print("  //  g_object_unref (service);")
        print("  g_object_unref (context);")

        print("  return EXIT_SUCCESS;")
        print("}")
