## How to configure environment

> You must have `pyenv` installed.

```bash
cd hideit
pyenv update
pyenv install 3.14
pyenv local 3.14
python3 -m venv venv
./venv/bin/activate
pip install -r requirements.txt
pip install -r requirements.dev.txt
```

## How to run
```bash
python3 -m hideit
```

## How to lint
```bash
ruff format .; ruff check --fix .
```
