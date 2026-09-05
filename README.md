# TP8-LAB-AP
Juego hecho en **Python 3.12.3** con **Pygame**, donde acompañamos a **COPERNIBOT**
a través de una grilla hasta llegar al **merendero**, evitando obstaculos (paredes) y sin 
repetir el camino ya recorrido.

## COMO EJECUTAR EL JUEGO
1. Tener python 3.12.3 instalado
2. Instalar Pygame:
```
pip instal pygame
```



## Controles
 -`MOVIMIENTO`:  ↑ ↓ ← → (Mueve a copernibot segun la direccion de la flecha).  
 -`R`:  Reinicia el nivel.  
 -`ESC`:  Salir del juego.  

 ---

 ## REQUERIMENTOS
 Los siguientes arhcivos deberan estar en la **misma carpeta** que `Codigo-inicioV2.py`
 - "**COPERNIBOT.png**" (imagen del avatar de copernibot)
 - "**ram_sneeze.mp3**" (sonido del movimiento)
 - "**subaru_victory.mp3**" (sonido de victoria)

---

## Aporte creativo
para darle un toque de mi personalidad utilice los sonidos de: **ram_sneeze.mp3**
y **subaru_victory.mp3** provenientes del anime RE:ZERO

![imagen de re zero](https://private-user-images.githubusercontent.com/271253993/646767205-1a77ff33-b14f-4794-b2ed-98dc7349a2e7.webp?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3ODg2MjE0MTIsIm5iZiI6MTc4ODYyMTExMiwicGF0aCI6Ii8yNzEyNTM5OTMvNjQ2NzY3MjA1LTFhNzdmZjMzLWIxNGYtNDc5NC1iMmVkLTk4ZGM3MzQ5YTJlNy53ZWJwP1gtQW16LUFsZ29yaXRobT1BV1M0LUhNQUMtU0hBMjU2JlgtQW16LUNyZWRlbnRpYWw9QUtJQVZDT0RZTFNBNTNQUUs0WkElMkYyMDI2MDkwNSUyRnVzLWVhc3QtMSUyRnMzJTJGYXdzNF9yZXF1ZXN0JlgtQW16LURhdGU9MjAyNjA5MDVUMTUxMTUyWiZYLUFtei1FeHBpcmVzPTMwMCZYLUFtei1TaWduYXR1cmU9NTZlYmQ3MDdiMmNiYjY3NmQ0NmU4MTc0ZDBkNGI4ZjU1NDExNmQxMmJkZmU2NDNjMjMxOTBjYWE0Zjc0ZmRmOSZYLUFtei1TaWduZWRIZWFkZXJzPWhvc3QmcmVzcG9uc2UtY29udGVudC10eXBlPWltYWdlJTJGd2VicCJ9.RMrJcXs6WIY5b2lVvGjTmVlA0cFPFCPuTw-qsKNBUVY)

## NOTA IMPORTANTE ACERCA DEL SONIDO DE VICTORIA
### Aqui tuve un par de problemas con el sonido de victoria, al ganar un par de veces dejaba de funcionar y esto me rompio la cabeza durante un buen rato y al no entender que pasaba decidi pedirle ayuda a claude, aqui la explicacion:  
Al principio, el sonido de victoria (`subaru_victory.mp3`) se cargaba con
`pygame.mixer.Sound`, igual que el sonido de pasos. Esto funcionaba las
primeras veces, pero después de ganar varias veces seguidas (reiniciando con
`R`), el sonido empezaba a fallar o directamente dejaba de escucharse.
 
**Causa:** es un bug conocido de pygame al reproducir archivos `.mp3` con
`pygame.mixer.Sound`. Ese método decodifica el audio completo en memoria como
un "chunk", y el decodificador de mp3 que usa pygame internamente (mpg123)
se degrada después de varias cargas/reproducciones seguidas dentro de la
misma ejecución.
 
**Solución:** el sonido de victoria ahora se reproduce con
`pygame.mixer.music` en vez de `pygame.mixer.Sound`. Es un módulo distinto
dentro de pygame, pensado para reproducir archivos de audio por streaming
(leyéndolos de a poco en vez de cargarlos enteros), y no sufre ese problema
de degradación. Por eso en el código vas a ver:
 
```python
pygame.mixer.music.load(ruta_sonido_victoria)
pygame.mixer.music.play()
```
 
en vez de crear un objeto `Sound` para la victoria.
 
> Nota: `pygame.mixer.music` solo puede reproducir **un archivo a la vez**,
> pero como el sonido de victoria se usa una sola vez por partida (no se
> superpone con otros sonidos), no hay ningún problema en usarlo acá.

---

## Formulario de transparencia
Utilice claude, le pedi ayuda para incluir un color rojo cuando se quiera mover a copernibot hacia una direccion la cual ya se halla cruzado antes, para la animacion de **NIVEL COMPLETADO** que uso `math.sin`, y el problema donde mas me ayudo (en los anteriores mayormente fue unicamente de guia claude) fue en un error con el sonido de victoria que dejaba de funcionar luego de un par de veces de llegar al merendero, Puedes revisar la [explicación error del sonido de victoria](#NOTA-IMPORTANTE-ACERCA-DEL-SONIDO-DE-VICTORIA) para más detalles.
aparte de ayudarme grandemente a interpretar la `sintaxis basica de redaccion y formato` en la cual habian cosas que no entendia bien del todo como por ejemplo a la hora de poner la imagen de re zero tuve algunas complicaciones o con el vinculo de antes para no tener que extenderme nuevamente en la explicacion.



