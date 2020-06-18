# Splunk_App_Version_Checker
Uses Splunk's REST API to pull down all apps and versions then checks Splunkbase for compatibility.

## How to run
```
python3 splunkbase_web_scraper.py
```

## Example Results
```
Enter Server Name: SERVER
Enter Version to Check (eg: 8.0): 8.0
Enter Splunk Credentials
Username: admin
Password:
Lab_Workload_Management_Sec_SH, null, null
Splunk Common Information Model, 4.13.0, https://apps.splunk.com/apps/id/Splunk_SA_CIM
Splunk Add-on for Unix and Linux, 7.0.1, https://apps.splunk.com/apps/id/Splunk_TA_nix
TA-Lab_Cluster_SH, null, null
_cluster, null, null
Home_Network, 1.0.0, null
Lab_Workload_Management_IDX-Cluster, null, null
Technology Add-on for pfSense, 2.2.1, https://apps.splunk.com/apps/id/TA-pfsense

[-] Splunk Common Information Model is not 8.0 compatible.
[+] Splunk Add-on for Unix and Linux is 8.0 compatible.
[+] Technology Add-on for pfSense is 8.0 compatible.
```
 ## Results Explained
The script reached out to the Splunk search head via the REST API, and ran a query that returned all apps installed. There were only three apps that were installed from Splunkbase. The three apps installed each have a field that provide links to Splunkbase where the script then checks if the version of the installed apps are compatible with the version that was entered.
