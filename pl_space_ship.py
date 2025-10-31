from pl_entity import Entity

import pl_const as cns

class SpaceShip(Entity):
	def __init__(self, e_id, hp=10, x=0, y=0, dmg=25, fire_rate=1):
		super().__init__(e_id, hp, x, y, dmg)
		
		#self.dmg = 25
		self.fire_rate = fire_rate
		
	def attack(self, target):
		return target.take_damage(self)