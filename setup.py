from setuptools import setup

setup(
    name='cslang-transpiler',
    version='1.0',
    py_modules=['transpiler'],
    install_requires=[
        'keyboard',
    ],
    entry_points={
        'console_scripts': [
            'transpilecsl = transpiler:main',
        ],
    },
)
