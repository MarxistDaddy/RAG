run:
	@uv run python3 -m src 

install:
	@uv venv ~/goinfre/RAG/.venv 
	@ln -s ~/goinfre/RAG/.venv .venv
	@uv sync
