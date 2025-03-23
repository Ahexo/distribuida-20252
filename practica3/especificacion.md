# Computación Distribuida 2025-2 Práctica 3: Gráficas generales
**Profesor:** Mauricio Riva Palacio Orozco
**Ayudante:** Adrián Felipe Fernández Romero
**Laboratorio:** Daniel Michel Tavera
**Fecha de entrega:** miércoles 2 de abril de 2025

# Descripción de la Práctica
El equipo deberá realizar lo siguiente:
- Generar una gráfica aleatoria (sin pesos en las aristas), como se describe más adelante.
- Implementar un algoritmo distribuido que explore la gráfica y obtenga su diámetro.

## Para generar la gráfica
- Se deberá preguntar al usuario el número de nodos en la gráfica
- Inicialmente, la gráfica está conectada de forma lineal (cada nodo solamente con el anterior y el siguiente).
- Después, cualquier otro par de nodos se conecta con probabilidad 50%.
- Finalmente, imprimir en pantalla una descripción de la gráfica. Puede ser una lista o matriz de adyacencias, o cualquier otra forma que consideren conveniente.

**Nota:** el algoritmo que genera la gráfica no necesariamente debe ser distribuido.

## Para obtener el diámetro
- Al finalizar el algoritmo, deberá imprimirse un mensaje que indique el resultado obtenido.
- Los demás detalles de implementación del algoritmo, así como las entradas y otras salidas, quedan a discreción del equipo.

Recuerden agregar comentarios que expliquen el funcionamiento del código.

## Requisitos de entrega
Guardar el código fuente del programa en un archivo con el nombre “Practica3”, seguido
de los nombres de los integrantes del equipo; por ejemplo:
> Practica3_MauricioRivaPalacio_AdrianFernandez_DanielMichel.py

Realizar también un reporte en pdf con el mismo nombre, en el cual se indique lo siguiente:
- Los nombres de todos los integrantes del equipo.
- Una descripción de cómo se desarrolló la práctica y cómo funciona la solución implementada.
- La forma de operar el programa, incluyendo qué entrada(s) se espera(n) del usuario, así como qué salida(s) arroja.
- Cualquier otro comentario o aclaración que consideren pertinente.

Subir los archivos al Classroom antes de las 23:59 horas de la fecha de entrega cumpliendo los siguientes lineamientos:
- Solamente un miembro del equipo debe enviar los archivos.
- Los demás integrantes deben marcar la práctica como entregada y agregar un comentario en el que indiquen quiénes son los integrantes de su equipo y quién entregó el código.