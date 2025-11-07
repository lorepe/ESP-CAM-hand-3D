# ...existing code...
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
        return None
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
        if not ret:
            continue

        img = detector.findHands(img)
        lmList, bbox = detector.findPosition(img)

        # Preparar panel negro a la derecha
        h, w = img.shape[:2]
        panel_w = 300
        panel = np.zeros((h, panel_w, 3), dtype=np.uint8)  # negro
        combined = np.concatenate((img, panel), axis=1)

        angles = [None]*5

        if len(lmList) != 0:
            # Crear diccionario id -> (x,y) por si lmList viene en formato [id, x, y]
            pos = {lm[0]: (lm[1], lm[2]) for lm in lmList}

            fingers = detector.fingersUp()
            mensaje = ''.join(map(str, fingers))  # Ejemplo: "10110"
            arduino.write((mensaje + '\n').encode())  # Enviar con salto de línea

            # Calcular ángulos y dibujar marcadores en la imagen
            for i in range(5):
                inds = finger_indices.get(i)
                if inds and all(idx in pos for idx in inds):
                    mcp = pos[inds[0]]
                    pip = pos[inds[1]]
                    tip = pos[inds[2]]
                    angle = calculate_angle(mcp, pip, tip)
                    angles[i] = angle
                    # Dibujar círculos en pip y tip en la imagen original (izquierda)
                    cv2.circle(combined, (pip[0], pip[1]), 5, (0, 255, 0), cv2.FILLED)
                    cv2.circle(combined, (tip[0], tip[1]), 5, (0, 0, 255), cv2.FILLED)

            # Mostrar en terminal los grados (con símbolo y texto "grados" por compatibilidad)
            for i in range(5):
                name = finger_names[i]
                angle = angles[i]
                if angle is None:
                    print(f"{name}: N/A")
                else:
                    # Imprimir con símbolo y con palabra "grados" por si el símbolo no se muestra bien
                    print(f"{name}: {angle}°    ({angle} grados)")
            print()

            # Dibujar texto en el panel negro (a la derecha) en blanco
            start_x = w + 10  # área del panel empieza en w, dibujamos con offset
            y0 = 40
            for i in range(5):
                name = finger_names[i]
                state = "arriba" if fingers[i] == 1 else "abajo"
                angle_text = f"{angles[i]}°" if angles[i] is not None else "N/A"
                text = f"{name}: {state}  {angle_text}"
                # cv2.putText se aplica a la imagen combinada; ajustar x en el panel
                cv2.putText(combined, text, (w + 10, y0 + i*35), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2, cv2.LINE_AA)

        else:
            # Si no hay mano detectada, mostrar mensaje en el panel
            cv2.putText(combined, "No se detecta mano", (w + 10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200,200,200), 2, cv2.LINE_AA)

        # Mostrar imagen combinada con matplotlib (izquierda video, derecha panel negro)
        img_rgb = cv2.cvtColor(combined, cv2.COLOR_BGR2RGB)
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
# ...existing code...