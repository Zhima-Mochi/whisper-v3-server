from setuptools import setup, find_packages

setup(
    name='whisper',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'torch>=2.0.0',
        'transformers>=4.30.0',
        'datasets>=2.12.0',
        'numpy>=1.20.0',
        'tqdm>=4.65.0',
    ],
    extras_require={
        'audio': [
            'librosa>=0.10.0',
            'soundfile>=0.12.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'whisper-v3 = v3.main:main',
        ],
    },
    description='A Python package for Whisper V3 speech recognition',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)
