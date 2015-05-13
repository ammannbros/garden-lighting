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
    install_requires=['Flask', 'Flask-libsass', 'Flask-Bower',
                      'RPi.GPIO', 'smbus-cffi', 'Flask-Script'],
    scripts=['scripts/garden-lighting'],
    include_package_data=True,
)
