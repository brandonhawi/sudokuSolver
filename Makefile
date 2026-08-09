DIFFICULTY  ?= easy
MODEL       ?= qwen3:8b
OLLAMA_HOST ?= http://gaming-pc:11434
NUM_CTX     ?= 4096
MAX_STEPS   ?= 300
THINK       ?=

GAME_URL  ?= http://127.0.0.1:5001
GAME_LOG  ?= .game.log
GAME_PID  ?= .game.pid

RUN := uv run --group agent
AGENT := $(RUN) python -m solver_agent.player

ifeq ($(THINK),1)
THINK_FLAG := --think
else ifeq ($(THINK),0)
THINK_FLAG := --no-think
else
THINK_FLAG :=
endif

AGENT_ARGS := --difficulty $(DIFFICULTY) --model $(MODEL) --host $(OLLAMA_HOST) \
              --num-ctx $(NUM_CTX) --max-steps $(MAX_STEPS) $(THINK_FLAG)

.DEFAULT_GOAL := help
.PHONY: help install game serve stop agent play models lint clean

help:
	@echo "Sudoku - a game a language model can be taught to play"
	@echo
	@echo "  make play              start the game if needed, then play one game"
	@echo "  make agent             play one game (game must already be running)"
	@echo "  make game              run the game server in the foreground"
	@echo "  make serve             run the game server in the background"
	@echo "  make stop              stop the background game server"
	@echo "  make models            list models on the Ollama host"
	@echo "  make install           install everything, agent group included"
	@echo "  make lint              pylint the Python"
	@echo "  make clean             remove caches and the background server log"
	@echo
	@echo "Variables (make play DIFFICULTY=hard THINK=1):"
	@echo "  DIFFICULTY   $(DIFFICULTY)        easy | medium | hard"
	@echo "  MODEL        $(MODEL)"
	@echo "  OLLAMA_HOST  $(OLLAMA_HOST)"
	@echo "  NUM_CTX      $(NUM_CTX)"
	@echo "  MAX_STEPS    $(MAX_STEPS)"
	@echo "  THINK        $(if $(THINK),$(THINK),unset)             1 forces thinking, 0 forces it off, unset uses the model default"
	@echo
	@echo "Watch the model play at $(GAME_URL)"

install:
	uv sync --all-groups

game:
	uv run flask run

serve:
	@if curl -sf -o /dev/null $(GAME_URL)/api/game; then \
		echo "game already running at $(GAME_URL)"; \
	else \
		uv run flask run > $(GAME_LOG) 2>&1 & echo $$! > $(GAME_PID); \
		printf "starting game server"; \
		for i in $$(seq 1 20); do \
			if curl -sf -o /dev/null $(GAME_URL)/api/game; then \
				echo " - up at $(GAME_URL)"; exit 0; \
			fi; \
			printf "."; sleep 0.5; \
		done; \
		echo; echo "game server did not come up, see $(GAME_LOG)"; exit 1; \
	fi

stop:
	@if [ -f $(GAME_PID) ]; then \
		kill $$(cat $(GAME_PID)) 2>/dev/null || true; \
		rm -f $(GAME_PID); \
		echo "stopped the game server"; \
	else \
		echo "no game server started by make is running"; \
	fi

agent:
	@curl -sf -o /dev/null $(GAME_URL)/api/game || \
		{ echo "no game at $(GAME_URL) - run 'make serve' first, or use 'make play'"; exit 1; }
	$(AGENT) $(AGENT_ARGS)

play: serve
	@echo "watch at $(GAME_URL)"
	@$(MAKE) --no-print-directory agent

models:
	@curl -sf $(OLLAMA_HOST)/api/tags \
		| python3 -c "import sys,json; [print(m['name']) for m in json.load(sys.stdin)['models']]" \
		|| echo "could not reach $(OLLAMA_HOST)"

lint:
	uv run pylint app.py mcp_server.py sudoku solver_agent --fail-under=9.5 \
		--disable=missing-module-docstring,missing-function-docstring,missing-class-docstring,invalid-name

clean:
	rm -rf __pycache__ */__pycache__ .pytest_cache $(GAME_LOG) $(GAME_PID)
