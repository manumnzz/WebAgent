.DEFAULT_GOAL := ayuda

.PHONY: ayuda formulario generar web reparar capturas mejorar test

ayuda formulario generar web reparar capturas mejorar test: ; @.venv/bin/python scripts/dev.py $@