# Import module
import typeworld.api

# Root of Response
root = typeworld.api.RootResponse()

# EndpointResponse
endpoint = typeworld.api.EndpointResponse()
endpoint.name.en = "Font Publisher"
endpoint.canonicalURL = "http://fontpublisher.com/api/"
endpoint.adminEmail = "admin@fontpublisher.com"
endpoint.supportedCommands = [
    x["keyword"] for x in typeworld.api.COMMANDS
]  # this API supports all commands

# Attach EndpointResponse to RootResponse
root.endpoint = endpoint

# Print API response as JSON
print(root.dumpJSON())
