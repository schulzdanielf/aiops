
# Implantar aplicação no cluster
deploy:
	@kubectl apply -f k8s/

# Verificar status da aplicação
status:
	@kubectl get pods
	@kubectl get services
	@kubectl get pvc
	@kubectl get pv

# Diretório do código fonte
SRC_DIR = .

# Limpar arquivos compilados Python e cache
clean:
	find $(SRC_DIR) -type f -name "*.py[co]" -delete
	find $(SRC_DIR) -type d -name "__pycache__" -delete 
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .mypy_cache
	rm -rf .pytest_cache

# Formatar código usando black
format:
	black .

# Lint com flake8
lint:
	flake8 --config=configs/.flake8 .

# Verificar tipos com mypy
mypy:
	mypy $(SRC_DIR)

# Executar testes com pytest
test:
	pytest --cov=app

# Instalar dependências do projeto
install:
	pip install -r requirements.txt

# Atualizar dependências do projeto
update:
	pip install --upgrade -r requirements.txt

# Recriar ambiente de desenvolvimento (exclui e reinstala dependências)
rebuild: clean install

# Adicionar arquivos ao git
git:
	git add .
	git status

# Acessa o diretório de filmes e cria uma nova imagem docker
filmes:
	cd apps/app_teste && docker build -t app-filmes .
	kubectl delete pod -l app=app-filmes

simulator:
	cd apps/simulator && docker build -t simulator .
	kubectl delete pod -l app=simulator

logs_filmes:
	kubectl logs -l app=app-filmes

# Tarefas padrões
.PHONY: clean format lint mypy test install update rebuild