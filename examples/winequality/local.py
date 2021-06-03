"""
To setup your shell for local development run:

    source <(python local.py)

"""
import pathlib

bin = pathlib.Path(__file__).absolute().parent.parent.parent.joinpath('bin')
sdk_py = pathlib.Path(__file__).absolute().parent.parent.parent.joinpath('sdk', 'python')

with open(sdk_py.joinpath('setup.py'), 'r') as fp:
    setup_py_source = fp.read()

with open(sdk_py.joinpath('setup.py'), 'w') as fp:
    fp.write(setup_py_source.replace('${VERSION}', '0.0.1'))

print(f'source venv/bin/activate')
print(f'export PATH=$PATH:{bin}')
print(f'(cd {sdk_py} && python -m pip install -e .)')
