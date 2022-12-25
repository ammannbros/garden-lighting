from setuptools import setup, find_packages

setup(
    name='garden-lighting',
    version='0.2',
    packages=find_packages(),
    url='',
    license='',
    author='holzi, max',
    author_email='',
    description='',
    install_requires=['Flask==2.2.2',
                      'Flask-Bower==1.1.1',
                      'click==8.1.3',
                      'waitress==2.1.2',
                      'smbus-cffi',
                      'tinydb==3.2.0'],
    scripts=['scripts/garden-lighting'],
    include_package_data=True,
)
