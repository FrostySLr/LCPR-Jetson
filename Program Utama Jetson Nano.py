import sklearn
import cv2
import torch
from torchvision.transforms import functional as F
import os
import csv
import time
import re
import serial
from paddleocr import PaddleOCR
from datetime import datetime

# Konfigurasi komunikasi serial dengan Arduino
ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
time.sleep(2)  # Tunggu koneksi serial siap

# Load the fine-tuned model
model_path = "newbestlite.pth"
device = torch.device("cuda")
model = torch.load(model_path, map_location=device)
model.eval()

# Initialize PaddleOCR
ocr = PaddleOCR(use_angle_cls=False, lang='en')

# Label untuk deteksi
target_label = "plat-nomor"

# Folder untuk menyimpan hasil
output_folder = "capture_new"
os.makedirs(output_folder, exist_ok=True)

# CSV file path for saving results
csv_file_path = os.path.join(output_folder, "detected_plates.csv")

# Cek file terakhir di folder capture
def get_next_image_counters():
    """Mendapatkan nomor file terakhir untuk full_frame dan crop."""
    existing_files = [f for f in os.listdir(output_folder) if re.match(r'^(full_frame|crop)\d+\.jpg$', f)]
    full_frame_numbers = [int(re.search(r'full_frame(\d+)\.jpg', f).group(1)) for f in existing_files if "full_frame" in f]
    crop_numbers = [int(re.search(r'crop(\d+)\.jpg', f).group(1)) for f in existing_files if "crop" in f]

    next_full_frame = max(full_frame_numbers, default=0) + 1
    next_crop = max(crop_numbers, default=0) + 1
    return next_full_frame, next_crop

# Inisialisasi image counter
image_counter, crop_counter = get_next_image_counters()

# Cek atau buat file CSV
if not os.path.exists(csv_file_path):
    with open(csv_file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp", "License Plate", "Full Image Filename", "Crop Filename", "Processing Time (s)"])

# Webcam capture
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 800)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 600)
print("Waiting for VLD Signal...")

def draw_bounding_boxes(image, predictions):
    """Draw bounding boxes on the image."""
    for box, score, label in zip(predictions['boxes'], predictions['scores'], predictions['labels']):
        if label == target_label_id and score > 0.5:
            x1, y1, x2, y2 = map(int, box.tolist())
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(image, f"{target_label}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

def crop_plate(image, predictions):
    """Crop the plate from the image."""
    crops = []
    for box, score, label in zip(predictions['boxes'], predictions['scores'], predictions['labels']):
        if label == target_label_id and score > 0.5:
            x1, y1, x2, y2 = map(int, box.tolist())
            cropped = image[y1:y2, x1:x2]
            crops.append((cropped, score))
    return crops

def recognize_text(image):
    """Recognize text from an image using PaddleOCR."""
    results = ocr.ocr(image, cls=True)
    if results[0]:
        first_line = results[0][0][1][0]
        return first_line
    return ""

target_label_id = 1  # Default jika label hanya numerik

try:
    is_vehicle_detected = False

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Fail to capture Image from webcam.")
            break

        cv2.imshow("Preview Webcam", frame)

        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').strip()
            
            if line == "Vehicle Detected" and not is_vehicle_detected:
                print("Vehicle Detected. Starting License Plate Detection...")
                is_vehicle_detected = True

                start_time = time.time()

                # Konversi frame ke tensor
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_tensor = F.to_tensor(frame_rgb).unsqueeze(0).to(device)

                with torch.no_grad():
                    outputs = model(frame_tensor)
                outputs = [{k: v.cpu() for k, v in t.items()} for t in outputs]
                predictions = outputs[0]

                # Gambar bounding box di frame
                draw_bounding_boxes(frame, predictions)

                # Simpan frame full dengan bounding box
                full_image_filename = os.path.join(output_folder, f"full_frame{image_counter}.jpg")
                cv2.imwrite(full_image_filename, frame)
                print(f"Full Picture with Bounding Box will be saved at: {full_image_filename}")

                # Crop dan simpan hasil
                crops = crop_plate(frame, predictions)
                with open(csv_file_path, mode='a', newline='') as file:
                    writer = csv.writer(file)
                    for crop, score in crops:
                        crop_filename = os.path.join(output_folder, f"crop{crop_counter}.jpg")
                        cv2.imwrite(crop_filename, crop)
                        print(f"Cropped Picture saved at: {crop_filename}")

                        crop_rgb = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
                        text = recognize_text(crop_rgb)
                        print(f"Extracted Text: {text}")

                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        processing_time = time.time() - start_time
                        writer.writerow([timestamp, text, full_image_filename, crop_filename, processing_time])

                        crop_counter += 1  # Naikkan counter untuk file crop berikutnya

                image_counter += 1

            elif line == "No Vehicle Detected":
                is_vehicle_detected = False

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("Program dihentikan oleh pengguna.")
finally:
    ser.close()
    cap.release()
    cv2.destroyAllWindows()

