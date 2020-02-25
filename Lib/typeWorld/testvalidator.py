import ssl, certifi, urllib, urllib.parse, urllib.request, json
sslcontext = ssl.create_default_context(cafile=certifi.where())
protectedSubscription = 'typeworld://json+https//s9lWvayTEOaB9eIIMA67:OxObIWDJjW95SkeL3BNr@typeworldserver.com/api/q8JZfYn9olyUvcCOiqHq/'
MOTHERSHIP = 'https://typeworld2.appspot.com/api'

print('Started...')

url = MOTHERSHIP
parameters = {"command": "validateAPIEndpoint",
			"subscriptionURL": protectedSubscription,
			}
data = urllib.parse.urlencode(parameters).encode('ascii')
response = urllib.request.urlopen(url, data, context=sslcontext)
response = json.loads(response.read().decode())

print(response)
