import keyring

key = '**replace**'
keyring.set_password('https://typeworld.appspot.com/api', 'revokeAppInstance', key)
keyring.set_password('http://127.0.0.1:8080/api', 'revokeAppInstance', key)
