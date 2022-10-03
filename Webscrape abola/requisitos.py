import requests

response = requests.get('https://abola.pt/')

print('Status code:', response.status_code)
'''
Informational responses (100–199)
Successful responses (200–299)
Redirection messages (300–399)
Client error responses (400–499)
Server error responses (500–599)
'''

print(f'Header:{response.headers}')

print(f'Content: {response.content}')

# Press ctrl + U to see the site html code
