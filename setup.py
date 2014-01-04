#!python
from distutils.core import setup

with open('README.txt') as file:
    long_description = file.read()

setup(name='StringGenerator',
      description='Generate randomized strings of characters using a template',
      url='https://github.com/paul-wolf/strgen',
      author='Paul Wolf',
      author_email='paul.wolf@yewleaf.com',
      version='0.1.2',
      packages=['strgen',],
      license='BSD',
      long_description=long_description,
  )

