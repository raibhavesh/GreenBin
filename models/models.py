from django.db import models

# Create your models here.
import os
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from django.conf import settings

# Load the model (update the filename if needed)
mobilenet_path = os.path.join(settings.BASE_DIR, 'mobilenetv2_waste_.h5')
mobilenet_model = load_model(mobilenet_path)

# Class labels (update these based on your model training)
class_labels = ['dry', 'wet', 'decomposable', 'non-decomposable']

def predict_mobilenet(img_path):
    img = image.load_img(img_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = img_array / 255.0

    prediction = mobilenet_model.predict(img_array)
    predicted_class = class_labels[np.argmax(prediction)]
    confidence = np.max(prediction)
    
    return predicted_class, confidence
