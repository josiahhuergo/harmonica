del source\harmonica*.rst
del source\modules*.rst
del build\html\* 
call sphinx-apidoc -M -o source ../harmonica
call make html