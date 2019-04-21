from setuptools import setup, find_packages

setup(
    name='garden-lighting',
    version='0.1',
    packages=find_packages(),
    url='https://github.com/ammannbros/garden-lighting',
    license='',
    author='holzi, max',
    author_email='max@maxammann.org',
    description='',
    install_requires=['Flask==1.0.2',
                      'Flask-Script==2.0.6',
                      'Flask-Bower==1.3.0',
                      'tornado==6.0.2',
                      'smbus-cffi==0.5.1 ',
                      'wiringpi==2.46.0',
                      'tinydb==3.13.0'],
    scripts=['scripts/garden-lighting'],
    include_package_data=True,
)
