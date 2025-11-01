import numpy as np
import parcial.handDetector as hand
import time
import cv2
import serial

# Configuración del puerto serie para Arduino
arduino_port = 'COM10'  # Cambia esto por el puerto de tu Arduino ('/dev/ttyUSB0' en Linux o Mac)
baud_rate = 9600       # Debe coincidir con el código en el Arduino
ser = serial.Serial(arduino_port, baud_rate, timeout=1)
time.sleep(2)  # Espera a que se inicie la conexión con Arduino

# Abrir una cámara para capturar video
# url = 'http://192.168.190.134/480x320.jpg'
url = 'http://192.168.190.134/1600x1200.jpg'
cap = cv2.VideoCapture(url)

detector = hand.handDetector()  # Crear un objeto para encontrar puntos de referencia de la mano

while True:
    cap.open(url)
    ret, img = cap.read()  # Captura frame por frame

    if ret:
        img = detector.findHands(img)  # Buscar mano/s en la imagen
        lmList, bbox = detector.findPosition(img)  # Devuelve los puntos de referencia y el recuadro que encierra la mano
        
        if len(lmList) != 0:  # Verificar si hay mano
            fingers = detector.fingersUp()  # Verificar si los dedos están levantados
            
            # Imprimir el estado de cada dedo individualmente
            print("Pulgar:", "arriba" if fingers[0] == 1 else "abajo")
            print("Indice:", "arriba" if fingers[1] == 1 else "abajo")
            print("Medio:", "arriba" if fingers[2] == 1 else "abajo")
            print("Anular:", "arriba" if fingers[3] == 1 else "abajo")
            print("Meñique:", "arriba" if fingers[4] == 1 else "abajo")
            print()  # Agrega una línea en blanco para mejor legibilidad

            # Crear el mensaje para enviar a Arduino
            # Enviamos los valores de los dedos en formato binario (ejemplo: "10101")
            data_to_send = ''.join(map(str, fingers))  # Convierte la lista [1,0,1,0,1] en "10101"
            ser.write(data_to_send.encode())  # Envía datos como bytes a Arduino

        cv2.imshow("Image", img)  # Mostrar imagen

    if cv2.waitKey(1) == ord('q'):  # Presionar la letra 'q' para cerrar
        break

cap.release()  # Liberar cámara
cv2.destroyAllWindows()  # Destruir o cerrar las ventanas
ser.close()  # Cerrar la conexión serie con Arduino
