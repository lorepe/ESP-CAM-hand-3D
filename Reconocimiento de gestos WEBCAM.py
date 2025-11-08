import numpy as np
import handDetector as hand
import cv2
import matplotlib.pyplot as plt
import serial
import time

# Inicializa el puerto serial
arduino = serial.Serial('COM7', 9600)
time.sleep(2)

# Abrir la cámara web local
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: No se pudo acceder a la cámara web.")
    exit()

detector = hand.handDetector()
plt.ion()

# Función para calcular ángulo entre tres puntos
def calculate_angle(a, b, c):
    ba = (a[0] - b[0], a[1] - b[1])
    bc = (c[0] - b[0], c[1] - b[1])
    dot = ba[0]*bc[0] + ba[1]*bc[1]
    mag1 = np.hypot(ba[0], ba[1])
    mag2 = np.hypot(bc[0], bc[1])
    if mag1 * mag2 == 0:
        return None
    angle = np.degrees(np.arccos(np.clip(dot / (mag1 * mag2), -1.0, 1.0)))
    return int(angle)

# Índices de landmarks para cada dedo (mcp, pip, tip)
finger_indices = {
    0: (2, 3, 4),    # Pulgar
    1: (5, 6, 8),    # Índice
    2: (9, 10, 12),  # Medio
    3: (13, 14, 16), # Anular
    4: (17, 18, 20)  # Meñique
}

finger_names = ["Pulgar", "Indice", "Medio", "Anular", "Meñique"]

while True:
    ret, img = cap.read()
    if not ret:
        continue

    img = detector.findHands(img)
    lmList, bbox = detector.findPosition(img)

    # Crear panel negro a la derecha
    h, w = img.shape[:2]
    panel_w = 300
    panel = np.zeros((h, panel_w, 3), dtype=np.uint8)
    combined = np.concatenate((img, panel), axis=1)

    if len(lmList) != 0:
        fingers = detector.fingersUp()
        pos = {lm[0]: (lm[1], lm[2]) for lm in lmList}
        angles = [None]*5

        for i in range(5):
            inds = finger_indices.get(i)
            if inds and all(idx in pos for idx in inds):
                a = pos[inds[0]]
                b = pos[inds[1]]
                c = pos[inds[2]]
                angle = calculate_angle(a, b, c)
                angles[i] = angle

        # Mostrar en terminal
        for i in range(5):
            estado = "arriba" if fingers[i] == 1 else "abajo"
            angulo = f"{angles[i]} grados" if angles[i] is not None else "N/A"
            print(f"{finger_names[i]}: {estado} - {angulo}")
        print()

        # Enviar al Arduino
        mensaje = ''.join(map(str, fingers))
        arduino.write((mensaje + '\n').encode())

        # Dibujar texto en el panel negro
        y0 = 40
        for i in range(5):
            estado = "arriba" if fingers[i] == 1 else "abajo"
            angulo = f"{angles[i]} grados" if angles[i] is not None else "N/A"
            texto = f"{finger_names[i]}: {estado}  {angulo}"
            cv2.putText(combined, texto, (w + 10, y0 + i*35), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)

    else:
        cv2.putText(combined, "No se detecta mano", (w + 10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200,200,200), 2)

    # Mostrar imagen con matplotlib
    img_rgb = cv2.cvtColor(combined, cv2.COLOR_BGR2RGB)
    plt.imshow(img_rgb)
    plt.axis('off')
    plt.draw()
    plt.pause(0.001)
    plt.clf()

# Puedes presionar Ctrl+C para detener el script manualmente
cap.release()
arduino.close()
cv2.destroyAllWindows()