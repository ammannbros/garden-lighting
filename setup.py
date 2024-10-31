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
    install_requires=['Flask==3.0.3',
                      'Werkzeug>=3.0.0',
                      'waitress==3.0.1',
                      'smbus-cffi',
                      'tinydb==3.2.0',
                      'statsd==4.0.1',
                      ],
    scripts=['scripts/garden-lighting'],
    include_package_data=True,
)
