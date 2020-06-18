from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
import urllib.request, urllib.parse, urllib.error
import httplib2
from bs4 import BeautifulSoup
import re
import json
import getpass
import time

class SplunkQuery:
  
  sessionKey = ''
  sid = ''

  def __init__(self,serverName,searchQuery):
    self.baseurl='https://' + serverName + ':8089'
    self.searchQuery=searchQuery

  def getSessionKey(self):
    # Authenticate with server.
    # Disable SSL cert validation. Splunk certs are self-signed.
    print('Enter Splunk Credentials')
    serverContent = httplib2.Http(disable_ssl_certificate_validation=True).request(self.baseurl + '/services/auth/login',
      'POST',
      headers={},
      body=urllib.parse.urlencode({'username':input('Username: '), 'password':getpass.getpass()}))[1]
    key = BeautifulSoup(serverContent.decode("UTF-8"), 'xml')
    sessionKey = key.find('sessionKey')
    if not sessionKey:
      print("Error: " + key.find('messages').text)
      exit()
    else:
      return sessionKey.text

  def formatSearchQuery(self):
    # Remove leading and trailing whitespace from the search
    self.searchQuery.strip()

    # If the query doesn't already start with the 'search' operator or another
    # generating command (e.g. "| inputcsv"), then prepend "search " to it.
    if not (self.searchQuery.startswith('search') or self.searchQuery.startswith("|")):
      self.searchQuery = 'search ' + self.searchQuery
    return self.searchQuery

  def splunkInitialSearch(self):
    # Run the search.
    # Again, disable SSL cert validation.
    self.sessionKey = self.getSessionKey()
    query = self.formatSearchQuery()
    search_post_req = httplib2.Http(disable_ssl_certificate_validation=True).request(self.baseurl + '/services/search/jobs','POST',
      headers={'Authorization': 'Splunk %s' % self.sessionKey},body=urllib.parse.urlencode({'search': query}))[1]

    # Parse the SID (search_id) from the search post request
    search_post_soup = BeautifulSoup(search_post_req.decode("UTF-8"), 'xml')
    search_id = search_post_soup.find('sid').text
    return search_id
  
  def isSearchCompleted(self):
    # Ensure search has completed
    self.sid = self.splunkInitialSearch()
    while True:
      search_status_url = self.baseurl + '/services/search/jobs/' + self.sid
      search_status = httplib2.Http(disable_ssl_certificate_validation=True).request(search_status_url,'GET',
        headers={'Authorization': 'Splunk %s' % self.sessionKey},body=None)[1].decode("UTF-8")
      pattern = re.compile('isDone">(0|1)')
      status = pattern.search(search_status).groups()[0]
      if (status == '1'):
        break
      time.sleep(1)
  
  def splunkSearch(self):
    self.isSearchCompleted()
    # Construct a GET request using the SID to get the search results
    url_string = self.baseurl + '/services/search/jobs/' + self.sid + '/results?output_mode=json&count=0'
    search_get_req = httplib2.Http(disable_ssl_certificate_validation=True).request(url_string,'GET',
      headers={'Authorization': 'Splunk %s' % self.sessionKey},body=None)[1]
    results = search_get_req.decode("UTF-8")

    results_dict = json.loads(results)
    for keys in results_dict['results']:
      keys.setdefault('label',"null")
      keys.setdefault('version',"null")
      keys.setdefault('details',"null")
    # Returns a list of dictionaries
    return results_dict['results']