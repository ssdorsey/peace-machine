from setuptools import setup, find_packages

setup(
    name="peace-machine",
    version='0.1',
    # py_modules=['hello'],
    packages=find_packages(),
    install_requires=[
        'Click',
        'transformers',
        'p_tqdm',
        'allennlp',
        'allennlp-models',
        'pandas',
        'cchardet'

        # 'Scrapy>=1.1.0',
        # Add all the required packages here
    ],
    
    entry_points={
         'console_scripts': ['peace-machine = peacemachine.commands:cli'] # Add more commands here
    },
)