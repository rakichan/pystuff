'''
Create a simple GUI of city information of California
	See attached JSON file (ca.json), which contains information of all cities in CA
	Use the data abstract from the JSON file to create a simple GUI for it
	The GUI should have a filter function based on the selection of city name (selectable)
	Display information of county full name, latitude, longitude 
	Sample GUI is shown below
	Use any python library as needed
'''
import sys
from PyQt4 import QtCore, QtGui
from myForm import Ui_Dialog
import json

CITY_INFORMATION = 'ca.json'	# for now its hardcoded

class cityInformation(QtGui.QDialog):
	'''
	Builds the UI and populates from the json data
	'''
	def __init__(self, parent=None):
		QtGui.QWidget.__init__(self, parent)
		self.ui = Ui_Dialog()
		self.ui.setupUi(self)
		self.setWindowTitle("City Information")
		self.populate()

		self.ui.cityComboBox.activated[int].connect(self.onActivated)

	def populate(self):
		'''
		To populate the combo box with the 
		city names from the json file
		'''
		try:
			with open(CITY_INFORMATION) as dataFile:
				self.data = json.load(dataFile)
				# populate the combobox
				for item in self.data:
					self.currText = item['name']
					# print self.currText
					self.ui.cityComboBox.addItem(self.currText)
		except IOError:
			print "The file is missing"
			sys.exit()

	def onActivated(self, i):
		'''
		Upon item selection, the onactivated method is called
		'''
		self.ui.countyTextBrowser.setText(self.data[i]['county_name'])
		self.ui.latitudeTextBrowser.setText(self.data[i]['primary_latitude'])
		self.ui.longitudeTextBrowser.setText(self.data[i]['primary_longitude'])
	

if __name__ == "__main__":
		app = QtGui.QApplication(sys.argv)
		myapp = cityInformation()
		myapp.show()
		sys.exit(app.exec_())
