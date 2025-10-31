import pl_const as cns

from pl_space_ship import SpaceShip

class Player(SpaceShip):
	def __init__(self, hp=100, x=0, y=0, dmg=25, fire_rate=1):
		super().__init__(cns.PLAYER, hp, x, y)
		self.power = 20
		self.invincible = False
	