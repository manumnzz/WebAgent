.DEFAULT_GOAL := ayuda

.PHONY: ayuda formulario generar web test

ayuda formulario generar web test: ; @.venv/bin/python scripts/dev.py $@