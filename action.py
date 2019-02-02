# Represent the action that can be invoked on an UPnP-based IoT device
class Action(object):
    def __init__(self, actionroot):
        self.name = actionroot.find('./name').text

        argumentLists = None
        if len(actionroot.findall('./argumentList/argument')) > 0:
            argumentLists = actionroot.findall('./argumentList/argument')
        else:
            argumentLists = actionroot.findall('./argumentList')

        self.arguments = []
        for argument in argumentLists:
            try:
                argumentName = argument.find('./name').text
                relatedStateVariable = argument.find('./relatedStateVariable').text.lower()
                direction = argument.find('./direction').text
                self.arguments.append({ 'name': argumentName, 'relatedStateVariable': relatedStateVariable, 'direction': direction })
            except:
                print("Unable to extract arguments for action: ", self.name)
