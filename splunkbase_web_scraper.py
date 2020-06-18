import requests
from bs4 import BeautifulSoup
import json
from splunk_rest_query import SplunkQuery
import time

def getSplunkAppVersions(splunkappURL):
  source = requests.get(splunkappURL)

  soup = BeautifulSoup(source.text, 'lxml')
  side_bar = soup.find('div', class_='u.item:1/1* sidebar')

  version_dict = {}
  for versions in side_bar.find_all('sb-release-select', class_='u.item:1/1@*'):
      version_dict[versions['sb-target']] = []

  for versions in side_bar.find_all('sb-release-select', class_='u.item:1/1@*'):
      for link in versions.find_all('a'):
          version = link.parent.attrs['sb-target']
          version_dict[version].append(link.text)
  source.close()
  return version_dict

def checkAppCompatibility(resultDict):
  for apps in resultDict:
    if (apps['version'] != 'null') and (apps['details'] != 'null'):
      url = apps['details']
      app_ver_dict = getSplunkAppVersions(url)
      app_version = apps['version']
      if version_compatibility in app_ver_dict[app_version]:
        print('[+] ' + apps['label'] + ' is ' + version_compatibility + ' compatible.')
      else:
        print('[-] ' + apps['label'] + ' is not ' + version_compatibility + ' compatible.')
      time.sleep(1.5)


serverName = input('Enter Server Name: ')
searchQuery = '| rest /services/apps/local | search disabled=0 core=0 | dedup label | table label, version, details'
version_compatibility = input('Enter Version to Check (eg: 8.0): ')

# Create a new search and run through Splunk REST API
#newQuery = SplunkQuery(userName,password,serverName,searchQuery)
newQuery = SplunkQuery(serverName,searchQuery)
results =  newQuery.splunkSearch()

# Printing results for Debugging purposes
for keys in results:
  print(keys['label'] + ", " + keys['version'] + ", " + keys['details'])

print("\n")
print(results)
print("\n")

# Take results from REST Search Query and Check if installed Splunk apps are compatible
checkAppCompatibility(results)
