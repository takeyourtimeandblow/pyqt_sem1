import pl_const as cns

class Entity():
	def __init__(self, e_id=-1, hp=10, x=0, y=0, dmg=25):
		self.e_id = e_id
		self.hp = hp
		self.x = x
		self.y = y
		self.dmg = dmg
		

	def is_alive(self):
		return self.hp > 0
	
	def take_damage(self, attacker):
		if (self.e_id == cns.ENEMY and attacker.e_id == cns.ENEMY_BULLET):
			return -1
		self.hp -= attacker.dmg
		return 0