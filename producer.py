import time
import sys
import cv2
import tensorflow as tf
from tensorflow import keras
import numpy as np

from kafka import KafkaProducer
from kafka.errors import KafkaError

producer = KafkaProducer(bootstrap_servers='localhost:9092')
topic = 'my-topic'

import tensorflow as tf
from keras.models import load_model

# define the custom optimizer
custom_optimizer = tf.keras.optimizers.RMSprop(learning_rate=0.001)

# load the Keras model, passing the custom optimizer to custom_objects
model = keras.models.load_model('/home/william/Downloads/my_model.h5' , custom_objects={'RMSprop': custom_optimizer}, compile=False)

# Definir la lista de etiquetas
labels = ['piedra', 'papel', 'tijera']


def emit_video(path_to_video):
    print('start')

    video = cv2.VideoCapture(path_to_video)

    while video.isOpened():
        success, frame = video.read()
        if not success:
            break

        
        img_array = cv2.resize(frame, (150, 150))

        # Convertir la imagen a un arreglo de numpy
        # img_array = np.array(data)

        # Normalizar la imagen
        img_array = img_array / 255.

        # Añadir una dimensión adicional para que coincida con la forma de entrada del modelo
        img_array = tf.expand_dims(img_array, 0)

        # Hacer la predicción
        prediction = model.predict(img_array)

        # Obtener el índice del valor máximo en la salida de la predicción
        predicted_index = np.argmax(prediction)

        # Obtener el nombre de la etiqueta correspondiente al índice
        predicted_label = labels[predicted_index]

        # Imprimir el nombre de la etiqueta predicha
        print(predicted_label)
 
        # Adjuntar la etiqueta predicha a la imagen
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame, predicted_label, (10, 50), font, 1, (255, 255, 255), 2, cv2.LINE_AA)

        _, data = cv2.imencode('.jpeg', frame)


        # Enviar el cuadro codificado en formato JPEG al servidor Kafka
        future = producer.send(topic, data.tobytes())

        try:
            future.get(timeout=5)
        except KafkaError as e:
            print(e)
            break

        print('.', end='', flush=True)

emit_video(0)
# zero is for open webcam or usb webcam
# can play a video just add video file in emit_video function
# rtsp camera stream add rtsp feed in emit_video function