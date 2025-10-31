import sys
#from pl_const import PATH
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget)
from PyQt5.QtCore import QTimer, Qt, QSize

from PyQt5 import uic

from platinum_frame import PlatinumGameFrame
from platinum_score import PlatinumScoreTable

class PlatinumSupernovaMain(QMainWindow):
	def __init__(self):
		super().__init__()
		uic.loadUi("pl_main.ui", self)
		
		self.centralwidget.setLayout(self.mainL) # set layout if we want to stretch all project
		
		self.gameFrame = PlatinumGameFrame(parent=self)
		
		
		#self.verticalLayout.insertWidget(0, self.gameNameWidget)
		
		self.gameNameWidget.setVisible(False)
		self.tableShowed = False 
		
		self.pbStart.clicked.connect(self.startGame)
		self.pbScores.clicked.connect(self.showScoresToggle)
		self.pbQuit.clicked.connect(sys.exit)
		

	def startGame(self, _):
		self.gameFrame.setFocus()
		self.gameFrame.startTimers()
	
	def showScoresToggle(self, _): #shows scores
		if self.tableShowed:
			self.gameNameWidget.setVisible(False)
			self.tableShowed = False
			return
		self.gameNameWidget = PlatinumScoreTable()
		self.gameNameWidget.setVisible(True)
		self.tableShowed = True
		

def main():
	app = QApplication(sys.argv)
	window = PlatinumSupernovaMain()
	window.show()
	sys.exit(app.exec_())

if __name__ == "__main__":

	main()
