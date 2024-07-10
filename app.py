from flask import Flask, flash, render_template, url_for, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
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
                if username == result['no_induk'] and check_password_hash(result["password"], password):
                    session["no_induk"] = result['no_induk']
                    session["nama"]     = result['nama']
                    session["role"]     = str(result['role']) 
                    session["logged"]   = True
                    return redirect(url_for("dashboard"))
                else:
                    flash('Username atau password tidak tepat.', 'error')
                    return render_template("login.html")
        return render_template("login.html")
    
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "role" in session:
        with connection.cursor() as cursor:
            if session["role"] == "1":
                sql = f"SELECT kuis.id_kuis as id_kuis, kuis.kuis_ke as kuis_ke, matkul.nama_matkul as nama_matkul, user.nama as pengampu FROM kuis INNER JOIN matkul ON kuis.id_matkul=matkul.id_matkul INNER JOIN user ON matkul.id_dosen=user.id_user"
            else:
                sql = f"SELECT kuis.id_kuis as id_kuis, kuis.kuis_ke as kuis_ke, matkul.nama_matkul as nama_matkul, user.nama as pengampu FROM kuis INNER JOIN matkul ON kuis.id_matkul=matkul.id_matkul INNER JOIN user ON matkul.id_dosen=user.id_user WHERE user.no_induk={session['no_induk']}"
            cursor.execute(sql)
            kuis_list = cursor.fetchall()
        return render_template("index.html", kuis=kuis_list)
    else:
        return redirect(url_for("login"))

@app.route("/logout")
def logout():
    if "no_induk" and "nama" and "role" in session: # hapus session
        session.pop("no_induk")
        session.pop("nama")
        session.pop("role")
    return redirect(url_for('login'))
# End of KONFIGURASI LOGIN

# UPLOAD FILE CSV
ALLOWED_EXTENSIONS = {'csv'}
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/upload", methods=["GET", "POST"])
def upload_file():
    if request.method == 'POST':
        API_URL = "https://api-inference.huggingface.co/models/cassador/4bs4lr2"
        headers = {"Authorization": "Bearer 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"}

        def query(payload):
            response = requests.post(API_URL, headers=headers, json=payload)
            return response.json()
        # validasi file dan format file
        if request.files['file']:
            if allowed_file(request.files['file'].filename):
                file = request.files['file']
            else:
                flash('File tidak didukung, silakan upload file dengan format .csv', 'danger')
                return redirect(url_for("dashboard"))
            
        df = pd.read_csv(file, sep=";")
        df.fillna("", inplace=True)
        id_kuis             = request.form["id_kuis"]
        kolom_jawaban_essay = request.form["kolom_jawaban_essay"].split()
        kolom_identitas     = request.form["kolom_identitas"].split()
        try:
            jawaban = df[kolom_jawaban_essay].to_dict(orient='list')
            identitas = df[kolom_identitas].to_dict(orient='list')
        except KeyError as e:
            flash(str(e), 'danger')
            return redirect(url_for("dashboard")) 
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
            score = [round(max(0,score)*jawaban_kunci[i]["bobot_nilai"]) for score in output]
            output_all[i+1] = score
        identitas.update(jawaban)
        identitas.update(output_all)
        hasil_scoring = pd.DataFrame(identitas)
        try:
            hasil_scoring.to_excel(r"C:\Users\VGArt\Downloads\Hasil_Scoring.xlsx")
            flash('Hasil penilaian telah didownload', 'success')
        except:
            flash('Hasil penilaian gagal didownload', 'danger')
        return redirect(url_for("dashboard"))
# End of UPLOAD FILE CSV

# USER MANAGEMENT
# View user
@app.route("/user", methods=["GET", "POST"])
def view_user():
    if "role" in session:
        if session["role"] == '1':
            with connection.cursor() as cursor:
                    sql = "SELECT * FROM user"
                    cursor.execute(sql)
                    result = cursor.fetchall()
            return render_template("view_user.html", data=result)
        else:
            return redirect(url_for("dashboard"))
    else:
        return redirect(url_for("login"))

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
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
            # Create a new record
            sql = "INSERT INTO `user` (`no_induk`, `nama`, `password`, `role`) VALUES (%s, %s, %s, %s)"
            data = nik, nama, hashed_password, role
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

# Delete user
@app.route("/delete_user", methods=["POST"])
def delete_user():
    if request.method == 'POST':
        with connection.cursor() as cursor:
            id_user = request.form["id_user"]
            # Delete record
            sql2 = "DELETE FROM matkul WHERE id_dosen=%s"
            cursor.execute(sql2, id_user)
            sql = "DELETE FROM `user` WHERE id_user=%s"
            cursor.execute(sql, id_user)

            # connection is not autocommit by default. So you must commit to save
            # your changes.
            connection.commit()
            cursor.close()
        return redirect(url_for('view_user'))
# End of USER MANAGEMENT

# MATA KULIAH MANAGEMENT
# View Mata Kuliah
@app.route("/mata_kuliah", methods=["GET", "POST"])
def view_mata_kuliah():
    if "role" in session:
        with connection.cursor() as cursor:
            if session["role"] == '1':
                sql = "SELECT matkul.id_matkul as id_matkul, matkul.kode_matkul as kode, matkul.nama_matkul as matkul, matkul.tahun_ajaran as tahun_ajaran, user.id_user as id_user, user.nama as pengampu, user.no_induk as nik FROM matkul INNER JOIN user ON matkul.id_dosen=user.id_user"
                sql2 = "SELECT id_user, nama FROM user"
            else:
                sql = f"SELECT matkul.id_matkul as id_matkul, matkul.kode_matkul as kode, matkul.nama_matkul as matkul, matkul.tahun_ajaran as tahun_ajaran, user.id_user as id_user, user.nama as pengampu, user.no_induk as nik FROM matkul INNER JOIN user ON matkul.id_dosen=user.id_user WHERE user.no_induk={session['no_induk']}"
                sql2 = f"SELECT id_user, nama FROM user WHERE no_induk={session['no_induk']}"
            cursor.execute(sql)
            result = cursor.fetchall()
            cursor.execute(sql2)
            result2 = cursor.fetchall()
        return render_template("view_matkul.html", data_pengampu=result2, data=result, data_dosen=result)
    else:
        return redirect(url_for('login'))

# Create Mata Kuliah
@app.route("/create_mata_kuliah", methods=["GET", "POST"])
def create_mata_kuliah():
    if "role" in session:
        if request.method == 'POST':
            with connection.cursor() as cursor:
                #ambil data
                kode_matkul = request.form["kode_matkul"]
                matkul = request.form["matkul"]
                tahun_ajaran = request.form["tahun_ajaran"]
                id_dosen = request.form["id_dosen"]
                # Create a new record
                sql = "INSERT INTO `matkul` (`kode_matkul`, `nama_matkul`, `tahun_ajaran`, `id_dosen`) VALUES (%s, %s, %s, %s)"
                data = kode_matkul, matkul, tahun_ajaran, id_dosen
                cursor.execute(sql, data)

                # connection is not autocommit by default. So you must commit to save
                # your changes.
                connection.commit()
                cursor.close()
            return redirect(url_for('view_mata_kuliah'))
    else:
        return redirect(url_for('login'))

# Update Mata Kuliah
@app.route("/update_mata_kuliah", methods=["GET","POST"])
def update_mata_kuliah():
    if request.method == "POST":
        with connection.cursor() as cursor:
                #ambil data
                id_matkul    = request.form["id_matkul"]
                kode         = request.form["kode_matkul"]
                matkul       = request.form["matkul"]
                tahun_ajaran = request.form["tahun_ajaran"]
                id_dosen     = request.form["id_dosen"]
                # Update a record
                sql = "UPDATE `matkul` SET kode_matkul= %s, nama_matkul=%s, tahun_ajaran=%s, id_dosen=%s WHERE id_matkul=%s"
                data = kode, matkul, tahun_ajaran, id_dosen, id_matkul
                cursor.execute(sql, data)
                connection.commit()
                cursor.close()
        return redirect(url_for('view_mata_kuliah'))

# Delete Mata Kuliah
@app.route("/delete_mata_kuliah", methods=["POST"])
def delete_mata_kuliah():
    if request.method == "POST":
        with connection.cursor() as cursor:
            id_matkul = request.form["id_matkul"]
            # Delete record
            sql = "DELETE FROM `matkul` WHERE id_matkul=%s"
            cursor.execute(sql, id_matkul)
            # connection is not autocommit by default. So you must commit to save
            # your changes.
            connection.commit()
            cursor.close()
        return redirect(url_for('view_mata_kuliah'))
# END OF MATA KULIAH MANAGEMENT

# KUIS MANAGEMENT
# View
@app.route("/kuis", methods=["GET"])
def view_kuis():
    if "role" in session:
        with connection.cursor() as cursor:
            if session["role"] == '1':
                sql = "SELECT kuis.id_kuis as id_kuis, kuis.kuis_ke as kuis_ke, matkul.nama_matkul as matkul, matkul.kode_matkul as kode, matkul.id_matkul as id_matkul,  matkul.tahun_ajaran as tahun_ajaran, user.nama as pengampu FROM kuis INNER JOIN matkul ON kuis.id_matkul=matkul.id_matkul INNER JOIN user ON matkul.id_dosen=user.id_user"

                sql2 = "SELECT matkul.id_matkul as id_matkul, matkul.nama_matkul as nama_matkul, user.nama as pengampu from matkul INNER JOIN user ON matkul.id_dosen=user.id_user"
            else:
                sql = f"SELECT kuis.id_kuis as id_kuis, kuis.kuis_ke as kuis_ke, matkul.nama_matkul as matkul, matkul.kode_matkul as kode, matkul.id_matkul as id_matkul, matkul.tahun_ajaran as tahun_ajaran, user.nama as pengampu FROM kuis INNER JOIN matkul ON kuis.id_matkul=matkul.id_matkul INNER JOIN user ON matkul.id_dosen=user.id_user WHERE user.no_induk={session['no_induk']}"

                sql2 = f"SELECT matkul.id_matkul as id_matkul, matkul.nama_matkul as nama_matkul, user.nama as pengampu from matkul INNER JOIN user ON matkul.id_dosen=user.id_user WHERE user.no_induk={session['no_induk']}"
            cursor.execute(sql)
            result = cursor.fetchall()
            cursor.execute(sql2)
            result2 = cursor.fetchall()
        return render_template("view_kuis.html", data_pilih_matkul=result2, data_kuis=result)
    else:
        return redirect(url_for('login'))

# Create Kuis
@app.route("/create_kuis", methods=["POST"])
def create_kuis():
    if request.method == "POST":
        with connection.cursor() as cursor:
            kuis_ke = request.form["kuis_ke"]
            id_matkul = request.form["id_matkul"]
            sql = "INSERT INTO `kuis` (`kuis_ke`, `id_matkul`) VALUES (%s, %s)"
            data = kuis_ke, id_matkul
            cursor.execute(sql, data)
            # connection is not autocommit by default. So you must commit to save
            # your changes.
            connection.commit()
            cursor.close()
            return redirect(url_for('view_kuis'))

# Update Kuis
@app.route("/update_kuis", methods=["GET", "POST"])
def update_kuis():
    if request.method == "POST":
        with connection.cursor() as cursor:
            #ambil data
            id_kuis = request.form["id_kuis"]
            kuis_ke = request.form["kuis_ke"]
            id_matkul = request.form["id_matkul"]
            # Update a record
            sql = "UPDATE `kuis` SET kuis_ke= %s, id_matkul=%s WHERE id_kuis=%s"
            data = kuis_ke, id_matkul, id_kuis
            cursor.execute(sql, data)
            connection.commit()
            cursor.close()
        return redirect(url_for('view_kuis'))

# Delete Kuis
@app.route("/delete_kuis", methods=["POST"])
def delete_kuis():
    if request.method == "POST":
        with connection.cursor() as cursor:
            id_kuis = request.form["id_kuis"]
            # Delete record
            sql = "DELETE FROM `kuis` WHERE id_kuis=%s"
            cursor.execute(sql, id_kuis)
            # connection is not autocommit by default. So you must commit to save
            # your changes.
            connection.commit()
            cursor.close()
        return redirect(url_for('view_kuis'))
# END OF KUIS MANAGEMENT


# SOAL DAN JAWABAN MANAGEMENT
@app.route("/soal_dan_jawaban/<int:id_kuis>", methods=["GET", "POST"])
def view_soal(id_kuis):
    with connection.cursor() as cursor:
        sql = "SELECT soal.*, kuis.id_kuis FROM soal INNER JOIN kuis ON soal.id_kuis=kuis.id_kuis INNER JOIN matkul ON kuis.id_matkul=matkul.id_matkul INNER JOIN user ON matkul.id_dosen=user.id_user WHERE kuis.id_kuis=%s"
        sql2 = "SELECT kuis.kuis_ke, matkul.nama_matkul, user.nama FROM kuis INNER JOIN matkul ON kuis.id_matkul=matkul.id_matkul INNER JOIN user ON matkul.id_dosen=user.id_user WHERE id_kuis=%s"
        if(cursor.execute(sql, id_kuis) > 0):
            result = cursor.fetchall()
            cursor.execute(sql2, id_kuis)
            result2 = cursor.fetchone()
        else:
            cursor.execute(sql2, id_kuis)
            result2 = cursor.fetchone()
            return render_template('create_soal.html', data_kuis=result2, id_kuis=id_kuis)
        cursor.close()
        return render_template('view_soal.html', header=result2, data_soal=result, id_kuis=id_kuis)

# Create Soal
@app.route("/create_soal", methods=["POST"])
def create_soal():
    if request.method == "POST":
        with connection.cursor() as cursor:
            id_kuis = request.form["id_kuis"]
            soal    = request.form["soal"]
            jawaban_kunci = request.form["jawaban_kunci"]
            bobot_nilai = request.form["bobot_nilai"]
            sql = "INSERT INTO `soal` (`soal`, `jawaban_kunci`, `bobot_nilai`, `id_kuis`) VALUES (%s, %s, %s, %s)"
            data = soal, jawaban_kunci, bobot_nilai, id_kuis
            cursor.execute(sql, data)
            # connection is not autocommit by default. So you must commit to save
            # your changes.
            connection.commit()
            cursor.close()
            return redirect(url_for('view_soal', id_kuis=id_kuis))

# Update Soal
@app.route("/update_soal", methods=["POST"])
def update_soal():
    if request.method == "POST":
        with connection.cursor() as cursor:
            id_kuis = request.form["id_kuis"]
            id_soal = request.form["id_soal"]
            soal    = request.form["soal"]
            jawaban_kunci = request.form["jawaban_kunci"]
            bobot_nilai   = request.form["bobot_nilai"]
            sql = "UPDATE `soal` SET soal= %s, jawaban_kunci=%s, bobot_nilai=%s WHERE id_soal=%s"
            data = soal, jawaban_kunci, bobot_nilai, id_soal
            cursor.execute(sql, data)
            # connection is not autocommit by default. So you must commit to save
            # your changes.
            connection.commit()
            cursor.close()
        return redirect(url_for('view_soal', id_kuis=id_kuis))

# Delete soal
@app.route("/delete_soal", methods=["POST"])
def delete_soal():
    if request.method == "POST":
        with connection.cursor() as cursor:
            id_kuis = request.form["id_kuis"]
            id_soal = request.form["id_soal"]
            # Delete record
            sql = "DELETE FROM `soal` WHERE id_soal=%s"
            cursor.execute(sql, id_soal)
            # connection is not autocommit by default. So you must commit to save
            # your changes.
            connection.commit()
            cursor.close()
        return redirect(url_for('view_soal', id_kuis=id_kuis))
# END OF KUIS MANAGEMENT