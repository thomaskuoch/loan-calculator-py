install:
	uv sync

streamlit:
	uv run streamlit run streamlit_app.py --server.port 8501