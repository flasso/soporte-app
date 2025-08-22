from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from flask_mail import Mail, Message
import os
from datetime import datetime
import pytz

app = Flask(__name__)

# Configuración correo
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'soporte@cloudsoftware.com.co'
app.config['MAIL_PASSWORD'] = 'zuig guvt xgzj rwlq'
app.config['MAIL_DEFAULT_SENDER'] = 'soporte@cloudsoftware.com.co'
mail = Mail(app)

UPLOAD_FOLDER = 'casos'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def now_colombia():
    return datetime.now(pytz.timezone('America/Bogota'))

@app.route('/', methods=['GET', 'POST'])
def soporte():
    empresas = ['Adela', 'Acomedios', 'Media Plus', 'TBWA']
    tipos_problema = ['Caso', 'Solicitud', 'Mejora']
    if request.method == 'POST':
        nombre = request.form['nombre']
        correo = request.form['correo']
        telefono = request.form['telefono']
        empresa = request.form['empresa']
        tipo_problema = request.form['tipo_problema']
        descripcion = request.form['descripcion']
        fecha = now_colombia().strftime('%Y-%m-%d_%H-%M-%S')

        # Guardar archivo si lo hay
        archivo = request.files.get('archivo')
        archivo_nombre = None
        if archivo and archivo.filename:
            archivo_nombre = f"{fecha}_{archivo.filename}"
            archivo.save(os.path.join(UPLOAD_FOLDER, archivo_nombre))

        # Guardar en archivo .txt
        txt_path = os.path.join(UPLOAD_FOLDER, f"{fecha}_{nombre}.txt")
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(f"Fecha: {fecha}\nNombre: {nombre}\nCorreo: {correo}\nTeléfono: {telefono}\nEmpresa: {empresa}\nTipo: {tipo_problema}\nDescripción:\n{descripcion}\nAdjunto: {archivo_nombre}\n")

        # Enviar correo a soporte
        msg = Message('Nuevo caso reportado', recipients=[app.config['MAIL_USERNAME']])
        msg.body = f"""Nuevo caso:
Nombre: {nombre}
Correo: {correo}
Teléfono: {telefono}
Empresa: {empresa}
Tipo: {tipo_problema}
Descripción: {descripcion}
"""
        if archivo_nombre:
            with app.open_resource(os.path.join(UPLOAD_FOLDER, archivo_nombre)) as adj:
                msg.attach(archivo_nombre, archivo.content_type, adj.read())

        mail.send(msg)
        return redirect('/gracias')
    return render_template('formulario.html', empresas=empresas, tipos_problema=tipos_problema)

@app.route('/gracias')
def gracias():
    return render_template('gracias.html')

@app.route('/admin')
def admin():
    archivos = sorted(os.listdir(UPLOAD_FOLDER))
    registros = [f for f in archivos if f.endswith('.txt')]
    return render_template('admin.html', registros=registros)

@app.route('/ver/<filename>')
def ver(filename):
    path = os.path.join(UPLOAD_FOLDER, filename)
    with open(path, 'r', encoding='utf-8') as f:
        contenido = f.read()
    return render_template('responder.html', contenido=contenido, archivo=filename)

@app.route('/adjunto/<filename>')
def adjunto(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/vaciar', methods=['GET', 'POST'])
def vaciar():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == '940402':
            for f in os.listdir(UPLOAD_FOLDER):
                os.remove(os.path.join(UPLOAD_FOLDER, f))
            return "Base de datos vaciada."
        return "Contraseña incorrecta."
    return '''
    <form method="post">
        <input type="password" name="password" placeholder="Contraseña">
        <input type="submit" value="Vaciar">
    </form>
    '''
