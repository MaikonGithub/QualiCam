#!/usr/bin/env python3
"""
Servidor QualiCam - Sistema de Controle de Estoque de Marmoraria
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os
from datetime import datetime
import logging

# Configuração do logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Permite requisições de qualquer origem

# Configuração do banco de dados
DATABASE = 'qualicam.db'

def init_database():
    """Inicializa o banco de dados com as tabelas necessárias"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Tabela de chapas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chapas (
            id TEXT PRIMARY KEY,
            nome_material TEXT NOT NULL,
            fornecedor TEXT NOT NULL,
            tamanho REAL NOT NULL,
            preco REAL NOT NULL,
            localizacao TEXT NOT NULL,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabela de retalhos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS retalhos (
            id TEXT PRIMARY KEY,
            nome_material TEXT NOT NULL,
            fornecedor TEXT NOT NULL,
            tamanho REAL NOT NULL,
            preco REAL NOT NULL,
            localizacao TEXT NOT NULL,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    logger.info("Banco de dados inicializado com sucesso")

def get_db_connection():
    """Cria uma conexão com o banco de dados"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint para verificar se o servidor está funcionando"""
    return jsonify({"status": "ok", "message": "Servidor QualiCam funcionando"}), 200

@app.route('/chapas/<chapa_id>', methods=['GET'])
def get_chapa(chapa_id):
    """Busca uma chapa pelo ID"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM chapas WHERE id = ?', (chapa_id,))
        chapa = cursor.fetchone()
        
        conn.close()
        
        if chapa:
            return jsonify({
                "id": chapa["id"],
                "nomeMaterial": chapa["nome_material"],
                "fornecedor": chapa["fornecedor"],
                "tamanho": chapa["tamanho"],
                "preco": chapa["preco"],
                "localizacao": chapa["localizacao"]
            }), 200
        else:
            return jsonify({"message": "Chapa não encontrada"}), 404
            
    except Exception as e:
        logger.error(f"Erro ao buscar chapa {chapa_id}: {str(e)}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@app.route('/chapas', methods=['POST'])
def create_chapa():
    """Cria uma nova chapa"""
    try:
        data = request.get_json()
        
        # Validação dos dados
        required_fields = ['id', 'nomeMaterial', 'fornecedor', 'tamanho', 'preco', 'localizacao']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Campo obrigatório: {field}"}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verifica se a chapa já existe
        cursor.execute('SELECT id FROM chapas WHERE id = ?', (data['id'],))
        if cursor.fetchone():
            conn.close()
            return jsonify({"error": "Chapa já existe"}), 409
        
        # Insere a nova chapa
        cursor.execute('''
            INSERT INTO chapas (id, nome_material, fornecedor, tamanho, preco, localizacao)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            data['id'],
            data['nomeMaterial'],
            data['fornecedor'],
            data['tamanho'],
            data['preco'],
            data['localizacao']
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Chapa {data['id']} criada com sucesso")
        return jsonify({"message": "Chapa criada com sucesso"}), 201
        
    except Exception as e:
        logger.error(f"Erro ao criar chapa: {str(e)}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@app.route('/chapas/<chapa_id>', methods=['PUT'])
def update_chapa(chapa_id):
    """Atualiza uma chapa existente"""
    try:
        data = request.get_json()
        
        # Validação dos dados
        required_fields = ['nomeMaterial', 'fornecedor', 'tamanho', 'preco', 'localizacao']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Campo obrigatório: {field}"}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verifica se a chapa existe
        cursor.execute('SELECT id FROM chapas WHERE id = ?', (chapa_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({"error": "Chapa não encontrada"}), 404
        
        # Atualiza a chapa
        cursor.execute('''
            UPDATE chapas 
            SET nome_material = ?, fornecedor = ?, tamanho = ?, preco = ?, 
                localizacao = ?, data_atualizacao = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (
            data['nomeMaterial'],
            data['fornecedor'],
            data['tamanho'],
            data['preco'],
            data['localizacao'],
            chapa_id
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Chapa {chapa_id} atualizada com sucesso")
        return jsonify({"message": "Chapa atualizada com sucesso"}), 200
        
    except Exception as e:
        logger.error(f"Erro ao atualizar chapa {chapa_id}: {str(e)}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@app.route('/chapas/<chapa_id>', methods=['DELETE'])
def delete_chapa(chapa_id):
    """Remove uma chapa"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verifica se a chapa existe
        cursor.execute('SELECT id FROM chapas WHERE id = ?', (chapa_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({"error": "Chapa não encontrada"}), 404
        
        # Remove a chapa
        cursor.execute('DELETE FROM chapas WHERE id = ?', (chapa_id,))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Chapa {chapa_id} removida com sucesso")
        return jsonify({"message": "Chapa removida com sucesso"}), 200
        
    except Exception as e:
        logger.error(f"Erro ao remover chapa {chapa_id}: {str(e)}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@app.route('/retalhos', methods=['POST'])
def create_retalho():
    """Cria um novo retalho"""
    try:
        data = request.get_json()
        
        # Validação dos dados
        required_fields = ['id', 'nomeMaterial', 'fornecedor', 'tamanho', 'preco', 'localizacao']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Campo obrigatório: {field}"}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verifica se o retalho já existe
        cursor.execute('SELECT id FROM retalhos WHERE id = ?', (data['id'],))
        if cursor.fetchone():
            conn.close()
            return jsonify({"error": "Retalho já existe"}), 409
        
        # Insere o novo retalho
        cursor.execute('''
            INSERT INTO retalhos (id, nome_material, fornecedor, tamanho, preco, localizacao)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            data['id'],
            data['nomeMaterial'],
            data['fornecedor'],
            data['tamanho'],
            data['preco'],
            data['localizacao']
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Retalho {data['id']} criado com sucesso")
        return jsonify({"message": "Retalho criado com sucesso"}), 201
        
    except Exception as e:
        logger.error(f"Erro ao criar retalho: {str(e)}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@app.route('/chapas', methods=['GET'])
def list_chapas():
    """Lista todas as chapas"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM chapas ORDER BY data_criacao DESC')
        chapas = cursor.fetchall()
        
        conn.close()
        
        result = []
        for chapa in chapas:
            result.append({
                "id": chapa["id"],
                "nomeMaterial": chapa["nome_material"],
                "fornecedor": chapa["fornecedor"],
                "tamanho": chapa["tamanho"],
                "preco": chapa["preco"],
                "localizacao": chapa["localizacao"],
                "dataCriacao": chapa["data_criacao"]
            })
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Erro ao listar chapas: {str(e)}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@app.route('/retalhos', methods=['GET'])
def list_retalhos():
    """Lista todos os retalhos"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM retalhos ORDER BY data_criacao DESC')
        retalhos = cursor.fetchall()
        
        conn.close()
        
        result = []
        for retalho in retalhos:
            result.append({
                "id": retalho["id"],
                "nomeMaterial": retalho["nome_material"],
                "fornecedor": retalho["fornecedor"],
                "tamanho": retalho["tamanho"],
                "preco": retalho["preco"],
                "localizacao": retalho["localizacao"],
                "dataCriacao": retalho["data_criacao"]
            })
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Erro ao listar retalhos: {str(e)}")
        return jsonify({"error": "Erro interno do servidor"}), 500

if __name__ == '__main__':
    # Inicializa o banco de dados
    init_database()
    
    # Configurações do servidor
    host = '0.0.0.0'  # Permite acesso de qualquer IP na rede
    port = 8000
    debug = True
    
    logger.info(f"Iniciando servidor QualiCam em {host}:{port}")
    logger.info("Para acessar o servidor, use o IP da máquina na rede local")
    
    app.run(host=host, port=port, debug=debug)

