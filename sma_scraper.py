#Initialize necessary libraries
import xml.etree.ElementTree as etree #Import library for handling XML
import requests #Import library to implement HTTP requests
from datetime import datetime
from lxml import html

#Grab the timestamp from script's entry point to analyze execution time
startTime = datetime.now()

#Declare arrays for the device list in a given SMA plant and the inverters associated with the cluster controller
devices = []
inverters = []

#Enter in port forward to a cluster controller for remote access
ClusterControllerIP = 'http://111.222.333.444:8443'  

#Prepare the links for the cluster controller's login page and device overview page after a session is established
loginLink = ClusterControllerIP + '/culture/login'
deviceLink = ClusterControllerIP + '/culture/DeviceOverview.dml'

#Prepare the data payload needed to POST to the cluster controller to establish an authentication session
payload = {
	"Language": "LangEN", #Specify language for the session - note that this field MUST be included to log in!
	"Userlevels": "Installer", #Username to log into the cluster controller
	"password": "1111" #Password to log into the cluster controller
}

#Establish a connection to the cluster controller and POST the login payload to create a session
s = requests.session()
loginResponse = s.post(loginLink,data=payload)

#Fetch the XML response from the cluster controller upon successful login
loginResponse = s.get(deviceLink)

#Build an XML tree from the cluster controller's response
temptree = etree.fromstring(loginResponse.text)
tree = etree.ElementTree(temptree)
root = tree.getroot()

#Parse the XML tree for any devices by keying off the 'Value' tag and add them to the array of devices
for element in root.iter(tag= 'Value'):
	devices.append(element.text)
	
#Build out the array of inverters by scanning the list of devices for the ":i" identifier
inverters = [s for s in devices if ":i" in s]

#Iterate through the array of inverters and parse their current data points
for i in range(0,len(inverters)):
	#Grab the XML responses for the Instantaeous Values tab of the AC and DC sides of the inverter, based on its serial number
	dcLink = ClusterControllerIP + '/culture/DeviceOverview.dml?__newTab=&__deviceKey=' + inverters[i] + '&__selected=hp.processDataOverview__&__selectedCategory=5#5'
	acLink = ClusterControllerIP + '/culture/DeviceOverview.dml?__newTab=&__deviceKey=' + inverters[i] + '&__selected=hp.processDataOverview__&__selectedCategory=6#6'
	dcResponse = s.get(dcLink) #get page data from server, block redirects
	acResponse = s.get(acLink) #get page data from server, block redirects
	
	#Initialize arrays to hold the data points read in from the AC and DC sides of the inverter
	dcValues = []
	acValues = []

	#Create an XML tree of the DC data page and traverse it to find each key/value pair, updating the dcValues array
	temptree = etree.fromstring(dcResponse.text)
	tree= etree.ElementTree(temptree)
	root = tree.getroot()

	for element in root.iter(tag= 'Value'):
		dcValues.append(element.text)

	#Create an XML tree of the AC data page and traverse it to find each key/value pair, updating the acValues array
	temptree = etree.fromstring(acResponse.text)
	tree= etree.ElementTree(temptree)
	root = tree.getroot()

	for element in root.iter(tag= 'Value'):
		acValues.append(element.text)

	#Print out the values of the parsed XML, representing the inverter's current data set
	print ('Serial Number: ', acValues[85+i]) 	
	print ('Total AC Energy: ', acValues[78], ' MWh')
	print ('Total AC Active Power: ', acValues[71], ' kW')
	print ('AC L1 Power: ', acValues[48], ' W')
	print ('AC L2 Power: ', acValues[53], ' W')
	print ('AC L3 Power: ', acValues[58], ' W')
	print ('V L1 to N: ', acValues[20], ' V')
	print ('V L2 to N: ', acValues[24], ' V')
	print ('V L3 to N: ', acValues[28], ' V')
	print ('I L1: ', acValues[6], ' A')
	print ('I L2: ', acValues[11], ' A')
	print ('I L3: ', acValues[16], ' A')
	print ('Frequency: ', acValues[62], ' Hz')
	print ('DC Current Input 1: ', dcValues[5], ' A')
	print ('DC Voltage Input 1: ', dcValues[14], ' V')
	print ('DC Power Input 1: ', dcValues[23], ' W')
	print ('DC Current Input 2: ', dcValues[10], ' A')
	print ('DC Voltage Input 2: ', dcValues[18], ' V')
	print ('DC Power Input 2: ', dcValues[28], ' W\n')
	
print ('Inverter Count = ' , len(inverters)) #Print out the total number of inverters connected to the cluster controller
print ('Total exectution time = ', datetime.now() - startTime, 's') #Calculate the execution time based on script's exit point and write it to the console
