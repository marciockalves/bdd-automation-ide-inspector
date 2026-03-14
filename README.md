# 🤖 Feature Editor Pro: Automação BDD Assistida por IA

O **Feature Editor Pro** é um ambiente de desenvolvimento integrado (IDE) focado em testes de comportamento (BDD). Ele une o poder do **Playwright** com a inteligência de modelos de linguagem (LLMs) locais para transformar descrições em português em scripts de automação funcionais.

---

## 🌟 O Conceito: Semantic Mapping (Mapeamento Semântico)

Diferente de ferramentas de captura comuns (*record and playback*), este projeto utiliza uma técnica avançada de **Mapeamento Semântico**. 

O fluxo não apenas "grava" o clique, mas compreende a **intenção**:
1. **Extração:** O sistema "limpa" o HTML da página, mantendo apenas elementos interativos (botões, inputs, links).
2. **Normalização:** Steps em português são traduzidos internamente para o padrão Gherkin.
3. **Casamento (Matching):** A IA (Ollama) recebe a intenção do usuário (ex: *"quero logar"*) e a lista de elementos reais, decidindo qual `id`, `name` ou `class` melhor atende ao comando.
4. **Resiliência:** Como o mapeamento é baseado no significado do elemento, os testes tornam-se menos quebráveis por mudanças simples de layout.



---

## 🛠️ Arquitetura Técnica

### Motor de IA Local
- **Ollama:** Executa modelos como **Llama 3** ou **Mistral** localmente.
- **Integração:** Comunicação via API REST (porta 11434).

### Tecnologias Core
- **Frontend:** PySide6 (Qt para Python).
- **Navegador Interno:** QtWebEngine (Chromium).
- **Automação:** Playwright para execução e manipulação do browser.
- **Gerenciamento:** `uv` para pacotes Python e `make` para automação de tarefas.

---

## ⚙️ Configuração do Ambiente Híbrido

O projeto detecta automaticamente se você está operando em seu ambiente Linux ou macOS.

### 🐧 No Linux (Fedora + NVIDIA RTX)
Para utilizar o poder da sua GPU NVIDIA de 8GB:
1. Navegue até a pasta `docker/`.
2. Execute o orquestrador:
   ```bash
   docker compose -f docker-compose.nvidia.yml up -d

# 🤖 Feature Editor Pro: Automação BDD Assistida por IA

IDE de automação para transformar requisitos em português em scripts **Playwright** funcionais utilizando **IA Local (Ollama)**.

---

## 🌟 O Conceito: Semantic Mapping
Este projeto utiliza **Mapeamento Semântico** para identificar elementos HTML. Em vez de seletores estáticos que quebram facilmente, a IA analisa o contexto do step (ex: *"Clico no botão de login"*) e encontra o elemento mais provável no DOM simplificado da página.

---

## ⚙️ Gestão de IA (Ollama)

O projeto suporta três modos de operação para o motor de IA, gerenciados via `Makefile`:

### 1. Linux com GPU NVIDIA (Fedora)
Utiliza Docker com suporte a CUDA para máxima performance na sua RTX.
- **Subir:** `make ai-up-nvidia`
- **Descer:** `make ai-down-nvidia`

### 2. macOS Nativo (Recomendado para M4)
Aproveita a aceleração **Metal** e a Memória Unificada de 24GB do seu Mac Mini M4.
- **Configurar:** `make ai-setup-mac` (instala via Homebrew)
- **Rodar:** O comando `make run-ui` já inicia o serviço automaticamente no Mac.

### 3. macOS via Docker
Caso prefira rodar isolado em container no Mac.
- **Subir:** `make ai-up-mac-docker`
- **Descer:** `make ai-down-mac-docker`

---

## 📖 Comandos Rápidos

| Comando | Função |
| :--- | :--- |
| `make setup` | Instala dependências de Python e Browsers. |
| `make run-ui` | Abre o editor principal. |
| `make ai-up-nvidia` | Inicia IA no Linux com suporte a GPU. |
| `make ai-setup-mac` | Instala Ollama nativo no macOS. |
| `make test` | Executa a suíte de testes BDD (Behave). |
| `make clean` | Remove arquivos temporários e caches. |

---

## 🛠️ Requisitos de Sistema
- **Linux:** Driver NVIDIA + NVIDIA Container Toolkit instalado.
- **Mac:** Homebrew instalado (para o modo nativo).
- **Python:** Gerenciado via `uv`.

### ⚠️ Estabilidade em Linux (NVIDIA)
Se a aplicação fechar subitamente (Error 139), o sistema está enfrentando um conflito de driver com o Chromium. O comando `make run-ui` utiliza a flag `--disable-gpu` para mitigar isso. Em hardware NVIDIA, a renderização via software é recomendada para o Inspetor BDD para evitar Segmentation Faults durante a captura do DOM.

Desenvolvido por **Marcio Alves**.

