from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from wtforms import StringField, DateField, FloatField, SelectField
from wtforms.validators import DataRequired
from models.despesas import Despesa
from models.ganhos import Ganho
from models.user import User
import secrets

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = secrets.token_hex(16)


login_manager = LoginManager(app)
login_manager.login_view = 'login'

class DespesaForm(FlaskForm):
    descricao = StringField('Descrição', validators=[DataRequired()])
    categoria = StringField('Categoria', validators=[DataRequired()])
    data = DateField('Data', format='%Y-%m-%d', validators=[DataRequired()])
    valor = FloatField('Valor', validators=[DataRequired()])
    status = SelectField('Status', choices=[('pendente', 'Pendente'), ('paga', 'Paga')])

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            flash('Login bem-sucedido.', 'success')
            return redirect(url_for('index'))
        else:
            flash('Credenciais inválidas. Tente novamente.', 'error')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout bem-sucedido.', 'success')
    return redirect(url_for('login'))


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        descricao = request.form['descricao']
        categoria = request.form['categoria']
        data_string = request.form['data']
        data_formatada = datetime.strptime(data_string, '%Y-%m-%d')
        data_br = data_formatada.strftime('%d/%m/%Y')
        valor = float(request.form['valor'].replace(',', '.'))
        valor_formatado = "{:.3f}".format(valor)
        status = request.form['status']

        with app.app_context():
            nova_despesa = Despesa(descricao=descricao, categoria=categoria,
                                   data=data_br, valor=valor_formatado, status=status)
            db.session.add(nova_despesa)
            db.session.commit()

    with app.app_context():
        despesas = Despesa.query.all()

    return render_template('index.html', despesas=despesas)


@app.route('/lista_despesas')
def lista_despesas():
    with app.app_context():
        despesas = Despesa.query.all()

    return render_template('lista_despesas.html', despesas=despesas)


@app.route('/editar_despesa/<int:id>', methods=['GET', 'POST'])
def editar_despesa(id):
    despesa = Despesa.query.get(id)

    if request.method == 'POST':
        descricao = request.form['descricao']
        categoria = request.form['categoria']
        data_string = request.form['data']
        data_formatada = datetime.strptime(data_string, '%Y-%m-%d')
        data_br = data_formatada.strftime('%d/%m/%Y')
        valor = float(request.form['valor'].replace(',', '.'))
        valor_formatado = "{:.2f}".format(valor)
        status = request.form['status']

        despesa.descricao = descricao
        despesa.categoria = categoria
        despesa.data = data_br
        despesa.valor = valor_formatado
        despesa.status = status

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash('Erro ao atualizar a despesa. Por favor, tente novamente.', 'error')
            return redirect(url_for('lista_despesas'))

        return redirect(url_for('lista_despesas'))

    return render_template('editar_despesa.html', despesa=despesa)


@app.route('/deletar_despesa/<int:id>', methods=['POST'])
def deletar_despesa(id):
    despesa = Despesa.query.get(id)

    if despesa:
        try:
            db.session.delete(despesa)
            db.session.commit()
            flash('Despesa excluída com sucesso.', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Erro ao excluir a despesa. Por favor, tente novamente.', 'error')
    else:
        flash('Despesa não encontrada.', 'error')

    return redirect(url_for('lista_despesas'))


@app.route('/editar_ganhos/<int:id>', methods=['GET', 'POST'])
def editar_ganhos(id):
    ganho = Ganho.query.get(id)
    
    if request.method == 'POST':
        descricao = request.form['descricao_ganho']
        categoria = request.form['categoria_ganho']
        data_string = request.form['data_ganho']
        data_formatada = datetime.strptime(data_string, '%Y-%m-%d')
        data_br = data_formatada.strftime('%d/%m/%Y')
        valor = float(request.form['valor_ganho'].replace(',', '.'))
        valor_formatado = "{:.2f}".format(valor)
        responsavel = request.form['responsavel_ganho']
        
        ganho.descricao = descricao
        ganho.categoria = categoria
        ganho.data = data_br
        ganho.valor = valor_formatado
        ganho.responsavel = responsavel
    
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash('Erro ao atualizar a ganho. Por favor, tente novamente.', 'error')
            return redirect(url_for('lista_ganhos'))
    
    return render_template('editar_ganhos.html', ganho=ganho)

@app.route('/deletar_ganhos/<int:id>', methods=['POST'])
def deletar_ganhos(id):
    ganho = Ganho.query.get(id)

    if ganho:
        try:
            db.session.delete(ganho)
            db.session.commit()
            flash('ganho excluída com sucesso.', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Erro ao excluir a ganho. Por favor, tente novamente.', 'error')
    else:
        flash('ganho não encontrada.', 'error')

    return redirect(url_for('listar_ganhos'))


@app.route('/ganhos', methods=['GET', 'POST'])
def adicionar_ganhos():
    if request.method == 'POST':
        descricao = request.form['descricao_ganho']
        categoria = request.form['categoria_ganho']
        data_string = request.form['data_ganho']
        data_formatada = datetime.strptime(data_string, '%Y-%m-%d')
        data_br = data_formatada.strftime('%d/%m/%Y')
        valor = float(request.form['valor_ganho'].replace(',', '.'))
        valor_formatado = "{:.2f}".format(valor)
        responsavel = request.form['responsavel_ganho']
        with app.app_context():
            novo_ganho = Ganho(descricao=descricao, categoria=categoria,
                               data=data_br, valor=valor_formatado, responsavel=responsavel)
            db.session.add(novo_ganho)
            db.session.commit()

    return render_template('ganhos.html', ganhos=Ganho.query.all())

@app.route('/lista_ganhos')
def listar_ganhos():
    with app.app_context():
        ganhos = Ganho.query.all()

    return render_template('lista_ganhos.html', ganhos=ganhos)



if __name__ == '__main__':
    from sql_alchemy import db
    db.init_app(app)
    app.run(debug=True)
