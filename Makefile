.PHONY: help install setup dev build rebuild up down logs clean clean-all \
        quickstart setup-env check-ai-mode check-model remove-model \
        restart restart-backend restart-frontend restart-vllm restart-redis \
        ps status logs-backend logs-frontend logs-vllm logs-redis health test-wazuh info \
        dev-backend dev-frontend shell-backend shell-frontend shell-vllm shell-redis \
        lint format download-model build up-cache cache-enable cache-disable cache-clear cache-stats

# ============================================================================
# Shell + echo
# ============================================================================
SHELL := /bin/bash
ECHO  := printf "%b\n"

# ============================================================================
# Cores (portável, via tput)
# ============================================================================
TERM_COLORS := $(shell tput colors 2>/dev/null || echo 0)
ifeq ($(TERM_COLORS),0)
	CYAN    :=
	GREEN   :=
	YELLOW  :=
	RED     :=
	BLUE    :=
	MAGENTA :=
	RESET   :=
	BOLD    :=
else
	CYAN    := $(shell tput setaf 6)
	GREEN   := $(shell tput setaf 2)
	YELLOW  := $(shell tput setaf 3)
	RED     := $(shell tput setaf 1)
	BLUE    := $(shell tput setaf 4)
	MAGENTA := $(shell tput setaf 5)
	RESET   := $(shell tput sgr0)
	BOLD    := $(shell tput bold)
endif

# Default target
.DEFAULT_GOAL := help

# ============================================================================
# Help
# ============================================================================
help: ## 📚 Mostrar todos os comandos disponíveis
	@$(ECHO) ""
	@$(ECHO) "$(CYAN)╔══════════════════════════════════════════════════════════════════╗$(RESET)"
	@$(ECHO) "$(CYAN)║$(RESET)  $(BOLD)🛡️  Wazuh SCA AI Analyst - Guia de Comandos$(RESET)                $(CYAN)║$(RESET)"
	@$(ECHO) "$(CYAN)╚══════════════════════════════════════════════════════════════════╝$(RESET)"
	@$(ECHO) ""
	@$(ECHO) "$(BOLD)🚀 INÍCIO RÁPIDO:$(RESET)"
	@$(ECHO) "  $(GREEN)make quickstart$(RESET)    → Setup completo interativo"
	@$(ECHO) "  $(GREEN)make up$(RESET)            → Iniciar serviços"
	@$(ECHO) ""
	@$(ECHO) "$(BOLD)📋 COMANDOS DISPONÍVEIS:$(RESET)"
	@$(ECHO) ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk -v BLUE="$(BLUE)" -v MAGENTA="$(MAGENTA)" -v CYAN="$(CYAN)" -v YELLOW="$(YELLOW)" -v GREEN="$(GREEN)" -v RED="$(RED)" -v RESET="$(RESET)" 'BEGIN {FS = ":.*?## "}; { \
			cmd = $$1; \
			desc = $$2; \
			if (desc ~ /^🔧/) printf "  " BLUE "%-18s" RESET " %s\n", cmd, desc; \
			else if (desc ~ /^🤖/) printf "  " MAGENTA "%-18s" RESET " %s\n", cmd, desc; \
			else if (desc ~ /^🐳/) printf "  " CYAN "%-18s" RESET " %s\n", cmd, desc; \
			else if (desc ~ /^📋/) printf "  " YELLOW "%-18s" RESET " %s\n", cmd, desc; \
			else if (desc ~ /^🏥/) printf "  " GREEN "%-18s" RESET " %s\n", cmd, desc; \
			else if (desc ~ /^🧹/) printf "  " RED "%-18s" RESET " %s\n", cmd, desc; \
			else printf "  %-18s %s\n", cmd, desc; \
		}'
	@$(ECHO) ""
	@$(ECHO) "$(BOLD)💡 DICA:$(RESET) Use $(GREEN)make <comando>$(RESET) para executar"
	@$(ECHO) "$(BOLD)📖 HELP:$(RESET) Use $(GREEN)make info$(RESET) para ver informação do projeto"
	@$(ECHO) ""

# ============================================================================
# 🔧 Setup & Instalação
# ============================================================================
quickstart: ## 🔧 Setup completo interativo (recomendado para primeira vez)
	@$(ECHO) ""
	@$(ECHO) "$(CYAN)╔══════════════════════════════════════════════════════════════════╗$(RESET)"
	@$(ECHO) "$(CYAN)║$(RESET)  $(BOLD)🚀 Quick Start - Wazuh SCA AI Analyst$(RESET)                      $(CYAN)║$(RESET)"
	@$(ECHO) "$(CYAN)╚══════════════════════════════════════════════════════════════════╝$(RESET)"
	@$(ECHO) ""
	@$(ECHO) "$(BOLD)Passo 1/6:$(RESET) Criar ficheiro .env..."
	@make setup-env
	@$(ECHO) ""
	@$(ECHO) "$(BOLD)Passo 2/6:$(RESET) Verificar configuração AI..."
	@make check-ai-mode
	@$(ECHO) ""
	@$(ECHO) "$(BOLD)Passo 3/6:$(RESET) Configurar Cache Redis"
	@REDIS_CACHE=$$(grep "^ENABLE_REDIS_CACHE=" .env | cut -d '=' -f2 | tr -d ' \r\n'); \
	if [ -z "$$REDIS_CACHE" ]; then \
		read -p "$(YELLOW)Habilitar Redis cache para melhor performance? [Y/n]$(RESET) " -n 1 -r; \
		$(ECHO) ""; \
		if [[ ! $$REPLY =~ ^[Nn]$$ ]]; then \
			make cache-enable; \
		else \
			$(ECHO) "$(YELLOW)⚠️  Redis cache desabilitado. Use 'make cache-enable' para habilitar.$(RESET)"; \
		fi; \
	else \
		if [ "$$REDIS_CACHE" = "true" ]; then \
			$(ECHO) "$(GREEN)✓$(RESET) Redis cache: $(GREEN)habilitado$(RESET) (já configurado em .env)"; \
			$(ECHO) "$(YELLOW)⚠️  Execute 'make up-cache' para iniciar com Redis$(RESET)"; \
		else \
			$(ECHO) "$(YELLOW)⚠️$(RESET)  Redis cache: $(YELLOW)desabilitado$(RESET) (já configurado em .env)"; \
		fi; \
	fi
	@$(ECHO) ""
	@$(ECHO) "$(BOLD)Passo 4/6:$(RESET) Configurar Auto-download de Modelo"
	@AI_MODE=$$(grep "^AI_MODE=" .env | cut -d '=' -f2 | tr -d ' \r\n'); \
	if [ "$$AI_MODE" = "external" ]; then \
		$(ECHO) "$(BLUE)ℹ$(RESET)  Modo external: download de modelo não necessário"; \
		sed -i.bak 's/AUTO_DOWNLOAD_MODEL=.*/AUTO_DOWNLOAD_MODEL=false/' .env && rm -f .env.bak; \
	else \
		AUTO_DL=$$(grep "^AUTO_DOWNLOAD_MODEL=" .env | cut -d '=' -f2 | tr -d ' \r\n'); \
		if [ -z "$$AUTO_DL" ]; then \
			read -p "$(YELLOW)Fazer download automático do modelo AI? [Y/n]$(RESET) " -n 1 -r; \
			$(ECHO) ""; \
			if [[ ! $$REPLY =~ ^[Nn]$$ ]]; then \
				sed -i.bak 's/AUTO_DOWNLOAD_MODEL=.*/AUTO_DOWNLOAD_MODEL=true/' .env && rm -f .env.bak; \
				$(ECHO) "$(GREEN)✅ Auto-download habilitado$(RESET)"; \
			else \
				sed -i.bak 's/AUTO_DOWNLOAD_MODEL=.*/AUTO_DOWNLOAD_MODEL=false/' .env && rm -f .env.bak; \
				$(ECHO) "$(YELLOW)⚠️  Auto-download desabilitado$(RESET)"; \
			fi; \
		else \
			if [ "$$AUTO_DL" = "true" ]; then \
				$(ECHO) "$(GREEN)✓$(RESET) Auto-download: $(GREEN)habilitado$(RESET) (já configurado em .env)"; \
			else \
				$(ECHO) "$(YELLOW)⚠️$(RESET)  Auto-download: $(YELLOW)desabilitado$(RESET) (já configurado em .env)"; \
			fi; \
		fi; \
	fi
	@$(ECHO) ""
	@$(ECHO) "$(BOLD)Passo 5/6:$(RESET) Verificar configuração de modelo AI"
	@AI_MODE=$$(grep "^AI_MODE=" .env | cut -d '=' -f2 | tr -d ' \r\n'); \
	AUTO_DL=$$(grep "^AUTO_DOWNLOAD_MODEL=" .env | cut -d '=' -f2 | tr -d ' \r\n'); \
	if [ "$$AI_MODE" = "local" ] || [ "$$AI_MODE" = "mixed" ]; then \
		if [ "$$AUTO_DL" = "true" ]; then \
			$(ECHO) "$(GREEN)✓$(RESET) Auto-download habilitado - Modelo será baixado automaticamente no primeiro start"; \
		else \
			$(ECHO) "$(YELLOW)⚠️$(RESET) Auto-download desabilitado - Modelo deve ser baixado manualmente"; \
			$(ECHO) "   Use: $(GREEN)make download-model$(RESET)"; \
		fi; \
	else \
		$(ECHO) "$(BLUE)ℹ$(RESET)  Modo external: download de modelo não necessário"; \
	fi
	@$(ECHO) ""
	@$(ECHO) "$(BOLD)Passo 6/6:$(RESET) Build das imagens Docker"
	@read -p "$(YELLOW)Fazer build das imagens agora? [Y/n]$(RESET) " -n 1 -r; \
	$(ECHO) ""; \
	if [[ ! $$REPLY =~ ^[Nn]$$ ]]; then \
		make build; \
	else \
		$(ECHO) "$(YELLOW)⚠️  Build não executado. Use 'make build' para construir as imagens.$(RESET)"; \
	fi
	@$(ECHO) ""
	@$(ECHO) "$(GREEN)╔══════════════════════════════════════════════════════════════════╗$(RESET)"
	@$(ECHO) "$(GREEN)║$(RESET)  $(BOLD)✅ Setup Completo!$(RESET)                                           $(GREEN)║$(RESET)"
	@$(ECHO) "$(GREEN)╚══════════════════════════════════════════════════════════════════╝$(RESET)"
	@$(ECHO) ""
	@$(ECHO) "$(BOLD)Próximos passos:$(RESET)"
	@$(ECHO) "  $(CYAN)1.$(RESET) Editar $(YELLOW).env$(RESET) com suas credenciais Wazuh"
	@$(ECHO) "  $(CYAN)2.$(RESET) Iniciar serviços: $(GREEN)make up$(RESET) $(YELLOW)(ou$(RESET) $(GREEN)make up-cache$(RESET) $(YELLOW)com Redis)$(RESET)"
	@$(ECHO) "  $(CYAN)3.$(RESET) Aceder à aplicação: $(BLUE)http://localhost:3000$(RESET)"
	@$(ECHO) ""
	@$(ECHO) "$(BOLD)💡 Comandos úteis:$(RESET)"
	@$(ECHO) "  $(GREEN)make info$(RESET)          → Ver informação do sistema"
	@$(ECHO) "  $(GREEN)make health$(RESET)        → Verificar saúde dos serviços"
	@$(ECHO) "  $(GREEN)make rebuild$(RESET)       → Reconstruir imagens Docker"
	@$(ECHO) ""

setup-env: ## 🔧 Criar ficheiro .env a partir do exemplo
	@if [ -f .env ]; then \
		$(ECHO) "$(YELLOW)⚠️  .env já existe. Mantendo ficheiro atual.$(RESET)"; \
	else \
		cp .env.example .env; \
		$(ECHO) "$(GREEN)✅ Ficheiro .env criado!$(RESET)"; \
		$(ECHO) "$(YELLOW)⚠️  Edite .env com suas credenciais antes de continuar.$(RESET)"; \
	fi

check-ai-mode: ## 🔧 Verificar configuração AI_MODE atual
	@if [ -f .env ]; then \
		AI_MODE=$$(grep "^AI_MODE=" .env | cut -d '=' -f2 | tr -d ' \r\n'); \
		$(ECHO) ""; \
		$(ECHO) "$(CYAN)╔══════════════════════════════════════════════════════════════════╗$(RESET)"; \
		$(ECHO) "$(CYAN)║$(RESET)  $(BOLD)📊 Configuração AI Atual$(RESET)                                    $(CYAN)║$(RESET)"; \
		$(ECHO) "$(CYAN)╚══════════════════════════════════════════════════════════════════╝$(RESET)"; \
		$(ECHO) ""; \
		$(ECHO) "  $(BOLD)AI_MODE:$(RESET) $(MAGENTA)$$AI_MODE$(RESET)"; \
		$(ECHO) "  $(BOLD)Debug:$(RESET) [$$AI_MODE]"; \
		$(ECHO) ""; \
		if [ "$$AI_MODE" = "local" ] || [ "$$AI_MODE" = "mixed" ]; then \
			$(ECHO) "  $(YELLOW)⚠️  vLLM será iniciado$(RESET) (requer GPU + modelo)"; \
			if [ ! -d "models" ] || [ -z "$$(ls -A models 2>/dev/null)" ]; then \
				$(ECHO) "  $(RED)❌ Modelo não encontrado!$(RESET) Run: $(GREEN)make download-model$(RESET)"; \
			else \
				$(ECHO) "  $(GREEN)✅ Modelo encontrado$(RESET)"; \
			fi; \
		elif [ "$$AI_MODE" = "external" ]; then \
			$(ECHO) "  $(BLUE)ℹ️  vLLM NÃO será iniciado$(RESET) (modo externo)"; \
		else \
			$(ECHO) "  $(RED)⚠️  AI_MODE inválido: '$$AI_MODE'$(RESET)"; \
			$(ECHO) "  $(YELLOW)Valores válidos: local, external, mixed$(RESET)"; \
		fi; \
		if [ "$$AI_MODE" = "external" ] || [ "$$AI_MODE" = "mixed" ]; then \
			OPENAI_KEY=$$(grep "^OPENAI_API_KEY=" .env | cut -d '=' -f2 | tr -d ' \r\n'); \
			if [ -z "$$OPENAI_KEY" ] || [ "$$OPENAI_KEY" = "your_openai_api_key_here" ]; then \
				$(ECHO) "  $(RED)❌ OpenAI API key não configurada!$(RESET)"; \
			else \
				$(ECHO) "  $(GREEN)✅ OpenAI API key configurada$(RESET)"; \
			fi; \
		fi; \
		$(ECHO) ""; \
	else \
		$(ECHO) "$(RED)❌ Ficheiro .env não encontrado!$(RESET)"; \
		$(ECHO) "   Run: $(GREEN)make setup-env$(RESET)"; \
	fi

install: ## 🔧 Instalar dependências localmente (desenvolvimento)
	@$(ECHO) "$(CYAN)📦 A instalar dependências...$(RESET)"
	@$(ECHO) ""
	@$(ECHO) "$(BOLD)Backend:$(RESET)"
	@cd backend && pip install -r requirements.txt
	@$(ECHO) ""
	@$(ECHO) "$(BOLD)Frontend:$(RESET)"
	@cd frontend && npm install
	@$(ECHO) ""
	@$(ECHO) "$(GREEN)✅ Todas as dependências instaladas!$(RESET)"

# ============================================================================
# 🤖 Gestão de Modelos AI
# ============================================================================
download-model: ## 🤖 Download modelo Llama 3 8B (~4.9GB)
	@$(ECHO) "$(CYAN)╔══════════════════════════════════════════════════════════════════╗$(RESET)"
	@$(ECHO) "$(CYAN)║$(RESET)  $(BOLD)📥 Download Modelo AI$(RESET)                                       $(CYAN)║$(RESET)"
	@$(ECHO) "$(CYAN)╚══════════════════════════════════════════════════════════════════╝$(RESET)"
	@$(ECHO) ""
	@$(ECHO) "$(BOLD)Modelo:$(RESET) Llama 3 8B Instruct (Quantizado Q4)"
	@$(ECHO) "$(BOLD)Tamanho:$(RESET) ~4.9GB"
	@$(ECHO) ""
	@mkdir -p models
	@if [ -f "models/Meta-Llama-3-8B-Instruct.Q4_K_M.gguf" ]; then \
		$(ECHO) "$(GREEN)✅ Modelo já existe!$(RESET)"; \
		$(ECHO) "   Localização: $(CYAN)models/Meta-Llama-3-8B-Instruct.Q4_K_M.gguf$(RESET)"; \
		$(ECHO) "   Para re-download, delete o ficheiro primeiro: $(RED)make remove-model$(RESET)"; \
	else \
		$(ECHO) "$(YELLOW)⏳ A fazer download... (pode demorar vários minutos)$(RESET)"; \
		$(ECHO) ""; \
		if command -v wget > /dev/null; then \
			wget --show-progress -O models/Meta-Llama-3-8B-Instruct.Q4_K_M.gguf \
				"https://huggingface.co/QuantFactory/Meta-Llama-3-8B-Instruct-GGUF/resolve/main/Meta-Llama-3-8B-Instruct.Q4_K_M.gguf"; \
		elif command -v curl > /dev/null; then \
			curl -L --progress-bar -o models/Meta-Llama-3-8B-Instruct.Q4_K_M.gguf \
				"https://huggingface.co/QuantFactory/Meta-Llama-3-8B-Instruct-GGUF/resolve/main/Meta-Llama-3-8B-Instruct.Q4_K_M.gguf"; \
		else \
			$(ECHO) "$(RED)❌ Erro: wget ou curl não encontrado!$(RESET)"; \
			$(ECHO) "   Instale wget ou curl primeiro."; \
			exit 1; \
		fi; \
		if [ -f "models/Meta-Llama-3-8B-Instruct.Q4_K_M.gguf" ]; then \
			$(ECHO) ""; \
			$(ECHO) "$(GREEN)✅ Download completo!$(RESET)"; \
			$(ECHO) "   Tamanho: $(CYAN)$$(du -h models/Meta-Llama-3-8B-Instruct.Q4_K_M.gguf | cut -f1)$(RESET)"; \
		else \
			$(ECHO) "$(RED)❌ Download falhou!$(RESET)"; \
			exit 1; \
		fi; \
	fi
	@$(ECHO) ""

check-model: ## 🤖 Verificar se modelo AI está presente
	@if [ -d "models" ] && [ -f "models/Meta-Llama-3-8B-Instruct.Q4_K_M.gguf" ]; then \
		$(ECHO) "$(GREEN)✅ Modelo encontrado!$(RESET)"; \
		$(ECHO) "   Ficheiro: $(CYAN)models/Meta-Llama-3-8B-Instruct.Q4_K_M.gguf$(RESET)"; \
		$(ECHO) "   Tamanho:  $(CYAN)$$(du -h models/Meta-Llama-3-8B-Instruct.Q4_K_M.gguf | cut -f1)$(RESET)"; \
	else \
		$(ECHO) "$(RED)❌ Modelo não encontrado!$(RESET)"; \
		$(ECHO) "   Execute: $(GREEN)make download-model$(RESET)"; \
		exit 1; \
	fi

remove-model: ## 🤖 Remover modelo AI (~4.9GB libertados)
	@$(ECHO) "$(YELLOW)🗑️  A remover modelo AI...$(RESET)"
	@if [ -f "models/Meta-Llama-3-8B-Instruct.Q4_K_M.gguf" ]; then \
		rm -f models/Meta-Llama-3-8B-Instruct.Q4_K_M.gguf; \
		$(ECHO) "$(GREEN)✅ Modelo removido (~4.9GB libertados)$(RESET)"; \
	else \
		$(ECHO) "$(YELLOW)⚠️  Nenhum modelo encontrado$(RESET)"; \
	fi

# ============================================================================
# 🐳 Operações Docker
# ============================================================================
build: ## 🐳 Construir imagens Docker
	@$(ECHO) "$(CYAN)🔨 A construir imagens Docker...$(RESET)"
	@docker-compose build
	@$(ECHO) "$(GREEN)✅ Build completo!$(RESET)"

rebuild: ## 🐳 Reconstruir imagens Docker (sem cache)
	@$(ECHO) "$(CYAN)🔨 A reconstruir imagens Docker (sem cache)...$(RESET)"
	@$(ECHO) "$(YELLOW)⚠️  Isto pode demorar vários minutos$(RESET)"
	@docker-compose build --no-cache
	@$(ECHO) "$(GREEN)✅ Rebuild completo!$(RESET)"
	@$(ECHO) ""
	@$(ECHO) "$(BOLD)Próximo passo:$(RESET) $(GREEN)make down$(RESET) && $(GREEN)make up$(RESET)"

up: ## 🐳 Iniciar todos os serviços
	@if [ ! -f .env ]; then \
		$(ECHO) "$(RED)❌ Ficheiro .env não encontrado!$(RESET)"; \
		$(ECHO) "   Execute: $(GREEN)make setup-env$(RESET)"; \
		exit 1; \
	fi
	@AI_MODE=$$(grep "^AI_MODE=" .env | cut -d '=' -f2 | tr -d ' \r\n'); \
	$(ECHO) ""; \
	$(ECHO) "$(CYAN)╔══════════════════════════════════════════════════════════════════╗$(RESET)"; \
	$(ECHO) "$(CYAN)║$(RESET)  $(BOLD)🚀 A Iniciar Wazuh SCA AI Analyst$(RESET)                          $(CYAN)║$(RESET)"; \
	$(ECHO) "$(CYAN)╚══════════════════════════════════════════════════════════════════╝$(RESET)"; \
	$(ECHO) ""; \
	$(ECHO) "  $(BOLD)Modo AI:$(RESET) $(MAGENTA)$$AI_MODE$(RESET)"; \
	if [ "$$AI_MODE" = "local" ] || [ "$$AI_MODE" = "mixed" ]; then \
		if [ ! -d "models" ] || [ -z "$$(ls -A models 2>/dev/null)" ]; then \
			$(ECHO) ""; \
			$(ECHO) "  $(RED)⚠️  AVISO: Modelo AI não encontrado!$(RESET)"; \
			$(ECHO) "  $(YELLOW)vLLM não iniciará sem modelo.$(RESET)"; \
			$(ECHO) "  $(GREEN)Solução: make download-model$(RESET)"; \
			$(ECHO) ""; \
			read -p "  Continuar mesmo assim? [y/N] " -n 1 -r; \
			$(ECHO) ""; \
			if [[ ! $$REPLY =~ ^[Yy]$$ ]]; then \
				exit 1; \
			fi; \
		fi; \
		$(ECHO) "  $(GREEN)✓$(RESET) vLLM será iniciado (requer GPU)"; \
		$(ECHO) "  $(YELLOW)⏳ Verificando imagem vLLM... (primeira vez pode demorar)$(RESET)"; \
		COMPOSE_PROFILES=$$AI_MODE docker-compose up -d; \
	elif [ "$$AI_MODE" = "external" ]; then \
		$(ECHO) "  $(BLUE)ℹ$(RESET)  vLLM NÃO será iniciado (modo externo)"; \
		docker-compose up -d; \
	else \
		$(ECHO) "  $(RED)❌ AI_MODE inválido: '$$AI_MODE'$(RESET)"; \
		$(ECHO) "  $(YELLOW)Valores válidos: local, external, mixed$(RESET)"; \
		exit 1; \
	fi
	@$(ECHO) ""
	@$(ECHO) "$(GREEN)╔══════════════════════════════════════════════════════════════════╗$(RESET)"
	@$(ECHO) "$(GREEN)║$(RESET)  $(BOLD)✅ Serviços Iniciados!$(RESET)                                       $(GREEN)║$(RESET)"
	@$(ECHO) "$(GREEN)╚══════════════════════════════════════════════════════════════════╝$(RESET)"
	@$(ECHO) ""
	@$(ECHO) "  $(BOLD)🌐 URLs de Acesso:$(RESET)"
	@$(ECHO) "     Frontend:  $(BLUE)http://localhost:3000$(RESET)"
	@$(ECHO) "     Backend:   $(BLUE)http://localhost:8000$(RESET)"
	@$(ECHO) "     API Docs:  $(BLUE)http://localhost:8000/docs$(RESET)"
	@$(ECHO) ""
	@$(ECHO) "  $(BOLD)📊 Comandos Úteis:$(RESET)"
	@$(ECHO) "     Ver estado:  $(GREEN)make ps$(RESET)"
	@$(ECHO) "     Ver logs:    $(GREEN)make logs$(RESET)"
	@$(ECHO) "     Health check:$(GREEN)make health$(RESET)"
	@$(ECHO) ""

up-cache: ## 🐳 Iniciar serviços COM Redis cache
	@if [ ! -f .env ]; then \
		$(ECHO) "$(RED)❌ Ficheiro .env não encontrado!$(RESET)"; \
		$(ECHO) "   Execute: $(GREEN)make setup-env$(RESET)"; \
		exit 1; \
	fi
	@$(ECHO) ""
	@$(ECHO) "$(CYAN)╔══════════════════════════════════════════════════════════════════╗$(RESET)"
	@$(ECHO) "$(CYAN)║$(RESET)  $(BOLD)🚀 A Iniciar com Redis Cache$(RESET)                                $(CYAN)║$(RESET)"
	@$(ECHO) "$(CYAN)╚══════════════════════════════════════════════════════════════════╝$(RESET)"
	@$(ECHO) ""
	@AI_MODE=$$(grep "^AI_MODE=" .env | cut -d '=' -f2 | tr -d ' \r\n'); \
	$(ECHO) "  $(BOLD)Modo AI:$(RESET) $(MAGENTA)$$AI_MODE$(RESET)"; \
	$(ECHO) "  $(BOLD)Redis:$(RESET) $(GREEN)Habilitado$(RESET)"; \
	if [ "$$AI_MODE" = "local" ] || [ "$$AI_MODE" = "mixed" ]; then \
		COMPOSE_PROFILES=$$AI_MODE,cache docker-compose up -d; \
	else \
		COMPOSE_PROFILES=cache docker-compose up -d; \
	fi
	@$(ECHO) ""
	@$(ECHO) "$(GREEN)✅ Serviços iniciados com Redis cache!$(RESET)"
	@$(ECHO) "   Verifique: $(GREEN)make health$(RESET)"

down: ## 🐳 Parar todos os serviços
	@$(ECHO) "$(YELLOW)🛑 A parar serviços...$(RESET)"
	@docker-compose --profile "*" down
	@$(ECHO) "$(GREEN)✅ Serviços parados!$(RESET)"

restart: ## 🐳 Reiniciar todos os serviços
	@$(ECHO) "$(CYAN)🔄 A reiniciar serviços...$(RESET)"
	@docker-compose restart
	@$(ECHO) "$(GREEN)✅ Serviços reiniciados!$(RESET)"

restart-backend: ## 🐳 Reiniciar apenas backend
	@$(ECHO) "$(CYAN)🔄 A reiniciar backend...$(RESET)"
	@docker-compose restart backend
	@$(ECHO) "$(GREEN)✅ Backend reiniciado!$(RESET)"

restart-frontend: ## 🐳 Reiniciar apenas frontend
	@$(ECHO) "$(CYAN)🔄 A reiniciar frontend...$(RESET)"
	@docker-compose restart frontend
	@$(ECHO) "$(GREEN)✅ Frontend reiniciado!$(RESET)"

restart-vllm: ## 🐳 Reiniciar apenas vLLM
	@$(ECHO) "$(CYAN)🔄 A reiniciar vLLM...$(RESET)"
	@docker-compose restart vllm
	@$(ECHO) "$(GREEN)✅ vLLM reiniciado!$(RESET)"

restart-redis: ## 🐳 Reiniciar apenas Redis
	@$(ECHO) "$(CYAN)🔄 A reiniciar Redis...$(RESET)"
	@docker-compose restart redis
	@$(ECHO) "$(GREEN)✅ Redis reiniciado!$(RESET)"

ps: ## 🐳 Mostrar estado dos serviços
	@$(ECHO) "$(CYAN)📊 Estado dos Serviços:$(RESET)"
	@$(ECHO) ""
	@docker-compose ps

status: ps ## 🐳 Alias para 'ps'

# ============================================================================
# 📋 Logs & Monitorização
# ============================================================================
logs: ## 📋 Ver logs de todos os serviços
	@$(ECHO) "$(CYAN)📋 A mostrar logs (Ctrl+C para sair)...$(RESET)"
	@docker-compose logs -f

logs-backend: ## 📋 Ver logs do backend
	@$(ECHO) "$(CYAN)📋 Backend logs (Ctrl+C para sair)...$(RESET)"
	@docker-compose logs -f backend

logs-frontend: ## 📋 Ver logs do frontend
	@$(ECHO) "$(CYAN)📋 Frontend logs (Ctrl+C para sair)...$(RESET)"
	@docker-compose logs -f frontend

logs-vllm: ## 📋 Ver logs do vLLM
	@$(ECHO) "$(CYAN)📋 vLLM logs (Ctrl+C para sair)...$(RESET)"
	@docker-compose logs -f vllm

logs-redis: ## 📋 Ver logs do Redis
	@$(ECHO) "$(CYAN)📋 Redis logs (Ctrl+C para sair)...$(RESET)"
	@docker-compose logs -f redis

# ============================================================================
# 🏥 Health Checks & Diagnósticos
# ============================================================================
health: ## 🏥 Verificar saúde dos serviços
	@$(ECHO) ""
	@$(ECHO) "$(CYAN)╔══════════════════════════════════════════════════════════════════╗$(RESET)"
	@$(ECHO) "$(CYAN)║$(RESET)  $(BOLD)🏥 Health Check$(RESET)                                              $(CYAN)║$(RESET)"
	@$(ECHO) "$(CYAN)╚══════════════════════════════════════════════════════════════════╝$(RESET)"
	@$(ECHO) ""
	@$(ECHO) "$(BOLD)Backend API:$(RESET)"
	@curl -s http://localhost:8000/health | jq . 2>/dev/null || $(ECHO) "  $(RED)❌ Não responde$(RESET)"
	@$(ECHO) ""
	@$(ECHO) "$(BOLD)Frontend:$(RESET)"
	@STATUS=$$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 2>/dev/null); \
	if [ "$$STATUS" = "200" ]; then \
		$(ECHO) "  $(GREEN)✅ Status: $$STATUS$(RESET)"; \
	else \
		$(ECHO) "  $(RED)❌ Não responde$(RESET)"; \
	fi
	@$(ECHO) ""
	@$(ECHO) "$(BOLD)vLLM (se ativo):$(RESET)"
	@curl -s http://localhost:8001/health 2>/dev/null | jq . 2>/dev/null || $(ECHO) "  $(YELLOW)⚠️  Não ativo ou não responde$(RESET)"
	@$(ECHO) ""
	@$(ECHO) "$(BOLD)Redis (se ativo):$(RESET)"
	@REDIS_STATUS=$$(docker-compose exec redis redis-cli PING 2>/dev/null); \
	if [ "$$REDIS_STATUS" = "PONG" ]; then \
		$(ECHO) "  $(GREEN)✅ Online$(RESET)"; \
		CACHE_KEYS=$$(docker-compose exec redis redis-cli DBSIZE 2>/dev/null | grep -o '[0-9]*'); \
		$(ECHO) "  $(CYAN)Chaves em cache: $$CACHE_KEYS$(RESET)"; \
	else \
		$(ECHO) "  $(YELLOW)⚠️  Não ativo ou não responde$(RESET)"; \
	fi
	@$(ECHO) ""

test-wazuh: ## 🏥 Testar conexão com Wazuh API
	@$(ECHO) "$(CYAN)🔗 A testar conexão Wazuh...$(RESET)"
	@curl -s http://localhost:8000/api/wazuh/test || $(ECHO) "$(RED)❌ Conexão falhou$(RESET)"

info: ## 🏥 Mostrar informação do projeto
	@$(ECHO) ""
	@$(ECHO) "$(CYAN)╔══════════════════════════════════════════════════════════════════╗$(RESET)"
	@$(ECHO) "$(CYAN)║$(RESET)  $(BOLD)📊 Wazuh SCA AI Analyst - Informação do Projeto$(RESET)            $(CYAN)║$(RESET)"
	@$(ECHO) "$(CYAN)╚══════════════════════════════════════════════════════════════════╝$(RESET)"
	@$(ECHO) ""
	@$(ECHO) "$(BOLD)📦 Stack Tecnológica:$(RESET)"
	@$(ECHO) "   Backend:  $(CYAN)FastAPI$(RESET) (Python 3.11+)"
	@$(ECHO) "   Frontend: $(CYAN)React + TypeScript + Vite$(RESET)"
	@$(ECHO) "   AI:       $(CYAN)vLLM (Llama 3) + OpenAI$(RESET)"
	@$(ECHO) "   Cache:    $(CYAN)Redis 7$(RESET) (opcional)"
	@$(ECHO) ""
	@if [ -f .env ]; then \
		AI_MODE=$$(grep "^AI_MODE=" .env | cut -d '=' -f2 | tr -d ' \r\n'); \
		REDIS_CACHE=$$(grep "^ENABLE_REDIS_CACHE=" .env | cut -d '=' -f2 | tr -d ' \r\n'); \
		AUTO_DL=$$(grep "^AUTO_DOWNLOAD_MODEL=" .env | cut -d '=' -f2 | tr -d ' \r\n'); \
		$(ECHO) "$(BOLD)⚙️  Configuração:$(RESET)"; \
		$(ECHO) "   AI_MODE:           $(MAGENTA)$$AI_MODE$(RESET)"; \
		$(ECHO) "   Redis Cache:       $$(if [ \"$$REDIS_CACHE\" = \"true\" ]; then echo \"$(GREEN)✅ Habilitado$(RESET)\"; else echo \"$(YELLOW)⚠️  Desabilitado$(RESET)\"; fi)"; \
		$(ECHO) "   Auto-download:     $$(if [ \"$$AUTO_DL\" = \"true\" ]; then echo \"$(GREEN)✅ Sim$(RESET)\"; else echo \"$(YELLOW)❌ Não$(RESET)\"; fi)"; \
		if [ -d "models" ] && [ -n "$$(ls -A models 2>/dev/null)" ]; then \
			$(ECHO) "   Modelo AI:         $(GREEN)✅ Transferido$(RESET)"; \
		else \
			$(ECHO) "   Modelo AI:         $(RED)❌ Não encontrado$(RESET)"; \
		fi; \
	else \
		$(ECHO) "$(YELLOW)⚠️  Ficheiro .env não encontrado$(RESET)"; \
	fi
	@$(ECHO) ""
	@$(ECHO) "$(BOLD)🌐 URLs de Acesso:$(RESET)"
	@$(ECHO) "   Frontend:  $(BLUE)http://localhost:3000$(RESET)"
	@$(ECHO) "   Backend:   $(BLUE)http://localhost:8000$(RESET)"
	@$(ECHO) "   API Docs:  $(BLUE)http://localhost:8000/docs$(RESET)"
	@$(ECHO) "   vLLM API:  $(BLUE)http://localhost:8001/v1$(RESET)"
	@$(ECHO) ""
	@$(ECHO) "$(BOLD)📚 Documentação:$(RESET)"
	@$(ECHO) "   README:    $(CYAN)README.md$(RESET)"
	@$(ECHO) "   Help:      $(GREEN)make help$(RESET)"
	@$(ECHO) ""

# ============================================================================
# 🧹 Limpeza & Manutenção
# ============================================================================
clean: ## 🧹 Limpar containers, volumes e cache
	@$(ECHO) "$(YELLOW)🧹 A limpar...$(RESET)"
	@$(ECHO) ""
	@$(ECHO) "  $(CYAN)→$(RESET) A parar containers..."
	@docker-compose --profile "*" down -v 2>/dev/null || true
	@$(ECHO) "  $(CYAN)→$(RESET) A limpar volumes Docker..."
	@docker volume rm wazuh-csa-bot_redis-data 2>/dev/null || true
	@docker volume rm wazuh-csa-bot_models 2>/dev/null || true
	@$(ECHO) "  $(CYAN)→$(RESET) A limpar cache Python..."
	@rm -rf backend/__pycache__ backend/**/__pycache__ 2>/dev/null || true
	@$(ECHO) "  $(CYAN)→$(RESET) A limpar build frontend..."
	@rm -rf frontend/dist 2>/dev/null || true
	@$(ECHO) "  $(CYAN)→$(RESET) A limpar relatórios PDF..."
	@rm -rf backend/reports/*.pdf 2>/dev/null || true
	@$(ECHO) ""
	@$(ECHO) "$(GREEN)✅ Limpeza completa!$(RESET)"
	@$(ECHO) "   $(YELLOW)Nota: node_modules preservado (use 'make clean-all' para remover)$(RESET)"

clean-all: clean remove-model ## 🧹 Limpeza total (inclui modelo AI e dependências)
	@$(ECHO) ""
	@$(ECHO) "  $(CYAN)→$(RESET) A remover node_modules..."
	@rm -rf frontend/node_modules 2>/dev/null || true
	@$(ECHO) ""
	@$(ECHO) "$(GREEN)✅ Limpeza total completa!$(RESET)"
	@$(ECHO) ""
	@$(ECHO) "$(BOLD)Espaço libertado:$(RESET)"
	@$(ECHO) "  ✓ Containers Docker parados"
	@$(ECHO) "  ✓ Volumes Docker removidos (Redis + Models)"
	@$(ECHO) "  ✓ Cache Python removido"
	@$(ECHO) "  ✓ Build frontend removido"
	@$(ECHO) "  ✓ Relatórios PDF removidos"
	@$(ECHO) "  ✓ Modelo AI removido (~4.9GB)"
	@$(ECHO) "  ✓ node_modules removido"
	@$(ECHO) ""
	@$(ECHO) "$(YELLOW)Para recomeçar:$(RESET) $(GREEN)make quickstart$(RESET)"

# ============================================================================
# 💻 Desenvolvimento
# ============================================================================
dev-backend: ## 💻 Executar backend em modo dev (local)
	@$(ECHO) "$(CYAN)🚀 A iniciar backend em dev mode...$(RESET)"
	@cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend: ## 💻 Executar frontend em dev mode (local)
	@$(ECHO) "$(CYAN)🚀 A iniciar frontend em dev mode...$(RESET)"
	@cd frontend && npm run dev

shell-backend: ## 💻 Abrir shell no container backend
	@docker-compose exec backend /bin/sh

shell-frontend: ## 💻 Abrir shell no container frontend
	@docker-compose exec frontend /bin/sh

shell-vllm: ## 💻 Abrir shell no container vLLM
	@docker-compose exec vllm /bin/bash

shell-redis: ## 💻 Abrir shell no container Redis
	@docker-compose exec redis redis-cli

# ============================================================================
# 📦 Gestão de Cache Redis
# ============================================================================
cache-enable: ## 📦 Habilitar Redis cache no .env
	@if [ -f .env ]; then \
		sed -i.bak 's/ENABLE_REDIS_CACHE=.*/ENABLE_REDIS_CACHE=true/' .env && rm -f .env.bak; \
		$(ECHO) "$(GREEN)✅ Redis cache habilitado no .env$(RESET)"; \
		$(ECHO) "$(YELLOW)⚠️  Execute 'make up-cache' para iniciar com Redis$(RESET)"; \
	else \
		$(ECHO) "$(RED)❌ Ficheiro .env não encontrado!$(RESET)"; \
		exit 1; \
	fi

cache-disable: ## 📦 Desabilitar Redis cache no .env
	@if [ -f .env ]; then \
		sed -i.bak 's/ENABLE_REDIS_CACHE=.*/ENABLE_REDIS_CACHE=false/' .env && rm -f .env.bak; \
		$(ECHO) "$(GREEN)✅ Redis cache desabilitado no .env$(RESET)"; \
	else \
		$(ECHO) "$(RED)❌ Ficheiro .env não encontrado!$(RESET)"; \
		exit 1; \
	fi

cache-clear: ## 📦 Limpar todo o cache Redis
	@$(ECHO) "$(YELLOW)🧹 A limpar cache Redis...$(RESET)"
	@docker-compose exec redis redis-cli FLUSHALL
	@$(ECHO) "$(GREEN)✅ Cache Redis limpo!$(RESET)"

cache-stats: ## 📦 Ver estatísticas do Redis
	@$(ECHO) "$(CYAN)📊 Estatísticas Redis:$(RESET)"
	@$(ECHO) ""
	@docker-compose exec redis redis-cli INFO stats | grep -E "keyspace_hits|keyspace_misses|instantaneous_ops_per_sec" || true
	@$(ECHO) ""
	@$(ECHO) "$(BOLD)Chaves em cache:$(RESET)"
	@docker-compose exec redis redis-cli DBSIZE

