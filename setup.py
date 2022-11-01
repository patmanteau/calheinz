from setuptools import setup, find_packages

setup(
    name='calheinz',
    version='0.0.1',
    description='An iCal change detector',
    packages=['calheinz'],
    package_dir={'calheinz': 'calheinz'},
    include_package_data=True,
    py_modules=['calheinz'],
    install_requires=[
        'Click',
    ],
    entry_points={
        'console_scripts': [
            'calheinz = calheinz.cli:entry'
        ]
    }
)