import requests
import csv

metadata = 'dsu_digipiid'
uuidlookup = {}

ACCOUNT = {
	"api": "REDACTED",
	"region": "lon",
	"ddi": REDACTED,
	"name": "REDACTED"
}

def auth(ACCOUNT):
	auth_body = {
		"auth": {
			"RAX-KSKEY:apiKeyCredentials": {
				"username": ACCOUNT["name"],
				"apiKey": ACCOUNT["api"],
				"tenantName": ACCOUNT["ddi"]
			}
		}
	}
	r = requests.post(
		"https://identity.api.rackspacecloud.com/v2.0/tokens", json=auth_body
	)
	token = r.json()["access"]["token"]["id"]
	return token
  
def getdigipi(ACCOUNT,token,uuid):
      token = auth(ACCOUNT)
      response = requests.get('https://lon.servers.api.rackspacecloud.com/v2/' + str(ACCOUNT["ddi"]) + '/servers/' + uuid +'/metadata/' + metadata, headers={'X-Auth-Token': token})
      if response.status_code == 404:
        #print('[!] [{0}] URL not found: [{1}]'.format(response.status_code,api_url))
        print('URL not found:', response.status_code)
        return None
  elif response.status_code == 401:
        print('Authentication Failed:', response.status_code)
        return None
  elif response.status_code >= 403:
        print('Forbidden', response.status_code)
        return None
  elif response.status_code == 200:
        digipi = response.json()['meta'][metadata]
        return digipi
  else:
        print('Unexpected Error:', response.status_code, response.content)
        return None
    
token = auth(ACCOUNT)
   
input_file = csv.DictReader(open("bill.file.csv"))
for row in input_file:
    if row['SERVICE_TYPE'] == 'Cloud Servers':
      uuid = row['RES_ID']
      if row['RES_ID'] != '':
        if uuid not in uuidlookup:
          digipi = getdigipi(ACCOUNT,token,uuid)
          if digipi is not None:
            uuidlookup[uuid] = digipi
            row['DIGIPI_ID'] = digipi
            print('adding', digipi)
        else:
          digipi = uuidlookup.get(uuid)
          row['DIGIPI_ID'] = digipi
          output_file.writerow(row)
          print('found', digipi)
    else:
      row['DIGIPI_ID'] = ''
