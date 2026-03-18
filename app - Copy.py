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

@app.route("/login", methods=["GET","POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "admin":
            return redirect("/dashboard")

        else:
            return "Invalid Login"

    return render_template("login.html")

#-logout

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

    import subprocess
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
        rows = rows,
        accuracy = accuracy
    )


# ---------------- PREDICTION PAGE ----------------

@app.route("/prediction", methods=["GET","POST"])
def prediction():

    global total_predictions
    global safe_predictions
    global unsafe_predictions

    if request.method == "POST":

        temp = float(request.form["temp"])
        maxt = float(request.form["maxtemp"])
        wind = float(request.form["windspeed"])
        cloud = float(request.form["cloudcover"])
        precip = float(request.form["precip"])
        humidity = float(request.form["humidity"])

        data = [[temp, maxt, wind, cloud, precip, humidity]]

        pred = model.predict(data)[0]

        total_predictions += 1

        if pred == 0:
            safe_predictions += 1
            result = "SAFE"
        else:
            unsafe_predictions += 1
            result = "UNSAFE"

        return render_template(
            "prediction.html",
            prediction=result,
            temp=temp,
            maxt=maxt,
            wind=wind,
            cloud=cloud,
            precip=precip,
            humidity=humidity
        )

    return render_template("prediction.html")


# ---------------- PREDICTION PERFORMANCE ----------------

@app.route("/pred_perf")
def pred_perf():

    return render_template(
        "pred_perf.html",
        total = total_predictions,
        safe = safe_predictions,
        unsafe = unsafe_predictions
    )


# ---------------- RUN SERVER ----------------

if __name__ == "__main__":
    app.run(debug=True)