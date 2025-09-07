from setuptools import setup, find_packages

setup(
    name='mypass', # O nome do seu pacote
    version='0.1.0',
    packages=find_packages(), # Encontra a pasta 'mypass' automaticamente

    # A MÁGICA ACONTECE AQUI!
    entry_points={
        'console_scripts': [
            # Leia-se: "Crie um comando chamado 'mypass' que,
            # quando executado, vai chamar o objeto 'app'
            # de dentro do arquivo 'mypass/cli.py'"
            'mypass = script.cli:app',
        ],
    },
)