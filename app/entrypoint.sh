#!/bin/sh

# Выполните dvc pull
dvc pull

# Запустите основное приложение
exec "$@"