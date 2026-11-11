run:
	@uv run python3 -m src 


api:
	@echo "hosting the api on local-host..."
	uv run uvicorn src.api:app --host 127.0.0.1 --port 8000 --reload

install:
	@uv venv ~/goinfre/RAG/.venv 
	@ln -s ~/goinfre/RAG/.venv .venv
	@uv sync
