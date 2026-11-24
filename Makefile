
.DEFAULT_GOAL := ayuda

.PHONY: ayuda formulario generar web reparar coste test

ayuda formulario generar web reparar coste test: ; @.venv/bin/python scripts/dev.py $@
