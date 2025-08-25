# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, redirect, send_from_directory
from flask_mail import Mail, Message
from datetime import datetime
import pytz
import os
import csv

app = Flask(__name__)

# Configuración correo
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'soporte@cloudsoftware.com.co'
app.config['MAIL_PASSWORD'] = 'zuig guvt xgzj rwlq'
app.config['MAIL_DEFAULT_SENDER'] = 'soporte@cloudsoftware.com.co'

mail = Mail(app)

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

CSV_FILE = 'casos.csv'

def now_colombia():
    tz = pytz.timezone('America/Bogota')
    return datetime.now(tz)

@app.route('/', methods=['GET', 'POST'])
def soporte():
    if request.method == 'POST':
        nombre = request.form['nombre']
        correo = request.form['correo']
        telefono = request.form['telefono']
        empresa = request.form['empresa']
        tipo_problema = request.form['tipo_problema']
        descripcion = request.form['descripcion']
        fecha_reporte = now_colombia().strftime("%Y-%m-%d %H:%M:%S")
        estado = 'pendiente'

        archivo = request.files.get('archivo')
        archivo_nombre = ''
        if archivo and archivo.filename:
            archivo_nombre = f"{datetime.now().timestamp()}_{archivo.filename}"
            archivo_path = os.path.join(UPLOAD_FOLDER, archivo_nombre)
            archivo.save(archivo_path)
        else:
            archivo_path = None

        with open(CSV_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([fecha_reporte, nombre, correo, telefono, empresa, tipo_problema, descripcion, archivo_nombre, estado])

        # Enviar correo a soporte
        msg = Message('Nuevo caso reportado', recipients=['soporte@cloudsoftware.com.co'])
        msg.body = f"""
Nuevo caso de soporte:

Nombre: {nombre}
Correo: {correo}
Teléfono: {telefono}
Empresa: {empresa}
Tipo: {tipo_problema}
Descripción: {descripcion}
"""
        if archivo_path:
            msg.attach(archivo.filename, archivo.mimetype, open(archivo_path, 'rb').read())
        mail.send(msg)

        return redirect('/gracias')

    empresas = ['', 'Adela', 'Acomedios', 'Aldas', 'Asoredes', 'Big Media', 'Cafam', 'Century', 'CNM']
    tipos_problema = ['Caso', 'Solicitud', 'Mejora']
    return render_template('formulario.html', empresas=empresas, tipos_problema=tipos_problema)

@app.route('/gracias')
def gracias():
    return render_template('gracias.html')

# app.py
from flask import Flask, render_template, request, redirect, send_from_directory
from datetime import datetime
import pytz
import os
import csv

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
CSV_FILE = 'casos.csv'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

clientes = ['Adela', 'Acomedios', 'Aldas', 'Asoredes']
tipos_problema = ['Caso', 'Solicitud', 'Mejora']

# Función para obtener fecha actual en Colombia
def now_colombia():
    tz = pytz.timezone('America/Bogota')
    return datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

@app.route('/', methods=['GET', 'POST'])
def formulario():
    if request.method == 'POST':
        nombre = request.form['nombre']
        correo = request.form['correo']
        telefono = request.form['telefono']
        empresa = request.form['empresa']
        tipo_problema = request.form['tipo_problema']
        descripcion = request.form['descripcion']
        estado = 'pendiente'
        fecha_reporte = now_colombia()

        archivo = request.files.get('archivo')
        archivo_nombre = ''
        if archivo and archivo.filename:
            archivo_nombre = f"{datetime.now().timestamp()}_{archivo.filename}"
            archivo.save(os.path.join(UPLOAD_FOLDER, archivo_nombre))

        with open(CSV_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([fecha_reporte, nombre, correo, telefono, empresa, tipo_problema, descripcion, archivo_nombre, estado])

        return redirect('/gracias')

    return render_template('formulario.html', clientes=clientes, tipos_problema=tipos_problema)

@app.route('/gracias')
def gracias():
    return render_template('gracias.html')

@app.route('/admin')
def admin():
    casos = []
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            for i, row in enumerate(reader):
                casos.append({'id': i, 'fecha': row[0], 'nombre': row[1], 'correo': row[2], 'telefono': row[3],
                              'empresa': row[4], 'tipo': row[5], 'descripcion': row[6],
                              'archivo': row[7], 'estado': row[8]})
    return render_template('admin.html', casos=casos)

@app.route('/static/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/vaciar', methods=['GET', 'POST'])
def vaciar():
    if request.method == 'POST':
        password = request.form['password']
        if password == '940402':
            open(CSV_FILE, 'w').close()
            return "Base de datos vaciada."
        return "Contraseña incorrecta."
    return '''<form method="post">Contraseña: <input type="password" name="password"> <input type="submit"></form>'''

if __name__ == '__main__':
    app.run(debug=True)
