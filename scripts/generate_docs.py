"""Generate complete local pdoc HTML using this repository's actual source."""
import os
from pathlib import Path
import subprocess
import sys

def main() -> None:
    """Build all public modules and provide a stable index landing page."""
    root=Path(__file__).resolve().parents[1]
    env=dict(os.environ, PYTHONPATH=str(root/'src'))
    subprocess.run([sys.executable,'-m','pdoc','--docformat','numpy','--output-directory',
                    str(root/'docs/html'),'heat_project','heat_project.model',
                    'heat_project.solvers','heat_project.reference','heat_project.metrics'],
                   cwd=root,env=env,check=True)
    index=root/'docs/html/index.html'
    if not index.exists():
        index.write_text('<!doctype html><html><head><meta charset="utf-8"><title>Heat project API</title></head><body><h1>Plate cooling API</h1><p><a href="heat_project.html">Open package documentation</a></p></body></html>')
    print(index)

if __name__=='__main__':
    main()
