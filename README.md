ORM
===

Python database management system for PosthgreSQL.

To use ORM you simply have to structure your database in the yaml file.
A yaml file have to look like(structure.yaml):
<pre><code>Article:
  fields:
      title: varchar(50)
      text: text
  relations:
      Category: one
      Tag: many

Category:
  fields:
      title: varchar(50)
  relations:
      Article: many

Tag:
  fields:
      value: varchar(50)
  relations:
      Article: many</code></pre>
After, you generate python classes(in models.py) by using generator.py, which is in the project. Python classes allows you to manage your entities in database. 
