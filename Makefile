.DEFAULT_GOAL := ayuda

.PHONY: ayuda formulario generar web reparar test

ayuda formulario generar web reparar test: ; @.venv/bin/python scripts/dev.py $@
