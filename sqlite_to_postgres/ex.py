import sys
import os


print(a :=__file__)
print(b:= os.path.dirname(__file__))
print(c:= os.path.join(os.path.dirname(__file__), '../../..'))

print(
    d:= os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
)