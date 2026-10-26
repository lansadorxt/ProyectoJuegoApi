from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_required
from extensions import db

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/juegos'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'una_clave_muy_secreta_y_dificil'

# Inicialización vinculada a la app sin duplicación
db.init_app(app)

# Configuración de Flask-Login
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

import controllers

# --- REGISTRO DE BLUEPRINTS ---
from auth import auth as auth_blueprint
app.register_blueprint(auth_blueprint, url_prefix='/auth')

from api.routes import api_bp
app.register_blueprint(api_bp, url_prefix='/api')

with app.app_context():
    db.create_all()

# --- RUTAS PROTEGIDAS (WEB) ---
@app.route('/')
@app.route('/juegos')
@login_required
def juegos():
    lista_juegos = controllers.obtener_juegos()
    return render_template('juegos.html', juegos=lista_juegos)

@app.route('/agregar_juego')
@login_required
def formulario_agregar_juego():
    return render_template('agregar_juego.html')

@app.route('/guardar_juego', methods=['POST'])
@login_required
def guardar_juego():
    nombre = request.form['nombre']
    descripcion = request.form['descripcion']
    precio = request.form['precio']
    controllers.insertar_juego(nombre, descripcion, precio)
    return redirect('/juegos')

@app.route('/eliminar_juego', methods=['POST'])
@login_required
def eliminar_juego():
    id = request.form['id']
    controllers.eliminar_juego(id)
    return redirect('/juegos')

@app.route('/formulario_editar_juego/<int:id>')
@login_required
def editar_juego(id):
    juego = controllers.obtener_juego_por_id(id)
    return render_template('editar_juego.html', juego=juego)

@app.route('/actualizar_juego', methods=['POST'])
@login_required
def actualizar_juego():
    id = request.form['id']
    nombre = request.form['nombre']
    descripcion = request.form['descripcion']
    precio = request.form['precio']
    controllers.actualizar_juego(id, nombre, descripcion, precio)
    return redirect('/juegos')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)