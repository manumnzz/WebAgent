
.DEFAULT_GOAL := ayuda

.PHONY: ayuda formulario generar web reparar refinar coste test

ayuda formulario generar web reparar refinar coste test: ; @.venv/bin/python scripts/dev.py $@
