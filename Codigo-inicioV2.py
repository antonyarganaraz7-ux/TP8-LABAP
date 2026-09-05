# -*- coding: utf-8 -*-
import os
import pygame
import sys
import math

PANTALLA_ANCHO = 1180
PANTALLA_ALTO = 720
COLUMNAS = 12
FILAS = 8
TAMANO_CELDA = 64
GRILLA_OFFSET_X = 20
GRILLA_OFFSET_Y = 60
HUD_X = GRILLA_OFFSET_X + COLUMNAS * TAMANO_CELDA + 20
FPS = 60

# --- colores cosas viejas --- #

COLOR_FONDO       = (28, 32, 42)
COLOR_CELDA       = (64, 72, 92)
COLOR_CELDA_BORDE = (40, 46, 60)
COLOR_SENDERO     = (240, 215, 90)
COLOR_MERENDERO   = (230, 130, 70)
COLOR_TEXTO       = (235, 235, 235)
COLOR_TEXTO_TENUE = (160, 165, 180)
COLOR_OK          = (90, 220, 130)
COLOR_HUD_BG      = (38, 44, 58)

# --- colores cosas nuevas --- #
COLOR_OBSTACULO   = (110, 70, 40)    
COLOR_ITEM        = (255, 215, 0)     
COLOR_BLOQUEADO   = (220, 90, 90)     

COOLDOWN_MS = 140
TIEMPO_AVISO_MS = 250   


def en_grilla(fila, columna):
    return 0 <= fila < FILAS and 0 <= columna < COLUMNAS


def celda_a_pixel(fila, columna):
    pixel_x = GRILLA_OFFSET_X + columna * TAMANO_CELDA
    pixel_y = GRILLA_OFFSET_Y + fila * TAMANO_CELDA
    return pixel_x, pixel_y


def mover_copernibot(estado, delta_fila, delta_columna, sonido_paso):
    fila_actual, columna_actual = estado["cursor"]
    nueva_fila = fila_actual + delta_fila
    nueva_columna = columna_actual + delta_columna
    nueva_celda = (nueva_fila, nueva_columna)

    # 1) No se puede salir de la grilla
    if not en_grilla(nueva_fila, nueva_columna):
        return

    # obstaculo
    if nueva_celda in estado["obstaculos"]:
        estado["aviso_bloqueo"] = pygame.time.get_ticks()
        return

    # bloqueo de sendero ya recorrido
    if nueva_celda in estado["sendero"]:
        estado["aviso_bloqueo"] = pygame.time.get_ticks()
        return

    # Si pasa las validaciones sigue
    estado["sendero"].append(nueva_celda)
    estado["cursor"] = nueva_celda
    estado["pasos"] += 1

    if sonido_paso is not None:
        sonido_paso.play()

    # Si la nueva celda tiene un item sin recolectar se recolecta
    if nueva_celda in estado["items"] and nueva_celda not in estado["items_recolectados"]:
        estado["items_recolectados"].append(nueva_celda)

   
    if nueva_celda == estado["merendero"]:
        estado["completado"] = True
        estado["tiempo_victoria"] = pygame.time.get_ticks()


def dibujar_grilla(pantalla, estado, fuente_chica, imagen_copernibot):
    celdas_sendero = set(estado["sendero"])

    for fila in range(FILAS):
        for columna in range(COLUMNAS):
            pixel_x, pixel_y = celda_a_pixel(fila, columna)
            rect_celda = pygame.Rect(pixel_x, pixel_y, TAMANO_CELDA, TAMANO_CELDA)

            color_celda = COLOR_CELDA
            if (fila, columna) in celdas_sendero:
                color_celda = COLOR_SENDERO
            if (fila, columna) in estado["obstaculos"]:
                color_celda = COLOR_OBSTACULO

            pygame.draw.rect(pantalla, color_celda, rect_celda)
            pygame.draw.rect(pantalla, COLOR_CELDA_BORDE, rect_celda, 1)

    # --- Dibujar ítems (monedas aun presentes en la pantalla) --- #
    for celda_item in estado["items"]:
        if celda_item not in estado["items_recolectados"]:
            pixel_x, pixel_y = celda_a_pixel(*celda_item)
            centro = (pixel_x + TAMANO_CELDA // 2, pixel_y + TAMANO_CELDA // 2)
            pygame.draw.circle(pantalla, COLOR_ITEM, centro, 10)
            pygame.draw.circle(pantalla, (120, 90, 0), centro, 10, 2)

    fila_merendero, columna_merendero = estado["merendero"]
    pixel_merendero_x, pixel_merendero_y = celda_a_pixel(fila_merendero, columna_merendero)

    pygame.draw.rect(pantalla, COLOR_MERENDERO,
                     (pixel_merendero_x + 6, pixel_merendero_y + 6,
                      TAMANO_CELDA - 12, TAMANO_CELDA - 12), 3)

    texto_merendero = fuente_chica.render("MERENDERO", True, COLOR_TEXTO)
    pantalla.blit(texto_merendero,
                  (pixel_merendero_x + TAMANO_CELDA // 2 - texto_merendero.get_width() // 2,
                   pixel_merendero_y + TAMANO_CELDA - 16))

    mitad = TAMANO_CELDA // 2
    sendero = estado["sendero"]
    for indice in range(1, len(sendero)):
        origen_x, origen_y = celda_a_pixel(*sendero[indice - 1])
        destino_x, destino_y = celda_a_pixel(*sendero[indice])
        pygame.draw.line(pantalla, (255, 255, 255),
                         (origen_x + mitad, origen_y + mitad),
                         (destino_x + mitad, destino_y + mitad), 4)

    fila_cursor, columna_cursor = estado["cursor"]
    pixel_cursor_x, pixel_cursor_y = celda_a_pixel(fila_cursor, columna_cursor)
    pantalla.blit(imagen_copernibot, (pixel_cursor_x + 2, pixel_cursor_y + 2))

    # --- Aviso visual cuando un movimiento fue bloqueado (pared o sendero repetido) ---
    ahora = pygame.time.get_ticks()
    if ahora - estado["aviso_bloqueo"] < TIEMPO_AVISO_MS:
        pixel_x, pixel_y = celda_a_pixel(fila_cursor, columna_cursor)
        rect_aviso = pygame.Rect(pixel_x, pixel_y, TAMANO_CELDA, TAMANO_CELDA)
        pygame.draw.rect(pantalla, COLOR_BLOQUEADO, rect_aviso, 3)


def dibujar_hud(pantalla, estado, fuente_mediana, fuente_chica):
    panel = pygame.Rect(HUD_X - 10, GRILLA_OFFSET_Y - 10,
                        PANTALLA_ANCHO - HUD_X, FILAS * TAMANO_CELDA + 20)
    pygame.draw.rect(pantalla, COLOR_HUD_BG, panel, border_radius=8)

    posicion_y = GRILLA_OFFSET_Y

    titulo_mision = fuente_mediana.render("Misión", True, COLOR_OK)
    pantalla.blit(titulo_mision, (HUD_X, posicion_y))
    posicion_y += titulo_mision.get_height() + 6

    lineas_mision = [
        "Acompaña a COPERNIBOT a dejar",
        "las donaciones en el merendero.",
    ]
    for linea in lineas_mision:
        texto_mision = fuente_chica.render(linea, True, COLOR_TEXTO)
        pantalla.blit(texto_mision, (HUD_X, posicion_y))
        posicion_y += texto_mision.get_height() + 2

    posicion_y += 14

    # --- Contador de pasos --- #
    texto_pasos = fuente_mediana.render(f"Pasos: {estado['pasos']}", True, COLOR_TEXTO)
    pantalla.blit(texto_pasos, (HUD_X, posicion_y))
    posicion_y += texto_pasos.get_height() + 6

    # --- Contador de monedas --- #
    total_items = len(estado["items"])
    recolectados = len(estado["items_recolectados"])
    texto_items = fuente_mediana.render(f"Monedas: {recolectados}/{total_items}", True, COLOR_ITEM)
    pantalla.blit(texto_items, (HUD_X, posicion_y))
    posicion_y += texto_items.get_height() + 18

    titulo_controles = fuente_mediana.render("Controles", True, COLOR_TEXTO)
    pantalla.blit(titulo_controles, (HUD_X, posicion_y))
    posicion_y += titulo_controles.get_height() + 10

    instrucciones = [
        "Flechas: Movimiento COPERNIBOT",
        "R      : Reiniciar nivel",
        "ESC    : Salir",
    ]
    for linea in instrucciones:
        texto_linea = fuente_chica.render(linea, True, COLOR_TEXTO_TENUE)
        pantalla.blit(texto_linea, (HUD_X, posicion_y))
        posicion_y += texto_linea.get_height() + 4


def dibujar_cartel_completado(pantalla, estado, fuente_grande, fuente_mediana):
    overlay = pygame.Surface((PANTALLA_ANCHO, PANTALLA_ALTO), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    pantalla.blit(overlay, (0, 0))

    cartel_ancho = 520
    cartel_alto = 200
    cartel_x = PANTALLA_ANCHO // 2 - cartel_ancho // 2
    cartel_y = PANTALLA_ALTO // 2 - cartel_alto // 2
    pygame.draw.rect(pantalla, COLOR_HUD_BG,
                     (cartel_x, cartel_y, cartel_ancho, cartel_alto),
                     border_radius=12)
    pygame.draw.rect(pantalla, COLOR_OK,
                     (cartel_x, cartel_y, cartel_ancho, cartel_alto),
                     4, border_radius=12)

    # --- Animacion de victoria --- #
    tiempo_transcurrido = pygame.time.get_ticks() - estado["tiempo_victoria"]
    escala = 1.0 + 0.12 * math.sin(tiempo_transcurrido / 150.0)

    texto_titulo_base = fuente_grande.render("NIVEL COMPLETADO", True, COLOR_OK)
    ancho_escalado = int(texto_titulo_base.get_width() * escala)
    alto_escalado = int(texto_titulo_base.get_height() * escala)
    texto_titulo = pygame.transform.smoothscale(texto_titulo_base, (ancho_escalado, alto_escalado))
    pantalla.blit(texto_titulo,
                  (PANTALLA_ANCHO // 2 - texto_titulo.get_width() // 2,
                   cartel_y + 50))

    texto_subtitulo = fuente_mediana.render("Llegaste al merendero", True, COLOR_TEXTO)
    pantalla.blit(texto_subtitulo,
                  (PANTALLA_ANCHO // 2 - texto_subtitulo.get_width() // 2,
                   cartel_y + 105))

    # --- Resumen de juego --- #
    texto_resumen = fuente_mediana.render(
        f"Pasos: {estado['pasos']}   Monedas: {len(estado['items_recolectados'])}/{len(estado['items'])}",
        True, COLOR_TEXTO_TENUE)
    pantalla.blit(texto_resumen,
                  (PANTALLA_ANCHO // 2 - texto_resumen.get_width() // 2,
                   cartel_y + 140))


def crear_estado_de_juego():
    entrada = (0, 0)
    merendero = (7, 11)

    # --- Obstaculos (paredes) --- #
    obstaculos = [(2, 4), (3, 4), (5, 7), (4, 9)]

    # --- Items --- #
    items = [(1, 3), (3, 8), (6, 5)]

    estado_de_juego = {
        "merendero": merendero,
        "sendero": [entrada],
        "cursor": entrada,
        "ultimo_movimiento": 0,
        "completado": False,
        "pasos": 0,
        "obstaculos": obstaculos,
        "items": items,
        "items_recolectados": [],
        "aviso_bloqueo": -TIEMPO_AVISO_MS,  
        "tiempo_victoria": 0,
    }
    return estado_de_juego


def cargar_imagen_copernibot():
    ruta_imagen = os.path.join(os.path.dirname(__file__), "COPERNIBOT.png")
    imagen = pygame.image.load(ruta_imagen).convert_alpha()
    return pygame.transform.smoothscale(imagen, (TAMANO_CELDA - 4, TAMANO_CELDA - 4))


def cargar_sonido(nombre_archivo):
    ruta_sonido = os.path.join(os.path.dirname(__file__), nombre_archivo)
    print(f"Intentando cargar sonido desde: {ruta_sonido}")
    try:
        sonido = pygame.mixer.Sound(ruta_sonido)
        print(f"  -> OK, {nombre_archivo} se cargó correctamente.")
        return sonido
    except Exception as error:
        print(f"  -> ERROR al cargar {nombre_archivo}: {error}")
        return None


def main():
    pygame.init()
    pygame.mixer.init()
    pygame.display.set_caption("OFIRCA 2026 - Ronda 1: Inicio")
    pantalla = pygame.display.set_mode((PANTALLA_ANCHO, PANTALLA_ALTO))
    reloj = pygame.time.Clock()

    fuente_grande = pygame.font.SysFont("consolas", 28, bold=True)
    fuente_mediana = pygame.font.SysFont("consolas", 17)
    fuente_chica = pygame.font.SysFont("consolas", 14)

    imagen_copernibot = cargar_imagen_copernibot()
    sonido_paso = cargar_sonido("ram_sneeze.mp3")
    ruta_sonido_victoria = os.path.join(os.path.dirname(__file__), "subaru_victory.mp3")

    estado = crear_estado_de_juego()
    ya_sono_victoria = False

    juego_en_ejecucion = True

    while juego_en_ejecucion:
        ahora = pygame.time.get_ticks()
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                juego_en_ejecucion = False
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    juego_en_ejecucion = False
                elif evento.key == pygame.K_r:
                    # --- Reinicio (R) ---
                    estado = crear_estado_de_juego()
                    ya_sono_victoria = False
                    pygame.mixer.music.stop()

        if not estado["completado"]:
            if ahora - estado["ultimo_movimiento"] >= COOLDOWN_MS:
                teclas = pygame.key.get_pressed()
                delta_fila, delta_columna = 0, 0
                if teclas[pygame.K_UP]:
                    delta_fila = -1
                elif teclas[pygame.K_DOWN]:
                    delta_fila = 1
                elif teclas[pygame.K_LEFT]:
                    delta_columna = -1
                elif teclas[pygame.K_RIGHT]:
                    delta_columna = 1
                if delta_fila != 0 or delta_columna != 0:
                    mover_copernibot(estado, delta_fila, delta_columna, sonido_paso)
                    estado["ultimo_movimiento"] = ahora
        else:
            # Reproducir el sonido de victoria una sola vez al completar el nivel.
            # Usamos pygame.mixer.music (en vez de pygame.mixer.Sound) porque
            # es el módulo pensado para reproducir archivos como mp3: los va
            # leyendo de a poco (streaming) en vez de cargarlos enteros a la
            # memoria como "chunk". pygame.mixer.Sound con mp3 tiene un bug
            # conocido: después de varias reproducciones en la misma ejecución,
            # el sonido empieza a fallar o a no sonar. music.play() no tiene
            # ese problema. (explicacion que dio claude acerca del error)
            if not ya_sono_victoria:
                try:
                    pygame.mixer.music.load(ruta_sonido_victoria)
                    pygame.mixer.music.play()
                    print("Reproduciendo sonido de victoria...")
                except Exception as error:
                    print(f"No se pudo reproducir el sonido de victoria: {error}")
                ya_sono_victoria = True

        pantalla.fill(COLOR_FONDO)
        dibujar_grilla(pantalla, estado, fuente_chica, imagen_copernibot)
        dibujar_hud(pantalla, estado, fuente_mediana, fuente_chica)
        if estado["completado"]:
            dibujar_cartel_completado(pantalla, estado, fuente_grande, fuente_mediana)

        pygame.display.flip()
        reloj.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
