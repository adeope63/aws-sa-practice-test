"""Isolated E2E server: never touches the personal study database."""
import os, sys, tempfile
from pathlib import Path
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'backend'))
path=Path(tempfile.mkdtemp(prefix='architect-lab-e2e-'))/'test.db'
os.environ['DATABASE_URL']=f'sqlite:///{path}'
import uvicorn
uvicorn.run('app.main:app',host='127.0.0.1',port=8001)
