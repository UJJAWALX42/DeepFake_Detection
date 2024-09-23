from flask import Flask, request, jsonify
import os
import cv2
import numpy as np
import torch
from model import DeepFakeModel 
from utils import preprocess_image 

app = Flask(__name__)


model_path = 'weights/best_model.pth' 
model = DeepFakeModel()
model.load_state_dict(torch.load(model_path))
model.eval()  

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    
    file_path = os.path.join('uploads', file.filename)
    file.save(file_path)


    image = preprocess_image(file_path) 
    image_tensor = torch.from_numpy(image).unsqueeze(0) 


    with torch.no_grad():
        output = model(image_tensor)
        prediction = torch.sigmoid(output).numpy().flatten()

   
    confidence = prediction[0]
    result = 'Fake' if confidence > 0.5 else 'Real'

    return jsonify({
        'result': result,
        'confidence': confidence
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
