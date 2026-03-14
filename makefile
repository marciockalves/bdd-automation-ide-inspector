# Variáveis
PYTHON = uv run python
PLAYWRIGHT = uv run playwright
OLLAMA_MODEL = llama3

# Caminhos dos Docker Compose
DOCKER_NVIDIA = containers/nvidia/docker-compose.yaml
DOCKER_MAC = containers/mac/docker-compose.yaml

.PHONY: help install setup update run-ui clean test ai-setup-mac ai-run-mac ai-up-nvidia ai-down-nvidia ai-up-mac-docker ai-down-mac-docker

help: ## Exibe esta ajuda
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Instala as dependências do projeto usando uv
	uv sync

setup: install ## Detecta o SO e instala dependências + Playwright
	@echo "🔍 Detecting Operating System..."
	@OS=$$(uname -s); \
	if [ "$$OS" = "Darwin" ]; then \
		echo "🍎 macOS detected. Installing Playwright browsers..."; \
		$(PLAYWRIGHT) install chromium; \
	elif [ "$$OS" = "Linux" ]; then \
		if [ -f /etc/fedora-release ]; then \
			echo "🎩 Fedora detected. Installing system dependencies via DNF..."; \
			sudo dnf install -y libicu libjpeg-turbo libwoff gstreamer1.0-libav; \
			$(PLAYWRIGHT) install chromium; \
		else \
			echo "🐧 Linux detected. Installing Playwright..."; \
			$(PLAYWRIGHT) install --with-deps chromium; \
		fi \
	fi
	@echo "✅ Setup complete!"

ai-setup-mac: ## (macOS Nativo) Instala Ollama e baixa o modelo
	@echo "🚀 Setting up Ollama for macOS..."
	@if ! command -v ollama >/dev/null 2>&1; then brew install --cask ollama; fi
	@ollama serve > /dev/null 2>&1 & sleep 5 && ollama pull $(OLLAMA_MODEL)
	@echo "✅ AI Setup complete!"

ai-run-mac: ## (macOS Nativo) Garante que o Ollama está rodando
	@pgrep -x "ollama" > /dev/null || (open -a Ollama &)

ai-up-nvidia: ## (Linux/NVIDIA) Sobe o container Ollama com GPU CUDA
	@echo "🟢 Starting Ollama NVIDIA Container..."
	docker compose -f $(DOCKER_NVIDIA) up -d
	docker exec -it ollama_nvidia ollama pull $(OLLAMA_MODEL)

ai-down-nvidia: ## (Linux/NVIDIA) Para o container NVIDIA
	docker compose -f $(DOCKER_NVIDIA) down

ai-up-mac-docker: ## (macOS/Docker) Sobe o container Ollama no Mac
	@echo "🟢 Starting Ollama Mac Docker Container..."
	docker compose -f $(DOCKER_MAC) up -d
	docker exec -it ollama_mac ollama pull $(OLLAMA_MODEL)

ai-down-mac-docker: ## (macOS/Docker) Para o container Mac
	docker compose -f $(DOCKER_MAC) down

run-ui: ## Inicia a interface gráfica com segurança máxima contra Segfault
	@OS=$$(uname -s); \
	if [ "$$OS" = "Darwin" ]; then \
		make ai-run-mac; \
		$(PYTHON) main.py; \
	elif [ "$$OS" = "Linux" ]; then \
		echo "🚀 Iniciando no Linux em modo de compatibilidade estável..."; \
		export QTWEBENGINE_DISABLE_SANDBOX=1; \
		export QT_XCB_GL_INTEGRATION=none; \
		$(PYTHON) main.py --disable-gpu --disable-software-rasterizer --no-sandbox; \
	fi

clean: ## Limpa caches e arquivos temporários
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf gerados/*.py