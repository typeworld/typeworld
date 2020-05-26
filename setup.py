from setuptools import setup, find_packages

setup(
  name = 'typeworld',         # How you named your package folder (MyLib)
  version = '0.2.0a4',
  license='apache-2.0',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'This module hosts the Type.World JSON Protocol definitions in `typeworld.api` and the headless client module in `typeworld.client`, as well as various tools.',   # Give a short description about your library
  author = 'Type.World',                   # Type in your name
  author_email = 'hello@type.world',      # Type in your E-Mail
  url = 'https://github.com/typeworld/typeworld',   # Provide either the link to your github or to your website
  keywords = ['fonts'],   # Keywords that define your package best
  install_requires=[            # I get to this in a second
          'markdown2',
          'semver',
          'certifi',
          'keyring',
          'deepdiff',
          'pyobjc',

      ],
  classifiers=[
    'Development Status :: 4 - Beta',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    "Environment :: Console",
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: Apache Software License',   # Again, pick a license
    "Operating System :: OS Independent",
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    "Topic :: Text Processing :: Fonts",
  ],
  entry_points={
    'console_scripts': [
      "validateTypeWorldEndpoint = typeworld.tools.validator:main",
    ]
  },
  package_dir={'': 'Lib'},
  packages=find_packages("Lib"),
)