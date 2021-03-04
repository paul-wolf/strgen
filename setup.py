#!python
import io
from distutils.core import setup

description = 'Generate randomized strings of characters using a template'

with io.open('README.txt', encoding='utf-8') as file:
    long_description = file.read()

setup(name='StringGenerator',
      description=description,
      url='https://github.com/paul-wolf/strgen',
      author='Paul Wolf',
      author_email='paul.wolf@yewleaf.com',
      version='0.4.1',
      packages=['strgen', ],
      license='BSD',
      long_description=long_description,
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Programming Language :: Python :: 3.9',          
          'Topic :: Software Development :: Libraries :: Python Modules',
      ],
      )
