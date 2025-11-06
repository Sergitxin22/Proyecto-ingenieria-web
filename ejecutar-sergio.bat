@echo off
cd ..\entornoWeb\Scripts
call activate
cd ..\..\Proyecto-ingenieria-web\ProyectoTienda
python manage.py runserver