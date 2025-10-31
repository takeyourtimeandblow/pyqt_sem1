import sys
from PyQt5.QtWidgets import (QDialog)
from PyQt5 import uic

import pandas as pd

#from pl_const import PATH

class PlatinumGameOverDialog(QDialog):
	def __init__(self, score):
		super().__init__()
		
		self.score = score
		
		uic.loadUi('pl_game_over_dialog.ui', self)
		self.label.setText(f"""Game Over! Score - {score}
Enter Your nickname""")

		self.lineEdit.setFocus()
	
	def accept(self): #User presed OK. Their score will be saved to scores.csv
		input_file = 'scores.csv'
		output_file = 'scores.csv'

		# Read the CSV into a pandas DataFrame
		df = pd.read_csv(input_file)
		
		new_data = {'NAME': [self.lineEdit.text()], 'HISCORE': [self.score]}
		new_row_df = pd.DataFrame(new_data)
		
		df = pd.concat([df, new_row_df], ignore_index=True)
		self.close()
		

		# Save the modified DataFrame back to a CSV file
		df.to_csv(output_file, index=False)
