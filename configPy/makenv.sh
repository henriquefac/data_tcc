#!b/bin/bash

echo "Iniciando projeto"


# verificar se na raiz do projeto existe arquivo files

if [ ! -d "files" ]; then
	echo "Criando diretório de arquivos"
	
	mkdir files
	touch files/data_dir.txt
	echo "Diretório reservado para os dados necessários" >> files/data_dir.txt
fi

if [ ! -d "src" ]; then
	echo "Criando diretório para scripts"

	mkdir src
	touch src/data_dir.txt
	echo "Diretório reservado para os dados necessários" >> src/data_dir.txt
fi


if [ ! -d ".venv" ]; then
	echo "Criando ambiente de prgramação python"
	python3 -m venv .venv

	echo "export PYTHONPATH=$(pwd)" >> .venv/bin/activate
	echo "export JUPYTER_PATH=$(pwd)" >> .venv/bin/activate

	source .venv/bin/activate

	pip install python-dotenv
	
	if [ -f "requirements.txt" ]; then
		pip install -r requirements.txt
	else
		echo "Aviso: requirements.txt não encontrado. Nenhum pacote foi instalado"
	fi

	deactivate
fi

source .venv/bin/activate




