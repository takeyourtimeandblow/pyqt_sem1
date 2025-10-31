import pl_const as cns

from pl_space_ship import SpaceShip

class Enemy(SpaceShip):
	def __init__(self, hp=25, x=0, y=0, dmg=25, fire_rate=1):
		super().__init__(cns.ENEMY, hp, x, y)
    