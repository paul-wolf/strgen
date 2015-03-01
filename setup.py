#!python
from distutils.core import setup

description='Generate randomized strings of characters using a template'

# try:
#     long_description = pypandoc.convert('README.md', 'rst')    
# except (IOError, OSError):
#     print('check that you have installed pandoc properly and that README.md exists!')
#     long_description = description

with open('README.txt') as file:
    long_description = file.read()

setup(name='StringGenerator',
      description=description,
      url='https://github.com/paul-wolf/strgen',
      author='Paul Wolf',
      author_email='paul.wolf@yewleaf.com',
      version='0.1.5',
      #version = module.__version__,
      packages=['strgen',],
      license='BSD',
      long_description=long_description,
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.4',
          'Topic :: Software Development :: Libraries :: Python Modules',
          ],
  )

