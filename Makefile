.PHONY: install install-full setup-env verify clean

# Standard installation
install:
	pip install .

# Installation with all extras
install-full:
	pip install ".[full]"

# Interactive .env setup
setup-env:
	@if [ ! -f .env ]; then \
		echo "Creating .env from template..."; \
		echo "OPENAI_API_KEY=" > .env; \
		echo "VECTOR_DB_TYPE=chroma" >> .env; \
		echo "CHROMA_PERSIST_DIR=./chroma_db" >> .env; \
		echo "REDIS_URL=redis://localhost:6379/0" >> .env; \
		echo ".env created. Please fill in your API keys."; \
	else \
		echo ".env already exists."; \
	fi

# Run all verification scripts
verify:
	@echo "Running all verification scripts..."
	python3 tests/verify_memory.py
	python3 tests/verify_rag.py
	python3 tests/verify_vlm.py
	python3 tests/verify_observability.py
	python3 tests/verify_framework_chatbot.py

# Clean build artifacts
clean:
	rm -rf build/ dist/ *.egg-info/
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
