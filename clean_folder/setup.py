from setuptools import setup, find_namespace_packages

setup(name='clean_folder',
      version='0.1',
      description='clean folder tool v0.1',
      url='http://github.com/opawlyuk/clean_folder',
      author='Olena Pawliuk',
      author_email='opawlyuk@gmail.com',
      license='MIT',
      packages=find_namespace_packages(),
      entry_points={'console_scripts': ['clean = clean_folder.clean:main']}
      )
