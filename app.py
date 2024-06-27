import os
import io
import base64
from flask import Flask, render_template_string, request
from werkzeug.utils import secure_filename
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np
import matplotlib.pyplot as plt

app = Flask(__name__)

# Path to your pre-trained model
MODEL_PATH = 'C:\\Users\\vrund\\Desktop\\IProject\\image-classification\\cifar10_model.h5'
model = load_model(MODEL_PATH)
print("Model loaded successfully")

# Define your class labels (CIFAR-10 classes)
class_labels = ['airplane', 'automobile', 'bird', 'cat', 'deer', 'dog', 'frog', 'horse', 'ship', 'truck']

# HTML template with enhanced CSS for styling
html_template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Image Classification</title>
    <style>
        body {
            font-family: 'Poppins', sans-serif;
            margin: 0;
            padding: 0;
            background-color: #0c2233; /* fourth-color */
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }

        .container {
            background-color: #fce38a; /* first-color */
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
            text-align: center;
            width: 95%;
            max-width: 800px;
            position: relative;
            overflow: hidden;
            margin: 40px 0; /* Increased margin */
        }

        .pulse, .result {
            font-size: 2.5rem;
            letter-spacing: 5px;
            color: #0e5f76; /* second-color */
            text-transform: uppercase;
            width: 100%;
            text-align: center;
            line-height: 0.85em;
            outline: none;
            animation: animate 5s linear infinite;
            margin: 10px 0;
            text-shadow: 0 0 10px #03bcf4, 0 0 20px #03bcf4, 0 0 40px #03bcf4, 0 0 80px #03bcf4, 0 0 160px #03bcf4;
        }

        @keyframes animate {
            0%, 18%, 20%, 50.1%, 60%, 65.1%, 80%, 90.1%, 92%, 100% {
                color: #0e5f76; /* second-color */
                box-shadow: none;
            }
            100% {
                color: #fff;
                text-shadow: 0 0 10px #03bcf4, 0 0 20px #03bcf4, 0 0 40px #03bcf4, 0 0 80px #03bcf4, 0 0 160px #03bcf4;
            }
        }

        form {
            margin: 20px 0;
        }

        .file-input {
            position: relative;
            margin-bottom: 20px;
        }

        .file-input input[type="file"] {
            opacity: 0;
            width: 100%;
            height: 50px;
            position: absolute;
            top: 0;
            left: 0;
            cursor: pointer;
        }

        .file-input label {
            display: block;
            background-color: #083d56; /* third-color */
            color: white;
            padding: 15px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            transition: background-color 0.3s ease;
            font-size: 1.1em;
            box-shadow: 0 0 10px rgba(8, 61, 86, 0.7);
            position: relative;
            overflow: hidden;
        }

        .file-input label::before {
            content: '\\f382';
            font-family: 'Font Awesome 5 Free';
            font-weight: 900;
            position: absolute;
            top: 50%;
            left: 20px;
            transform: translateY(-50%);
        }

        .file-input label:hover {
            background-color: #72e8e1; /* second-color */
        }

        .submit-btn {
            background-color: #083d56; /* third-color */
            color: white;
            padding: 15px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            transition: background-color 0.3s ease;
            font-size: 1.1em;
            box-shadow: 0 0 10px rgba(8, 61, 86, 0.7);
            animation: pulse-animation 1.5s infinite;
        }

        .submit-btn:hover {
            background-color: #0e5f76; /* second-color */
        }

        .result-container, .bar-graph-container {
            margin-top: 60px; /* Increased margin for more space */
            text-align: center;
        }

        .result-container img {
            max-width: 100%;
            height: auto;
            border-radius: 15px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
        }

        .bar-graph-container img {
            max-width: 100%;
            height: auto;
            border-radius: 15px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
        }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="pulse">Image Classification</h1>
        <form method="POST" enctype="multipart/form-data">
            <div class="file-input">
                <input type="file" name="file" id="file">
                <label for="file">Choose a file</label>
            </div>
            <button type="submit" class="submit-btn">Upload and Classify</button>
        </form>
        {% if result %}
            <div class="result-container">
                <h2 class="result">Result: {{ result }}</h2>
                <img src="data:image/png;base64,{{ image_data }}" alt="Uploaded Image">
            </div>
            <div class="bar-graph-container">
                <h2 class="result">Prediction Probabilities</h2>
                <img src="data:image/png;base64,{{ bar_graph }}" alt="Bar Graph">
            </div>
        {% endif %}
    </div>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def upload_and_classify():
    if request.method == 'POST':
        if 'file' not in request.files:
            return "No file part"
        
        file = request.files['file']
        
        if file.filename == '':
            return "No selected file"
        
        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join('uploads', filename)
            file.save(file_path)
            
            img = image.load_img(file_path, target_size=(32, 32))
            img_array = image.img_to_array(img)
            img_array = np.expand_dims(img_array, axis=0)
            img_array /= 255.0
            
            predictions = model.predict(img_array)
            predicted_class = class_labels[np.argmax(predictions[0])]
            predicted_probabilities = predictions[0]

            plt.figure(figsize=(10, 6))
            plt.bar(class_labels, predicted_probabilities, color=['#fce38a', '#0e5f76', '#083d56', '#0c2233', '#03bcf4', '#0e3742', '#029ec3', '#cbf078', '#f8f398', '#f1b963'])
            plt.xlabel('Class', labelpad=20)
            plt.ylabel('Probability', labelpad=20)
            plt.xticks(rotation=45)
            plt.title('Class Probabilities')
            plt.tight_layout(pad=2.0)  # Add padding to the layout
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            bar_graph_data = base64.b64encode(buf.getvalue()).decode('utf-8')
            buf.close()

            with open(file_path, "rb") as img_file:
                image_data = base64.b64encode(img_file.read()).decode('utf-8')
            
            return render_template_string(html_template, result=predicted_class, image_data=image_data, bar_graph=bar_graph_data)
    
    return render_template_string(html_template, result=None)

if __name__ == '__main__':
    app.run(debug=True, port=1111)
