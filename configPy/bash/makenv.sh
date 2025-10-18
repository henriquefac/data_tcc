#!/bin/bash

echo "Iniciando projeto"

# --- Criação de Diretórios ---
echo "--- Configurando Diretórios ---"

# Verifica se o diretório 'files' existe e cria, se necessário
if [[ ! -d "files" ]]; then
	echo "Criando diretório 'files'"
	mkdir files
	touch files/data_dir.txt
	echo "Diretório reservado para dados brutos ou auxiliares" >> files/data_dir.txt
else
	echo "Diretório 'files' já existe."
fi

# Verifica se o diretório 'src' existe e cria, se necessário
if [[ ! -d "src" ]]; then
	echo "Criando diretório 'src' para scripts"
	mkdir src
	touch src/src_dir.txt
	echo "Diretório reservado para scripts e código-fonte" >> src/data_dir.txt
else
	echo "Diretório 'src' já existe."
fi


if [[ ! -d "files/output" ]]; then
	echo "Criando diretório 'files/output'"
	mkdir files/output
	touch files/output/output.txt
	echo "Diretório resevardo para os resultados do processamento" >> files/output/output.txt
else
	echo "Diretório 'files/output' já existe"
fi


# --- Configuração do Ambiente Virtual ---
echo "--- Configurando Ambiente Python (.venv) ---"

if [[ ! -d ".venv" ]]; then
	echo "Criando ambiente virtual Python (.venv)..."
	python3 -m venv .venv

	# Ativa e configura o ambiente temporariamente
	source .venv/bin/activate

	# Configura variáveis de ambiente no script de ativação do venv
	# Isso garante que a variável PYTHONPATH e JUPYTER_PATH sejam definidas sempre que o venv for ativado
	echo "" >> .venv/bin/activate
	echo "# Variáveis adicionadas pelo script de setup" >> .venv/bin/activate
	echo "export PYTHONPATH=\$(pwd)" >> .venv/bin/activate
	echo "export JUPYTER_PATH=\$(pwd)" >> .venv/bin/activate

	pip install python-dotenv # Instala pacote básico

	if [[ -f "requirements.txt" ]]; then
		echo "Instalando dependências de 'requirements.txt'..."
		pip install -r configPy/requirements.txt
		pip install -r requirements.txt
		
	else
		echo "Aviso: 'requirements.txt' não encontrado. Nenhum pacote adicional foi instalado."
	fi


	deactivate # Desativa o ambiente
else
	echo "Ambiente virtual '.venv' já existe."
fi

# Ativa o ambiente para o restante do script (incluindo o download)
echo "Ativando ambiente virtual..."
source .venv/bin/activate

echo "---"
echo "Setup concluído! O ambiente virtual está ATIVADO."
echo "Para desativar o ambiente, use: deactivate"
