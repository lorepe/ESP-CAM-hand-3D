import numpy as np
import parcial.handDetector as hand
import cv2
import matplotlib.pyplot as plt
import serial
import time

# Inicializa el puerto serial
arduino = serial.Serial('COM3', 9600)
time.sleep(2)  # Espera a que se estabilice la conexión

# Abrir la cámara web local
cap = cv2.VideoCapture(0)

# Verifica que la cámara se haya abierto correctamente
if not cap.isOpened():
    print("Error: No se pudo acceder a la cámara web.")
    exit()

detector = hand.handDetector()

plt.ion()  # Activar modo interactivo de matplotlib

# Función para calcular ángulo entre tres puntos (grados)
def calculate_angle(a, b, c):
    # a, b, c son tuplas (x, y); calcula el ángulo en b entre ba y bc
    ba = (a[0] - b[0], a[1] - b[1])
    bc = (c[0] - b[0], c[1] - b[1])
    dot = ba[0]*bc[0] + ba[1]*bc[1]
    mag1 = np.hypot(ba[0], ba[1])
    mag2 = np.hypot(bc[0], bc[1])
    if mag1 * mag2 == 0:
        return 0
    angle = np.degrees(np.arccos(np.clip(dot / (mag1 * mag2), -1.0, 1.0)))
    return int(angle)

# Índices aproximados de los landmarks (Mediapipe): (mcp, pip, tip)
finger_indices = {
    0: (2, 3, 4),    # Pulgar
    1: (5, 6, 8),    # Indice
    2: (9, 10, 12),  # Medio
    3: (13, 14, 16), # Anular
    4: (17, 18, 20)  # Meñique
}

finger_names = ["Pulgar", "Indice", "Medio", "Anular", "Meñique"]

try:
    while True:
        ret, img = cap.read()

        if ret:
            img = detector.findHands(img)
            lmList, bbox = detector.findPosition(img)

            if len(lmList) != 0:
                # Crear diccionario id -> (x,y) por si lmList viene en formato [id, x, y]
                pos = {lm[0]: (lm[1], lm[2]) for lm in lmList}

                fingers = detector.fingersUp()
                print("Pulgar:", "arriba" if fingers[0] == 1 else "abajo")
                print("Indice:", "arriba" if fingers[1] == 1 else "abajo")
                print("Medio:", "arriba" if fingers[2] == 1 else "abajo")
                print("Anular:", "arriba" if fingers[3] == 1 else "abajo")
                print("Meñique:", "arriba" if fingers[4] == 1 else "abajo")
                print()

                mensaje = ''.join(map(str, fingers))  # Ejemplo: "10110"
                arduino.write((mensaje + '\n').encode())  # Enviar con salto de línea

                # Dibujar estado y ángulo de cada dedo en la imagen
                y0 = 30
                for i in range(5):
                    name = finger_names[i]
                    state = "arriba" if fingers[i] == 1 else "abajo"
                    angle = 0
                    # Si tenemos las coordenadas necesarias, calcular ángulo
                    inds = finger_indices.get(i)
                    if inds and all(idx in pos for idx in inds):
                        mcp = pos[inds[0]]
                        pip = pos[inds[1]]
                        tip = pos[inds[2]]
                        angle = calculate_angle(mcp, pip, tip)
                        # Dibujar círculos en pip y tip
                        cv2.circle(img, (pip[0], pip[1]), 5, (0, 255, 0), cv2.FILLED)
                        cv2.circle(img, (tip[0], tip[1]), 5, (0, 0, 255), cv2.FILLED)

                    text = f"{name}: {state} {angle}°"
                    cv2.putText(img, text, (10, y0 + i*25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

            # Mostrar imagen con matplotlib
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            plt.imshow(img_rgb)
            plt.axis('off')
            plt.draw()
            plt.pause(0.001)
            plt.clf()

except KeyboardInterrupt:
    pass
finally:
    cap.release()
    arduino.close()
    cv2.destroyAllWindows()