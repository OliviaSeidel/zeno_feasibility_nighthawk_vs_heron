"""Run the notebooks and save browser-readable copies."""
from pathlib import Path
import sys

import nbformat
from nbclient import NotebookClient
from nbconvert import HTMLExporter
from jupyter_client import KernelManager

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = [
    'understanding_survival_curves.ipynb',
    'relational_zeno_analysis.ipynb',
    'ideal_circuit_verification.ipynb',
    'memory_parity_robustness.ipynb',
    'relational_zeno_realistic_predictions.ipynb',
]


def reading_copy(notebook, name, folder):
    """Write HTML with links that work from the output folder."""
    import copy
    import re
    view = copy.deepcopy(notebook)
    for cell in view.cells:
        if cell.cell_type == 'markdown':
            cell.source = re.sub(
                r'\]\((?!https?://|#)([^)]+)\)',
                lambda m: '](../../' + m.group(1) + ')', cell.source)
    html, _ = HTMLExporter(template_name='lab').from_notebook_node(view)
    folder.mkdir(parents=True, exist_ok=True)
    (folder / (Path(name).stem + '.html')).write_text(html, encoding='utf-8')


def run():
    for name in NOTEBOOKS:
        print('Running', name, flush=True)
        path = ROOT / name
        notebook = nbformat.read(path, as_version=4)
        # Use the same Python environment that launched this script.
        manager = KernelManager(kernel_name='python3')
        manager.kernel_spec.argv = [
            sys.executable, '-m', 'ipykernel_launcher', '-f', '{connection_file}']
        client = NotebookClient(notebook, timeout=600, km=manager,
                                resources={'metadata': {'path': str(ROOT)}})
        try:
            client.execute()
        finally:
            if manager.has_kernel:
                manager.shutdown_kernel(now=True)
        nbformat.validate(notebook)
        nbformat.write(notebook, path)
        reading_copy(notebook, name, ROOT / 'outputs/notebooks')
        print('Saved', name, flush=True)


if __name__ == '__main__':
    run()
