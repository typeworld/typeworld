# Import module
import typeworld.protocol

# Root of Response
root = typeworld.protocol.RootResponse()

### EndpointResponse
endpoint = typeworld.protocol.EndpointResponse()
endpoint.name.en = 'Font Publisher'
endpoint.canonicalURL = 'http://fontpublisher.com/api/'
endpoint.adminEmail = 'admin@fontpublisher.com'
endpoint.supportedCommands = [x['keyword'] for x in typeworld.protocol.COMMANDS] # this API supports all commands

# Attach EndpointResponse to RootResponse
root.endpoint = endpoint

# Print API response as JSON
print(root.dumpJSON())