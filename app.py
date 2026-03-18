from flask import Flask, render_template, request, redirect
import pickle
import pandas as pd
import subprocess

app = Flask(__name__)

# Load model
model = pickle.load(open("model.pickle", "rb"))

# Prediction statistics
total_predictions = 0
safe_predictions = 0
unsafe_predictions = 0


# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template("index.html")


# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "admin":
            return redirect("/dashboard")
        else:
            return "Invalid Login"

    return render_template("login.html")


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    return redirect("/")


# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


# ---------------- TRAINING PAGE ----------------
@app.route("/training")
def training():
    return render_template("training.html")


# ---------------- TRAIN MODEL ----------------
@app.route("/train_model")
def train_model():

    subprocess.run(["python", "training/train.py"])

    # after training return back to training page
    return redirect("/training?status=trained")


# ---------------- MODEL PERFORMANCE ----------------
@app.route("/model_perf")
def model_perf():

    data = pd.read_csv("training/final_data.csv")

    rows = len(data)
    accuracy = "Approx 99%"   # from train.py output

    return render_template(
        "model_perf.html",
        rows=rows,
        accuracy=accuracy
    )


# ---------------- PREDICTION PAGE ----------------
@app.route("/prediction", methods=["GET", "POST"])
def prediction():

    if request.method == "POST":

        temp = float(request.form["temp"])
        maxt = float(request.form["maxt"])
        wspd = float(request.form["wspd"])
        cloud = float(request.form["cloud"])
        precip = float(request.form["precip"])
        humidity = float(request.form["humidity"])

        values = [[temp, maxt, wspd, cloud, precip, humidity]]

        result = model.predict(values)[0]

        if result == 0:
            pred = "SAFE"
        else:
            pred = "UNSAFE"

        # ---------- EXPLAINABILITY ----------
        explanation = []

        if pred == "UNSAFE":

            if precip > 200:
                explanation.append("Heavy rainfall detected which increases flood probability.")

            if cloud > 70:
                explanation.append("High cloud cover indicates possible continuous rainfall.")

            if humidity > 80:
                explanation.append("High humidity supports storm formation.")

            if wspd > 100:
                explanation.append("Strong wind speeds indicate severe weather conditions.")

            if len(explanation) == 0:
                explanation.append("Combination of weather conditions indicates potential flood risk.")

        else:

            explanation.append("Rainfall levels are within safe limits.")
            explanation.append("Humidity and cloud cover are not high enough to trigger flood risk.")
            explanation.append("Overall weather conditions are stable.")

        return render_template(
            "prediction.html",
            temp=temp,
            maxt=maxt,
            wspd=wspd,
            cloud=cloud,
            precip=precip,
            humidity=humidity,
            pred=pred,
            explanation=explanation
        )

    return render_template("prediction.html")


# ---------------- PREDICTION PERFORMANCE ----------------


# ---------------- RUN SERVER ----------------
if __name__ == "__main__":
    app.run(debug=True)