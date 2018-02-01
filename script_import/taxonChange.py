from enum import Enum

class ChangeType(Enum):
	
	REFERENCED_BY_TAXREF = 0,
	NEW_VALID_TAXON = 1,
	NEW_SYNONYMOUS = 2,
	SYNONYMOUS_TO_VALID = 3,
	VALID_TO_SYNONYMOUS = 4,
	VALID_TAXON_CHANGE = 5,
	HIGHER_TAXON_CHANGE = 6,
	NO_ID_CHANGE = 7

class TaxonChanges(list) :
	"""
		This class is used to contain all the object TaxonChange which
		contain the change on data
	"""
	def __init__(self):
		self = []

	def get_all(self, change_type):
		return [taxon_change for taxon_change in self if taxon_change.change_type == change_type]

	def get_accepted_by_user(self, change_type):
		return [taxon_change for taxon_change in self if taxon_change.is_accepted_by_user]

class TaxonChange:

	def __init__(self, tup, is_additionnal_change = False):
		self.tupple = tup
		self.change_type = None
		self.is_additionnal_change = None
		self.is_updatable = True
		self.user_message = ''
		self.is_accepted_by_user = True

	def __str__(self):
		if self.change_type is not None:
			return str(self.tupple) + str(self.change_type)
		else:
			return str(self.tupple)