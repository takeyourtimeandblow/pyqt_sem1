import sys
from random import randint
from PyQt5.QtWidgets import (QApplication, QWidget, QFrame) 
from PyQt5.QtCore import QTimer, Qt, QUrl

from PyQt5.QtGui import QPainter, QColor, QPen, QPixmap

from PyQt5 import uic, QtMultimedia

import pl_const as cns
#from pl_const import PATH

from pl_entity import Entity
from pl_player import Player
from pl_enemy import Enemy
from pl_game_over_dialog import PlatinumGameOverDialog

player_bullets = []
enemies = []
enemy_bullets = []

def resource_path(relative_path):
        """Get absolute path to resource, works for dev and for PyInstaller"""
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

#function is taken from https://stackoverflow.com/questions/54556158/keypressevent-in-pyqt (modified)
def check_intersection(el, rect):
	#print (el, rect)
	return rect[0] <= el[0] <= rect[2] and rect[1] <= el[1] <= rect[3] or \
		   rect[0] <= el[2] <= rect[2] and rect[1] <= el[1] <= rect[3] or \
		   rect[0] <= el[0] <= rect[2] and rect[1] <= el[3] <= rect[3] or \
		   rect[0] <= el[2] <= rect[2] and rect[1] <= el[3] <= rect[3]

class PlatinumGameFrame(QWidget):
	def __init__(self, parent=None):
		super().__init__(parent)
		uic.loadUi("pl_frame.ui", self)
		
		self.dx = 0
		self.dy = 0
		self.max_speed = 7
		self.session_score = 0
		self.player = QtMultimedia.QMediaPlayer()
		
		self.key_states = {Qt.Key_Up: False, Qt.Key_Down: False, Qt.Key_Left: False, Qt.Key_Right: False, Qt.Key_Space: False}
		
		self.hero = Player(x=self.heroTexture.x(), y=self.heroTexture.y())

		self.timer = QTimer(self)
		self.timerEnemy = QTimer(self)
		self.timerFireCoolDownPlayer = QTimer(self)
		self.timerFireCoolDownEnemy = QTimer(self)
		self.timerRespawnEnemies = QTimer(self)
		self.timerDamageImmunity = QTimer(self)
		
		self.timer.timeout.connect(self.thread)
		self.timer.timeout.connect(self.update_bullets_state)
		self.timerEnemy.timeout.connect(self.update_enemy_position) 
		self.timerFireCoolDownPlayer.timeout.connect(self.fireCoolDownFunc)
		self.timerFireCoolDownEnemy.timeout.connect(self.enemyShoot)
		self.timerRespawnEnemies.timeout.connect(self.respawnEnemies)
		
		self.timerDamageImmunity.timeout.connect(self.setPlayerInvincible)
		
		
		QApplication.instance().focusChanged.connect(self.handleFocusChanged)
		
		self.buffer = QPixmap(self.size())
		
		self.fireCoolDowned = True
		self.game_is_over = False
		if not parent:
			self.startTimers()
			
	def startTimers(self):
		if self.game_is_over:
			return
		self.timer.start(17) # 60 fps
		self.timerEnemy.start(100)
		self.timerFireCoolDownPlayer.start(self.hero.fire_rate * 1000)
		self.timerFireCoolDownEnemy.start(1 * 1000)
		self.timerRespawnEnemies.start(2 * 1000)
		
	def stopTimers(self):
		self.timer.stop()
		self.timerEnemy.stop()
		self.timerFireCoolDownPlayer.stop()
		self.timerFireCoolDownEnemy.stop()
		self.timerRespawnEnemies.stop()
		
	def handleFocusChanged(self, old_widget, new_widget):
		if not self.hasFocus():
			self.stopTimers()
			self.key_states[Qt.Key_Up] = False
			self.key_states[Qt.Key_Down] = False
			self.key_states[Qt.Key_Left] = False
			self.key_states[Qt.Key_Right] = False
		else:
			self.startTimers()
				
		if old_widget:
			print(f"Focus lost by: {old_widget.objectName() if old_widget.objectName() else old_widget.__class__.__name__}")
		if new_widget:
			print(f"Focus gained by: {new_widget.objectName() if new_widget.objectName() else new_widget.__class__.__name__}")
		
		
	def keyPressEvent(self, event):
		if event.key() in self.key_states:
			self.key_states[event.key()] = True

	def keyReleaseEvent(self, event):
		if event.isAutoRepeat():
			return
		if event.key() in self.key_states:
			self.key_states[event.key()] = False

	def thread(self):
		self.update_player_position()
		
	def fireCoolDownFunc(self): #When player can fire again
		self.fireCoolDowned = True
	
	def update_player_position(self):
		if self.key_states[Qt.Key_Space]: # space is fire
			self.shoot()
		if self.key_states[Qt.Key_Up]: self.dy = -self.max_speed
		if self.key_states[Qt.Key_Down]: self.dy = self.max_speed
		if self.key_states[Qt.Key_Left]: self.dx = -self.max_speed
		if self.key_states[Qt.Key_Right]: self.dx = self.max_speed
		if not self.key_states[Qt.Key_Left] and not self.key_states[Qt.Key_Right]: self.dx = 0
		if not self.key_states[Qt.Key_Up] and not self.key_states[Qt.Key_Down]: self.dy = 0
		
		x = self.heroTexture.x() + int(self.dx)
		y = self.heroTexture.y() + int(self.dy)
		if x in range(self.width()-self.heroTexture.size().width()) and y in range(self.height()-self.heroTexture.size().height()):
			self.heroTexture.move(x, y)
			self.hero.x = x
			self.hero.y = y
		else:
			if x not in range(self.width()-self.heroTexture.size().width()):
				self.dx = 0
				x = self.heroTexture.x() + int(self.dx)
			if y not in range(self.height()-self.heroTexture.size().height()):
				self.dy = 0
				y = self.heroTexture.y() + int(self.dy)
			self.heroTexture.move(x, y)
			self.hero.x = x
			self.hero.y = y
			
		if not self.hero.invincible: # checks if player is invincible and if they touched Enemy bullet
			for b in enemy_bullets:
				if check_intersection([b.x, b.y, b.x+10, b.y+10], [self.hero.x, self.hero.y, self.hero.x+self.heroTexture.size().width(), self.hero.y+self.heroTexture.size().height()]):
					self.hero.take_damage(b)
					if not self.hero.is_alive():
						self.game_over()
					self.hero.invincible = True # gives player invincibilty after being hit
					self.heroTexture.setStyleSheet("background-color: transparent;")
					self.timerDamageImmunity.start(2000)
	
	def shoot(self):
		if self.fireCoolDowned:
			player_bullets.append(Entity(cns.PLAYER_BULLET, x=self.hero.x, y=self.hero.y)) #adds info about bullets on screen
			
			media = QUrl.fromLocalFile('shot.mp3') # sound of fire
			content = QtMultimedia.QMediaContent(media)
			self.player.setMedia(content)
			self.player.play()

			self.fireCoolDowned = False
		
	def enemyShoot(self):
		if enemies:
			for e in enemies:
				enemy_bullets.append(Entity(cns.ENEMY_BULLET, x=e[0].x, y=e[0].y))
				media = QUrl.fromLocalFile('shot_enemy.mp3')
				content = QtMultimedia.QMediaContent(media)
				self.player.setMedia(content)
				self.player.play()
		
	def update_bullets_state(self):
			
		self.buffer.fill(QColor("white"))
		painter = QPainter(self.buffer)
		painter.setPen(QPen(QColor(0, 255, 0), 5))
		
		if player_bullets:
			del_bullets = []
			for b in range(len(player_bullets)):
				if 0 <= player_bullets[b].x < self.width() and 0 <= player_bullets[b].y < self.height():
					painter.drawEllipse(player_bullets[b].x, player_bullets[b].y, self.hero.power, self.hero.power)
					player_bullets[b].y -= 10
				else:
					del_bullets.append(b)
			for i in sorted(del_bullets, reverse=True):
				del player_bullets[i]
		
		painter.setPen(QPen(QColor(255, 0, 0), 5))
		if enemy_bullets:
			del_en_bulltes = []
			for b in range(len(enemy_bullets)):
				if 0 <= enemy_bullets[b].x < self.width() and 0 <= enemy_bullets[b].y < self.height():
					painter.drawEllipse(enemy_bullets[b].x, enemy_bullets[b].y, 10, 10)
					enemy_bullets[b].y += 10
				else:
					del_en_bulltes.append(b)
			for i in sorted(del_en_bulltes, reverse=True):
				del enemy_bullets[i]
				
		self.update()

	def paintEvent(self, event):
		super().paintEvent(event)

		painter = QPainter(self)
		painter.drawPixmap(self.rect(), self.buffer)
		painter.drawText(10, 10, f"HITPOINTS: {self.hero.hp}")
		painter.drawText(10, 30, f"SCORE: {self.session_score}")
		
		
	def update_enemy_position(self):
		if not enemies:
			return
		
		del_ens = []
		for i, e in enumerate(enemies):
			if not e[1]:
				e[1] = QFrame(self) 
				e[1].resize(64,64)
				e[1].setStyleSheet(f"background-image: url(\"enemyTexture.png\");")
				e[1].move(e[0].x, e[0].y)
				e[1].show()
			else:
				dx = e[0].x + randint(-15, 15)
				dy = e[0].y + randint(-15, 15)
				if 0 <= dx < self.width():
					e[0].x = dx
				if 0 <= dy < self.height():
					e[0].y = dy
				e[1].move(e[0].x, e[0].y)
			if player_bullets:
				for b in player_bullets: # check if enemy touched player's bullet
					if check_intersection([b.x, b.y, b.x+self.hero.power, b.y+self.hero.power], [e[1].x(), e[1].y(), e[1].x()+e[1].size().width(), e[1].y()+e[1].size().height()]):
						e[0].take_damage(b)
						if not e[0].is_alive():
							self.session_score += 100
							del_ens.append(i)
							e[1].deleteLater()
							
		for i in sorted(del_ens, reverse=True):
			del enemies[i][-1]
			del enemies[i][-1]
			del enemies[i]
			
	
	def respawnEnemies(self):
		enemies.append([Enemy(x=randint(40, 240), y=randint(40, 240)), None])
		
	def setPlayerInvincible(self):
		self.hero.invincible = False
		print(f"background-image: url(\"heroTexture.png\");")
		self.heroTexture.setStyleSheet(f"background-image: url(\"heroTexture.png\");")
		self.timerDamageImmunity.stop()
		
	def game_over(self): # The game is over
		self.game_is_over = True
		self.stopTimers()
		
		media = QUrl.fromLocalFile('gameover.mp3')
		content = QtMultimedia.QMediaContent(media)
		self.player.setMedia(content)
		self.player.play()
		
		go_dialog = PlatinumGameOverDialog(self.session_score)
		go_dialog.exec_()
		
def main():
	app = QApplication(sys.argv)
	window = PlatinumGameFrame()
	window.show()
	sys.exit(app.exec_())

if __name__ == "__main__":
	main()
