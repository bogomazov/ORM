from Entity import *

class Post(Entity):
   _fields   = ['title', 'text']
   _parents  = ['category']
   _children = []
   _siblings = {'tags': 'Tag'}
   
   
class Category(Entity):
   _fields   = ['title']
   _parents  = []
   _children = {'posts': 'Post'}
   _siblings = {}
   
   
class Tag(Entity):
   _fields   = ['name']
   _parents  = []
   _children = []
   _siblings = {'articles': 'Article'}

