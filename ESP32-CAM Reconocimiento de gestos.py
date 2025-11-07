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

while True:
    ret, img = cap.read()

    if ret:
        img = detector.findHands(img)
        lmList, bbox = detector.findPosition(img)

        if len(lmList) != 0:
            fingers = detector.fingersUp()
            print("Pulgar:", "arriba" if fingers[0] == 1 else "abajo")
            print("Indice:", "arriba" if fingers[1] == 1 else "abajo")
            print("Medio:", "arriba" if fingers[2] == 1 else "abajo")
            print("Anular:", "arriba" if fingers[3] == 1 else "abajo")
            print("Meñique:", "arriba" if fingers[4] == 1 else "abajo")
            print()

            mensaje = ''.join(map(str, fingers))  # Ejemplo: "10110"
            arduino.write((mensaje + '\n').encode())  # Enviar con salto de línea

        # Mostrar imagen con matplotlib
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        plt.imshow(img_rgb)
        plt.axis('off')
        plt.draw()
        plt.pause(0.001)
        plt.clf()

# Puedes presionar Ctrl+C para detener el script manualmente
cap.release()
arduino.close()
cv2.destroyAllWindows()