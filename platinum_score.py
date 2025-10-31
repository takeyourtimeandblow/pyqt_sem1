import sys
from PyQt5.QtWidgets import (QWidget,
							QApplication, QHeaderView)
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import QSortFilterProxyModel, QRegularExpression, Qt
from PyQt5 import uic

import pandas as pd

def read_data(fname):
	return pd.read_csv(fname).to_dict()
 
class PlatinumScoreTable(QWidget):
	def __init__(self, parent=None):
		super().__init__(parent)
		uic.loadUi("pl_score.ui", self)
 
		self.createTable()

		self.setLayout(self.verticalLayout)
 
		#Show window
		#self.show()
 
	#Create table
	def createTable(self):
		self.data = read_data('scores.csv')
		
		rows = len(max(self.data.values(), key=len))
		cols = len(self.data)

		model = QStandardItemModel(cols, rows)

		#Row count
		model.setRowCount(rows)

		#Column count
		model.setColumnCount(cols)
		model.setHorizontalHeaderLabels(self.data.keys())
		
		for x, (name, col) in enumerate(self.data.items()):
			for y, row in enumerate(col.values()):
				if isinstance(row, float):
					row = str(row)
					row = row[0:row.find('.')]
				if isinstance(row, int):
					row = str(row)
				model.setItem(y,x, QStandardItem(row))


		self.table_view.setModel(model)

		self.table_view.horizontalHeader().setStretchLastSection(True)
		self.table_view.horizontalHeader().setSectionResizeMode(
			QHeaderView.Stretch)
 
if __name__ == '__main__':
	app = QApplication(sys.argv)
	ex = PlatinumScoreTable()
	ex.show()
	sys.exit(app.exec_())

