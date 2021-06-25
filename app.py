#!/usr/bin/env python
from flask import Flask, Response, Request, request
from flask_sqlalchemy import SQLAlchemy
import os
import urllib.parse 
import json

# Configure Database URI: 
params = urllib.parse.quote_plus("DRIVER={SQL Server};SERVER=crud-testes.database.windows.net;DATABASE=listademercado;UID=gabriel.barbosa;PWD=Q0w9e8r7")

# initialization
app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecret'
app.config['SQLALCHEMY_DATABASE_URI'] = "mssql+pyodbc:///?odbc_connect=%s" % params
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

# extensions
db = SQLAlchemy(app)

class Produtos (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column (db.String(50))
    categoria = db.Column(db.String(50))

    def to_json(self):
        return {"id":self.id, "nome":self.nome, "categoria":self.categoria}


# Selecionar tudo
@app.route("/produtos", methods=["GET"])
def selecionar_produtos():
    produtos_classe = Produtos.query.all()
    produtos_json = [produtos.to_json() for produtos in produtos_classe] 

    return gera_response(200, "Produtos", produtos_json)

# Selecionar apenas um
@app.route("/produto/<id>", methods=["GET"])
def selecionar_produto(id):
    produto_classe = Produtos.query.filter_by(id=id).first()
    produto_json = produto_classe.to_json()

    return gera_response(200, "Produto", produto_json)

# Cadastrar
@app.route("/produto", methods=["POST"])
def cria_produto():
    body = request.get_json()

    #Try catch para gerar erro

    try:
        produto = Produtos(nome=body["nome"], categoria=body["categoria"])
        db.session.add(produto)
        db.session.commit()
        return gera_response(201, "Produto", produto.to_json(), "Criado com sucesso!")
    except Exception as e:
        print(e)
        return gera_response(400, "Produto", {}, "Erro ao cadastrar!")

# Atualizar
@app.route("/produto/<id>", methods=["PUT"])
def atualiza_produto(id):
    produto_classe = Produtos.query.filter_by(id=id).first()
    body = request.get_json()

    try:
        if('nome' in body):
            produto_classe.nome = body['nome']
        if('email' in body):
            produto_classe.categoria = body['categoria']

        db.session.add(produto_classe)
        db.session.commit()
        return gera_response(200, "Produto", produto_classe.to_json(), "Atualizado com sucesso!")
    except Exception as e:
        print(e)
        return gera_response(400, "Produto", {}, "Erro ao atualizar!")

# Deletar
@app.route("/produto/<id>", methods=["DELETE"])
def deleta_produto(id):
    produto_classe = Produtos.query.filter_by(id=id).first()

    try:
        db.session.delete(produto_classe)
        db.session.commit()
        return gera_response(200, "Produto", produto_classe.to_json(), "Deletado com sucesso!")
    except Exception as e:
        print('Erro',e)
        return gera_response(400, "Produto", {}, "Erro ao Deletar!")


#metodo criado para chamar a response
def gera_response(status, nome_do_conteudo, conteudo, mensagem=False):
    body = {}
    body[nome_do_conteudo] = conteudo

    if(mensagem):
        body["mensagem"] = mensagem

    return Response(json.dumps(body), status=status, mimetype="application/json")


#usado para rodar o código
app.run()