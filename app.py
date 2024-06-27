from flask import Flask, flash, render_template, url_for, request, redirect, session
from werkzeug.utils import secure_filename
import pandas as pd
import pymysql.cursors
import requests
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
        API_URL = "https://api-inference.huggingface.co/models/cassador/indobert-base-p2-nli-v2"
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
        hasil_scoring.to_excel('05juni.xlsx')
        return render_template("scoring_result.html")
    
# End of UPLOAD FILE CSV

# USER MANAGEMENT
# View user
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

# Create user
@app.route("/create_user", methods=["GET", "POST"])
def create_user():
    if request.method == 'POST':
        with connection.cursor() as cursor:
            #ambil data
            nik = request.form["nik"]
            nama = request.form["nama"]
            role = request.form["role"]
            password = request.form["password"]
            # Create a new record
            sql = "INSERT INTO `user` (`no_induk`, `nama`, `password`, `role`) VALUES (%s, %s, %s, %s)"
            data = nik, nama, password, role
            cursor.execute(sql, data)

            # connection is not autocommit by default. So you must commit to save
            # your changes.
            connection.commit()
            cursor.close()
        return redirect(url_for('view_user'))

# Update user
@app.route("/update_user", methods=["GET", "POST"])
def update_user():
    if request.method == 'POST':
        with connection.cursor() as cursor:
            #ambil data
            id_user = request.form["id_user"]
            nik = request.form["nik"]
            nama = request.form["nama"]
            role = request.form["role"]
            # Update a record
            sql = "UPDATE `user` SET no_induk=%s, nama=%s, role=%s WHERE id_user=%s"
            data = nik, nama, role, id_user
            cursor.execute(sql, data)
            
            connection.commit()
            cursor.close()
        return redirect(url_for('view_user'))

# Delete
@app.route("/delete_user", methods=["POST"])
def delete_user():
    if request.method == 'POST':
        with connection.cursor() as cursor:
            id_user = request.form["id_user"]
        
            # Delete record
            sql = "DELETE FROM `user` WHERE id_user=%s"
            cursor.execute(sql, id_user)

            # connection is not autocommit by default. So you must commit to save
            # your changes.
            connection.commit()
            cursor.close()
        return redirect(url_for('view_user'))
# End of USER MANAGEMENT


# MATA KULIAH MANAGEMENT
