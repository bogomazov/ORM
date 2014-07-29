import yaml

class YamlSchemaError(Exception):
    pass
class EntityError(Exception):
	pass

CLASS_TEMPLATE = """
class {name}(Entity):
   _fields   = [{fields}]
   _parents  = [{parents}]
   _children = [{children}]
   _siblings = [{siblings}]

"""

class Generator(object):
	def __init__(self, yamlfile, entity):
		if entity[len(entity)-3:len(entity)] != ".py":
			raise EntityError('Wrong entity file format\n Must to be a pythonic format.')

		self.__models = "from {entity} import *\n".format(entity=entity[:len(entity)-3])
		file = open(yamlfile, 'r')
		self.__schema = yaml.load(file)

		self.__build_models()

	def __build_models(self):
		for entity in self.__schema:
			fields = ", ".join("'{}'".format(field) for field in self.__schema[entity]['fields'])
			parents = ""
			children = ""
			siblings = ""

			for other_entity, relation in self.__schema[entity]['relations'].items():
				reverse_relation = self.__schema[other_entity]['relations'][entity]
				if relation == 'one' and reverse_relation == 'many':
					parents += ", '{}'".format(other_entity)
				elif relation == 'many' and  reverse_relation == 'many':
					siblings += ", '{}'".format(other_entity)
				elif relation == 'many' and reverse_relation == 'one':
					children += ", '{}'".format(other_entity)
				else:
					raise YamlSchemaError('Error in ' + other_entity  + ' relation ' + reverse_relation + ', table ' + entity + ' ' + relation)
			parents = parents[2:].lower()
			siblings = siblings[2:].lower()
			children = children[2:].lower()

			self.__models += CLASS_TEMPLATE.format(name=entity, fields=fields, parents=parents, children=children, siblings=siblings)

	def dump(self, filename):
		with open(filename, 'w') as file:
			file.write(self.__models)

if __name__ == "__main__":
	gen = Generator("Structure.yaml", "Entity.py")
	gen.dump('models.py')

