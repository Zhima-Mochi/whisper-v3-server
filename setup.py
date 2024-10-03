from setuptools import setup

setup(
    name='whisper-v3',
    version='1.0',
    py_modules=['main'],
    entry_points={
        'console_scripts': [
            'whisper-v3 = main:main',
        ],
    },
)
