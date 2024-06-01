from flask import Flask, flash, render_template, url_for, request, redirect, session
from werkzeug.utils import secure_filename
import os
import pandas as pd
import pymysql.cursors
import requests
import numpy as np
app = Flask(__name__)
app.config["SECRET_KEY"] = "mySecrecy" #session butuh secret key
app.jinja_env.filters["zip"] = zip
app.secret_key = "secret key" # untuk flash data

# encrypt and decrypt key

# Connect to the database
connection = pymysql.connect(host='localhost',
                             user='root',
                             password='',
                             database='aes_umpo',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

# KONFIGURASI LOGIN
@app.route("/", methods=["GET","POST"])
def login():
    if "no_induk" in session:
        return redirect(url_for("dashboard"))
    else:   
        # Jika button submit login diklik --> request POST
        if request.method == 'POST':
            username = request.form["username"]
            password = request.form["password"]
            with connection.cursor() as cursor:
                sql = "SELECT * FROM user WHERE no_induk=%s"
                cursor.execute(sql, username)
                result = cursor.fetchone()  
                # Auth
                if username == result['no_induk'] and password == result['password']:
                    session["no_induk"] = result['no_induk']
                    session["nama"]     = result['nama']
                    session["role"]     = str(result['role']) 
                    return redirect(url_for("dashboard"))
                else:
                    flash('Username atau password tidak tepat.', 'error')
                    return render_template("login.html")
        return render_template("login.html")
    
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "role" in session:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM kuis"
            cursor.execute(sql)
            kuis_list = cursor.fetchall()
        return render_template("index.html", kuis=kuis_list)
    else:
        return redirect(url_for("login"))

@app.route("/logout") # hapus session
def logout():
    if "no_induk" and "nama" and "role" in session:
        session.pop("no_induk")
        session.pop("nama")
        session.pop("role")
    return redirect(url_for('login'))


# End of KONFIGURASI LOGIN

# UPLOAD FILE CSV

ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
@app.route("/upload", methods=["GET", "POST"])
def upload_file():
    if request.method == 'POST':
        API_URL = "https://api-inference.huggingface.co/models/cassador/indobert-embedding-2epoch"
        headers = {"Authorization": "Bearer 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"}
        def query(payload):
            response = requests.post(API_URL, headers=headers, json=payload)
            return response.json()
        # check if the post request has the file part
        if request.files['file']:
            file = request.files['file']
        df = pd.read_csv(file, sep=";")
        df.fillna("", inplace=True)
        id_kuis = request.form["id_kuis"]
        kolom_jawaban_essay = request.form["kolom_jawaban_essay"].split()
        kolom_identitas     = request.form["kolom_identitas"].split()
        jawaban     = df[kolom_jawaban_essay].to_dict(orient='list')
        identitas   = df[kolom_identitas].to_dict(orient='list')
        jawaban_list = []
        for value in jawaban.values():
            li = value
            jawaban_list.append(li)
        output_all = {} #untuk menampung hasil semua operasi
       #ambil jawaban kunci dari database
        with connection.cursor() as cursor:
            sql = "SELECT * FROM soal WHERE id_kuis=%s"
            cursor.execute(sql,id_kuis)
            jawaban_kunci = cursor.fetchall()
        for i in range (len(jawaban_kunci)):
            jawaban_per_soal = jawaban_list[i]
            output = query({
                "inputs": {
                    "source_sentence": jawaban_kunci[i]["jawaban_kunci"],
                    "sentences": jawaban_per_soal
                },
            })
            score = [round(score*jawaban_kunci[i]["bobot_nilai"]) for score in output]
            output_all[i+1] = score
        identitas.update(output_all)
        hasil_scoring = pd.DataFrame(identitas)
        hasil_scoring.to_excel('hasil_scoring.xlsx')
        return "Hasil scoring berhasil didownload"
    
# End of UPLOAD FILE CSV

# USER MANAGEMENT
@app.route("/user", methods=["GET", "POST"])
def view_user():
    if session["role"] == '1':
        with connection.cursor() as cursor:
                sql = "SELECT * FROM user"
                cursor.execute(sql)
                result = cursor.fetchall()
        return render_template("view_user.html", data=result)
    else:
        return redirect(url_for("dashboard"))
    
# End of USER MANAGEMENT


# MATA KULIAH MANAGEMENT
