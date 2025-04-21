from django.shortcuts import render
from django.template.response import TemplateResponse
from django.core.files.storage import FileSystemStorage
from django.utils.datastructures import MultiValueDictKeyError
from django.conf import settings
from django.http import StreamingHttpResponse
from PIL import Image, ImageDraw
from ultralytics import YOLO
import numpy as np
import os
import cv2
from tensorflow.keras.models import load_model

# Load classification model globally
classification_model = load_model(r"C:/Users/raibh/Desktop/Clean-Care-Hub-main 3/Clean-Care-Hub-main 3/mobilenetv2_waste_classification.h5")



# Waste class labels
waste_labels = {
    0: "battery",
    1: "biological",
    2: "cardboard",
    3: "clothes",
    4: "glass",
    5: "metal",
    6: "paper",
    7: "plastic",
    8: "shoes",
    9: "trash"
}

# Dustbin color mapping
DUSTBIN_COLORS = {
    "battery": "blue",
    "biological": "green",
    "cardboard": "yellow",
    "clothes": "yellow",
    "glass": "blue",
    "metal": "blue",
    "paper": "yellow",
    "plastic": "blue",
    "shoes": "yellow",
    "trash": "brown",
}

# Optional: Class names for sanitation model (YOLO)
sanitation_classes = ["mixed", "restaurant-fastfood", "retail-groceries"]


class CustomFileSystemStorage(FileSystemStorage):
    def get_available_name(self, name, max_length=None):
        return name


# 🧼 Check Sanitation (YOLO detection)
def index(request):
    message = ""
    fss = CustomFileSystemStorage()

    try:
        # Clear old images
        media_root = settings.MEDIA_ROOT
        for filename in os.listdir(media_root):
            file_path = os.path.join(media_root, filename)
            if os.path.isfile(file_path):
                os.unlink(file_path)

        image = request.FILES["image"]
        _image = fss.save(image.name, image)
        path = os.path.join(settings.MEDIA_ROOT, _image)

        img = Image.open(path)
        img.thumbnail((480, 640))
        resized_path = os.path.join(settings.MEDIA_ROOT, "resized_image.jpg")
        img.save(resized_path)

        model = YOLO("best.pt")
        model.conf = 0.5

        img = Image.open(resized_path).convert("RGB")
        results = model(img)

        for detection in results:
            for box in detection.boxes.xyxy:
                x1, y1, x2, y2 = box.tolist()[:4]
                img_draw = ImageDraw.Draw(img)
                img_draw.rectangle([x1, y1, x2, y2], outline="yellow", width=5)

        result_image_path = os.path.join(settings.MEDIA_ROOT, "result_image.jpg")
        img.save(result_image_path)

        return TemplateResponse(
            request,
            "litterdetection.html",
            {
                "message": message,
                "image_url": fss.url(_image),
                "result_image_url": fss.url("result_image.jpg"),
            },
        )

    except MultiValueDictKeyError:
        return TemplateResponse(request, "litterdetection.html", {"message": "No Image Selected"})
    except Exception as e:
        return TemplateResponse(request, "litterdetection.html", {"message": str(e)})


# 📷 Live Sanitation Detection Feed (YOLO)
def live_video_feed(request):
    model = YOLO("best.pt")
    model.conf = 1.0

    def generate_frames():
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            raise Exception("Failed to open webcam")

        while True:
            success, frame = cap.read()
            if not success:
                break

            img = Image.fromarray(frame)
            results = model(img)

            for detection in results:
                for box in detection.boxes.xyxy:
                    x1, y1, x2, y2 = map(int, box[:4])
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            _, buffer = cv2.imencode(".jpg", frame)
            frame_bytes = buffer.tobytes()
            yield (b"--frame\r\n"
                   b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n")

        cap.release()

    return StreamingHttpResponse(generate_frames(), content_type="multipart/x-mixed-replace; boundary=frame")


# 🗑️ Smart Waste Classification (MobileNetV2)
def predict_waste(request):
    if request.method == "POST" and request.FILES.get("image"):
        image = request.FILES["image"]
        fss = FileSystemStorage()
        filename = fss.save(image.name, image)
        uploaded_image_url = fss.url(filename)

        image_path = os.path.join(settings.MEDIA_ROOT, filename)

        try:
            # Preprocess image for MobileNetV2
            img = Image.open(image_path).convert("RGB")
            img = img.resize((224, 224))
            img_array = np.array(img) / 255.0
            img_array = np.expand_dims(img_array, axis=0)

            # Predict
            predictions = classification_model.predict(img_array)
            predicted_index = np.argmax(predictions)
            confidence = round(float(np.max(predictions)) * 100, 2)
            predicted_label = waste_labels[predicted_index]
            bin_color = DUSTBIN_COLORS.get(predicted_label, "gray")

            return render(
                request,
                "waste_classifier.html",
                {
                    "image_url": uploaded_image_url,
                    "prediction": predicted_label,
                    "confidence": confidence,
                    "class_labels": waste_labels,
                    "bin_color": bin_color,
                },
            )
        except Exception as e:
            return render(request, "waste_classifier.html", {"message": str(e)})

    return render(request, "waste_classifier.html")
