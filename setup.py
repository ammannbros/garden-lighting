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
    install_requires=['Flask', 'Flask-Assets', 'pyScss', 'smbus-cffi'],
    scripts=['scripts/garden-lighting'],
)
