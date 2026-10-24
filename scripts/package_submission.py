"""Prepare a zipped clean Git clone, preserving authentic development history."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import zipfile

def main() -> None:
    """Clone the final committed branch, check required files and create a ZIP."""
    root=Path(__file__).resolve().parents[1]
    status=subprocess.check_output(['git','status','--porcelain'],cwd=root,text=True)
    if status.strip():
        raise RuntimeError('Commit all final tracked/untracked project files before packaging')
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
    origin=subprocess.check_output(['git','remote','get-url','origin'],cwd=root,text=True).strip()
    destination=root/'dist'
    destination.mkdir(exist_ok=True)
    required=['README.md','LICENSE','requirements.txt','src/heat_project/solvers.py',
              'reports/MMA3001_technical_report.pdf','reports/test_report.html','docs/html/index.html',
              'presentation/MMA3001_plate_cooling_presentation.pptx','results/summary.json']
    with tempfile.TemporaryDirectory(prefix='mma3001-clone-') as temp:
        clone=Path(temp)/'MMA3001_plate_cooling'
        subprocess.run(['git','clone','--no-hardlinks','--branch','main',str(root),str(clone)],check=True)
        subprocess.run(['git','remote','set-url','origin',origin],cwd=clone,check=True)
        for filename in required:
            if not (clone/filename).is_file():raise RuntimeError(f'Missing required clone file:{filename}')
        archive=destination/'MMA3001_repository_clone.zip'
        with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as zipped:
            for path in sorted(clone.rglob('*')):
                if path.is_file():zipped.write(path,Path(clone.name)/path.relative_to(clone))
        with zipfile.ZipFile(archive) as zipped:
            if zipped.testzip() is not None:raise RuntimeError('ZIP integrity failure')
            if not any('/.git/HEAD' in name for name in zipped.namelist()):
                raise RuntimeError('Archive must preserve actual clone history')
        digest=hashlib.sha256(archive.read_bytes()).hexdigest()
        manifest={'commit':commit,'remote':origin,'archive':archive.name,'sha256':digest,
                  'contains_git_history':True,'required_files_checked':required,
                  'bytes':archive.stat().st_size}
        (destination/'submission_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
        print(json.dumps(manifest,indent=2))

if __name__=='__main__':
    main()
