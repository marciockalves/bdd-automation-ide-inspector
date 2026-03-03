# Variáveis
PYTHON = uv run python
PLAYWRIGHT = uv run playwright

.PHONY: help install setup update run-ui clean test

help: ## Exibe esta ajuda
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Instala as dependências do projeto usando uv
	uv sync

setup: install ## Detect OS and install dependencies + Playwright browsers
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
		elif [ -f /etc/debian_version ] || [ -f /etc/lsb-release ]; then \
			echo "🐧 Ubuntu/Debian detected. Installing system dependencies via APT..."; \
			sudo $(PLAYWRIGHT) install-deps chromium; \
			$(PLAYWRIGHT) install chromium; \
		else \
			echo "❓ Linux distribution unknown. Attempting generic install..."; \
			$(PLAYWRIGHT) install --with-deps chromium; \
		fi \
	fi
	@echo "✅ Setup complete!"

update: ## Atualiza as dependências
	uv lock --upgrade

run-ui: ## Inicia a interface gráfica (BDDForm)
	$(PYTHON) main.py

test: ## Executa todos os testes BDD com Behave
	uv run behave

codegen: ## Abre o gerador de código do Playwright manualmente (URL padrão)
	$(PLAYWRIGHT) codegen https://www.google.com

clean: ## Limpa caches e arquivos temporários
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	rm -rf gerados/*.py

test-clean: ## Remove relatórios de testes antigos
	rm -rf .pytest_cache
	rm -f test-results.xml