from Entity import *

class Category(Entity):
   _fields   = ['title']
   _parents  = []
   _children = ['article']
   _siblings = []


class Article(Entity):
   _fields   = ['text', 'title']
   _parents  = ['category']
   _children = []
   _siblings = ['tag']


class Tag(Entity):
   _fields   = ['value']
   _parents  = []
   _children = []
   _siblings = ['article']

