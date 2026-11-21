import runpy
from pathlib import Path


arquivo_principal = Path(__file__).resolve().parent / "Sistema de cadastro de alunos.py"
runpy.run_path(str(arquivo_principal), run_name="__main__")
