# Proyecto Asistente Virtual


>[!NOTE]
> **INSTALAR DEPENDENCIAS PARA SU FUNCIONAMIENTO**

## ¿Cómo Ejecutarlo?

Dado que ocupamos dependencias, antes de ejecutar el archivo agente.py es necesario instalar las dependencias del proyecto.

Para esto es necesario crear un entorno virtual, esto con la finalidad de no generar incompatibilidad con las dependencias y versiones que ya tengamos instaladas.

## Paso 1: Crear entorno virtual
En el mismo directorio donde tenemos el archivo agente.py abrir una terminal y ejecutar el comando
~~~
python -m venv .venv
~~~

Es necesario activar el entorno virtual una vez creado, para esto se debe de ejecutar en la misma terminal
**WINDOWS**
~~~
.venv\Scripts\activate
~~~
**MAC/LINUX**
~~~
source .venv/bin/activate
~~~

## Paso2: Descargar dependencias

~~~bash
pip install -r requirements.txt
~~~