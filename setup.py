from setuptools import setup, find_packages

setup(
    name='garden-lighting',
    version='0.1',
    packages=find_packages(),
    url='',
    license='',
    author='holzi, max',
    author_email='',
    description='',
    install_requires=['Flask==0.10.1',
                      'Flask-Script==2.0.5',
                      'Flask-libsass==1.1.0',
                      'Flask-Bower==1.1.1',
                      'tornado==4.2',
                      'smbus-cffi==0.4.1',
                      'wiringpi2==1.1.1',
                      'tinydb==3.2.0'],
    scripts=['scripts/garden-lighting'],
    include_package_data=True,
)
