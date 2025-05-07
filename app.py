from flask import Flask, render_template, request, send_from_directory, redirect
import os
import pandas as pd
import json

app = Flask(__name__)

BASE_DIR = r"D:\Images Dataset"
FORMS_DIR = "forms"
AVAILABLE_FORMS = [f"form{i}.json" for i in range(1, 11)]
EMOTIONS = ["Happy", "Sad", "Angry", "Fear", "Surprise", "Disgust", "Contempt"]

@app.route('/')
def home():
    return redirect('/label')

@app.route('/label', methods=['GET', 'POST'])
def label_images():
    selected_form = request.args.get("form", "form1.json")
    form_path = os.path.join(FORMS_DIR, selected_form)

    if not os.path.exists(form_path):
        return f"Form file {selected_form} not found.", 404

    with open(form_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return render_template("labeling.html",
                           images=data["images"],
                           emotions=EMOTIONS,
                           forms=AVAILABLE_FORMS,
                           selected_form=selected_form)

@app.route('/submit_labels', methods=['POST'])
def submit_labels():
    subject_id = request.form.get("subject_id")
    selected_form = request.form.get("form_id")
    total = int(request.form.get("total"))

    data = []
    for i in range(total):
        entry = {
            "form": selected_form,
            "subject_id": subject_id,
            "filename": request.form.get(f"filename_{i}"),
            "model": request.form.get(f"model_{i}"),
            "category": request.form.get(f"category_{i}"),
            "true_emotion": request.form.get(f"true_emotion_{i}"),
            "perceived_emotion": request.form.get(f"perceived_emotion_{i}"),
            "rating": request.form.get(f"rating_{i}")
        }
        data.append(entry)

    df = pd.DataFrame(data)
    response_file = "responses.xlsx"
    if os.path.exists(response_file):
        old_df = pd.read_excel(response_file)
        df = pd.concat([old_df, df], ignore_index=True)

    df.to_excel(response_file, index=False)
    return redirect(f"/label?form={selected_form}")

@app.route('/serve_image')
def serve_image():
    model = request.args.get("model")
    category = request.args.get("category")
    emotion = request.args.get("emotion")
    filename = request.args.get("filename")
    folder = os.path.join(BASE_DIR, model, category, emotion)
    return send_from_directory(folder, filename)

if __name__ == '__main__':
    app.run(debug=True)
