#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Servidor API para Controle de Estoque - Marmoraria
Arquitetura Cliente-Servidor com Flask e SQLite
"""

import sqlite3
import os
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from database import DatabaseManager

app = Flask(__name__)
CORS(app)  # Permite requisições de outros domínios (necessário para o cliente)

# Inicializar gerenciador do banco de dados
db_manager = DatabaseManager()


@app.route('/chapas', methods=['GET'])
def listar_chapas():
    """Retorna lista de todas as chapas com status 'Disponível'"""
    try:
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id_chapa, nome_material, fornecedor, preco_compra_m2,
                   area_liquida_inicial, area_disponivel, localizacao, status, data_entrada
            FROM chapas 
            WHERE status = 'Disponível'
            ORDER BY data_entrada DESC
        ''')
        
        chapas = []
        for row in cursor.fetchall():
            chapa = {
                'id_chapa': row['id_chapa'],
                'nome_material': row['nome_material'],
                'fornecedor': row['fornecedor'],
                'preco_compra_m2': row['preco_compra_m2'],
                'area_liquida_inicial': row['area_liquida_inicial'],
                'area_disponivel': row['area_disponivel'],
                'localizacao': row['localizacao'],
                'status': row['status'],
                'data_entrada': row['data_entrada']
            }
            chapas.append(chapa)
        
        conn.close()
        return jsonify({'success': True, 'chapas': chapas})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/chapas/adicionar', methods=['POST'])
def adicionar_chapa():
    """Adiciona nova chapa ao estoque"""
    try:
        data = request.get_json()
        
        # Validar dados obrigatórios
        campos_obrigatorios = ['id_chapa', 'nome_material', 'fornecedor', 'preco_compra_m2', 'area_liquida_inicial', 'localizacao']
        for campo in campos_obrigatorios:
            if campo not in data or not data[campo]:
                return jsonify({'success': False, 'error': f'Campo {campo} é obrigatório'}), 400
        
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            # Verificar se ID já existe
            cursor.execute("SELECT id_chapa FROM chapas WHERE id_chapa = ?", (data['id_chapa'],))
            if cursor.fetchone():
                return jsonify({'success': False, 'error': f'ID {data["id_chapa"]} já existe'}), 400
            
            # Inserir chapa
            cursor.execute('''
                INSERT INTO chapas (id_chapa, nome_material, fornecedor, preco_compra_m2, 
                                  area_liquida_inicial, area_disponivel, localizacao, status, data_entrada)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'Disponível', datetime('now'))
            ''', (data['id_chapa'], data['nome_material'], data['fornecedor'], 
                  data['preco_compra_m2'], data['area_liquida_inicial'], 
                  data['area_liquida_inicial'], data['localizacao']))
            
            conn.commit()
        
        return jsonify({'success': True, 'id_chapa': data['id_chapa']})
        
    except Exception as e:
        print(f"ERRO ao adicionar chapa: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/chapas/update-area', methods=['POST'])
def atualizar_area_chapa():
    """Atualiza área disponível e localização de uma chapa"""
    try:
        data = request.get_json()
        
        # Validar dados obrigatórios
        if 'id_chapa' not in data:
            return jsonify({'success': False, 'error': 'ID da chapa é obrigatório'}), 400
        
        id_chapa = data['id_chapa']
        
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        # Verificar se chapa existe
        cursor.execute("SELECT id_chapa, area_disponivel, localizacao FROM chapas WHERE id_chapa = ?", (id_chapa,))
        chapa_existente = cursor.fetchone()
        
        if not chapa_existente:
            return jsonify({'success': False, 'error': f'Chapa {id_chapa} não encontrada'}), 404
        
        # Preparar dados para atualização
        updates = []
        params = []
        
        # Atualizar área disponível se fornecida
        if 'nova_area_disponivel' in data and data['nova_area_disponivel'] is not None:
            nova_area = float(data['nova_area_disponivel'])
            if nova_area < 0:
                return jsonify({'success': False, 'error': 'Área não pode ser negativa'}), 400
            updates.append("area_disponivel = ?")
            params.append(nova_area)
        
        # Atualizar localização se fornecida
        if 'nova_localizacao' in data and data['nova_localizacao'].strip():
            updates.append("localizacao = ?")
            params.append(data['nova_localizacao'].strip())
        
        # Atualizar OS associada se fornecida
        if 'os_associada' in data and data['os_associada'].strip():
            updates.append("os_associada = ?")
            params.append(data['os_associada'].strip())
        
        # Se não há nada para atualizar
        if not updates:
            return jsonify({'success': False, 'error': 'Nenhum campo para atualizar foi fornecido'}), 400
        
        # Adicionar ID da chapa aos parâmetros
        params.append(id_chapa)
        
        # Executar atualização
        query = f"UPDATE chapas SET {', '.join(updates)} WHERE id_chapa = ?"
        cursor.execute(query, params)
        
        # Verificar se alguma linha foi afetada
        if cursor.rowcount == 0:
            return jsonify({'success': False, 'error': 'Nenhuma chapa foi atualizada'}), 400
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True, 
            'message': f'Chapa {id_chapa} atualizada com sucesso',
            'id_chapa': id_chapa
        })
        
    except ValueError as e:
        return jsonify({'success': False, 'error': f'Dados inválidos: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/chapas/transformar-retalho', methods=['POST'])
def transformar_em_retalho():
    """Transforma uma chapa em retalho"""
    try:
        data = request.get_json()
        
        # Validar dados obrigatórios
        if 'id_chapa' not in data:
            return jsonify({'success': False, 'error': 'ID da chapa é obrigatório'}), 400
        
        id_chapa = data['id_chapa']
        
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        # Verificar se chapa existe
        cursor.execute("""
            SELECT id_chapa, nome_material, fornecedor, area_disponivel, localizacao, status 
            FROM chapas 
            WHERE id_chapa = ?
        """, (id_chapa,))
        
        chapa = cursor.fetchone()
        
        if not chapa:
            return jsonify({'success': False, 'error': f'Chapa {id_chapa} não encontrada'}), 404
        
        # Verificar se já é retalho
        if chapa['status'] == 'Retalho':
            return jsonify({'success': False, 'error': f'Chapa {id_chapa} já é um retalho'}), 400
        
        # Remover da tabela chapas e inserir na tabela retalhos
        cursor.execute("""
            DELETE FROM chapas 
            WHERE id_chapa = ?
        """, (id_chapa,))
        
        # Inserir na tabela retalhos
        cursor.execute("""
            INSERT INTO retalhos (id_chapa_original, nome_material, fornecedor, area_retalho, localizacao, data_transformacao)
            VALUES (?, ?, ?, ?, ?, datetime('now'))
        """, (id_chapa, chapa['nome_material'], chapa['fornecedor'], chapa['area_disponivel'], chapa['localizacao']))
        
        # Registrar movimentação
        cursor.execute("""
            INSERT INTO movimentacoes (id_chapa, tipo_movimentacao, quantidade_m2, data_movimentacao)
            VALUES (?, 'TRANSFORMAR_RETALHO', ?, datetime('now'))
        """, (id_chapa, chapa['area_disponivel']))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'Chapa {id_chapa} transformada em retalho com sucesso',
            'id_chapa': id_chapa,
            'area_retalho': chapa['area_disponivel']
        })
        
    except Exception as e:
        print(f"ERRO ao transformar chapa em retalho: {str(e)}")
        return jsonify({'success': False, 'error': f'Erro interno: {str(e)}'}), 500

@app.route('/chapas/metragem-total', methods=['GET'])
def obter_metragem_total():
    """Retorna metragem total por material"""
    try:
        # Usar o DatabaseManager para obter dados completos
        materiais = db_manager.get_material_summary()
        
        return jsonify({'success': True, 'materiais': materiais})
    
    except Exception as e:
        print(f"ERRO ao obter metragem total: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint para verificar se o servidor está funcionando"""
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})

# =============================================================================
# ROTAS ESPECÍFICAS PARA O APP QUALICAM
# =============================================================================

@app.route('/app/health', methods=['GET'])
def app_health_check():
    """Endpoint específico do app QualiCam para verificar conectividade"""
    return jsonify({"status": "ok", "message": "Servidor QualiCam funcionando"}), 200

@app.route('/app/chapas/<chapa_id>', methods=['GET'])
def app_get_chapa(chapa_id):
    """Busca uma chapa pelo ID - Rota específica do app QualiCam"""
    try:
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM chapas WHERE id_chapa = ?', (chapa_id,))
        chapa = cursor.fetchone()
        
        conn.close()
        
        if chapa:
            return jsonify({
                "id": chapa["id_chapa"],
                "nomeMaterial": chapa["nome_material"],
                "fornecedor": chapa["fornecedor"],
                "tamanho": chapa["area_disponivel"],
                "preco": chapa["preco_compra_m2"],
                "localizacao": chapa["localizacao"]
            }), 200
        else:
            return jsonify({"message": "Chapa não encontrada"}), 404
            
    except Exception as e:
        return jsonify({"error": "Erro interno do servidor"}), 500

@app.route('/app/chapas', methods=['POST'])
def app_create_chapa():
    """Cria uma nova chapa - Rota específica do app QualiCam"""
    try:
        data = request.get_json()
        
        # Validação dos dados
        required_fields = ['id', 'nomeMaterial', 'fornecedor', 'tamanho', 'preco', 'localizacao']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Campo obrigatório: {field}"}), 400
        
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        # Verifica se a chapa já existe
        cursor.execute('SELECT id_chapa FROM chapas WHERE id_chapa = ?', (data['id'],))
        if cursor.fetchone():
            conn.close()
            return jsonify({"error": "Chapa já existe"}), 409
        
        # Insere a nova chapa
        cursor.execute('''
            INSERT INTO chapas (id_chapa, nome_material, fornecedor, preco_compra_m2, 
                              area_liquida_inicial, area_disponivel, localizacao, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'Disponível')
        ''', (
            data['id'],
            data['nomeMaterial'],
            data['fornecedor'],
            data['preco'],
            data['tamanho'],
            data['tamanho'],
            data['localizacao']
        ))
        
        # Registrar movimentação de entrada
        cursor.execute('''
            INSERT INTO movimentacoes (id_chapa, tipo_movimentacao, quantidade_m2)
            VALUES (?, 'ENTRADA', ?)
        ''', (data['id'], data['tamanho']))
        
        conn.commit()
        conn.close()
        
        return jsonify({"message": "Chapa criada com sucesso"}), 201
        
    except Exception as e:
        return jsonify({"error": "Erro interno do servidor"}), 500

@app.route('/app/chapas/<chapa_id>', methods=['PUT'])
def app_update_chapa(chapa_id):
    """Atualiza uma chapa existente - Rota específica do app QualiCam"""
    try:
        data = request.get_json()
        
        # Validação dos dados
        required_fields = ['nomeMaterial', 'fornecedor', 'tamanho', 'preco', 'localizacao']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Campo obrigatório: {field}"}), 400
        
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        # Verifica se a chapa existe
        cursor.execute('SELECT id_chapa FROM chapas WHERE id_chapa = ?', (chapa_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({"error": "Chapa não encontrada"}), 404
        
        # Atualiza a chapa
        cursor.execute('''
            UPDATE chapas 
            SET nome_material = ?, fornecedor = ?, preco_compra_m2 = ?, 
                area_disponivel = ?, localizacao = ?
            WHERE id_chapa = ?
        ''', (
            data['nomeMaterial'],
            data['fornecedor'],
            data['preco'],
            data['tamanho'],
            data['localizacao'],
            chapa_id
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({"message": "Chapa atualizada com sucesso"}), 200
        
    except Exception as e:
        return jsonify({"error": "Erro interno do servidor"}), 500

@app.route('/app/chapas/<chapa_id>', methods=['DELETE'])
def app_delete_chapa(chapa_id):
    """Remove uma chapa - Rota específica do app QualiCam"""
    try:
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        # Verifica se a chapa existe
        cursor.execute('SELECT id_chapa FROM chapas WHERE id_chapa = ?', (chapa_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({"error": "Chapa não encontrada"}), 404
        
        # Remove a chapa
        cursor.execute('DELETE FROM chapas WHERE id_chapa = ?', (chapa_id,))
        
        conn.commit()
        conn.close()
        
        return jsonify({"message": "Chapa removida com sucesso"}), 200
        
    except Exception as e:
        return jsonify({"error": "Erro interno do servidor"}), 500

@app.route('/app/retalhos', methods=['POST'])
def app_create_retalho():
    """Cria um novo retalho - Rota específica do app QualiCam"""
    try:
        data = request.get_json()
        
        # Validação dos dados
        required_fields = ['id', 'nomeMaterial', 'fornecedor', 'tamanho', 'preco', 'localizacao']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Campo obrigatório: {field}"}), 400
        
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        # Verifica se o retalho já existe
        cursor.execute('SELECT id_retalho FROM retalhos WHERE id_chapa_original = ?', (data['id'],))
        if cursor.fetchone():
            conn.close()
            return jsonify({"error": "Retalho já existe"}), 409
        
        # Insere o novo retalho
        cursor.execute('''
            INSERT INTO retalhos (id_chapa_original, nome_material, fornecedor, area_retalho, localizacao)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            data['id'],
            data['nomeMaterial'],
            data['fornecedor'],
            data['tamanho'],
            data['localizacao']
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({"message": "Retalho criado com sucesso"}), 201
        
    except Exception as e:
        return jsonify({"error": "Erro interno do servidor"}), 500

@app.route('/app/chapas', methods=['GET'])
def app_list_chapas():
    """Lista todas as chapas - Rota específica do app QualiCam"""
    try:
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM chapas ORDER BY data_entrada DESC')
        chapas = cursor.fetchall()
        
        conn.close()
        
        result = []
        for chapa in chapas:
            result.append({
                "id": chapa["id_chapa"],
                "nomeMaterial": chapa["nome_material"],
                "fornecedor": chapa["fornecedor"],
                "tamanho": chapa["area_disponivel"],
                "preco": chapa["preco_compra_m2"],
                "localizacao": chapa["localizacao"],
                "dataCriacao": chapa["data_entrada"]
            })
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({"error": "Erro interno do servidor"}), 500

@app.route('/app/retalhos', methods=['GET'])
def app_list_retalhos():
    """Lista todos os retalhos - Rota específica do app QualiCam"""
    try:
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM retalhos ORDER BY data_transformacao DESC')
        retalhos = cursor.fetchall()
        
        conn.close()
        
        result = []
        for retalho in retalhos:
            result.append({
                "id": retalho["id_chapa_original"],
                "nomeMaterial": retalho["nome_material"],
                "fornecedor": retalho["fornecedor"],
                "tamanho": retalho["area_retalho"],
                "localizacao": retalho["localizacao"],
                "dataCriacao": retalho["data_transformacao"]
            })
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({"error": "Erro interno do servidor"}), 500

@app.route('/impressora/testar', methods=['POST'])
def testar_impressora():
    """Testa a impressora usando o gabarito oficial"""
    try:
        import subprocess
        
        # Usar diretamente o gabarito oficial para teste
        comando = ['lpr', '-P', '4BARCODE', '-o', 'raw', '/home/maikon/Documents/QualiPatio/SERVIDOR/gabarito_oficial.zpl']
        
        resultado = subprocess.run(comando, capture_output=True, text=True, timeout=30)
        
        if resultado.returncode == 0:
            return jsonify({
                'success': True,
                'message': 'Teste de impressão enviado com sucesso usando gabarito oficial!',
                'comando_executado': ' '.join(comando),
                'gabarito_usado': '/home/maikon/Documents/QualiPatio/SERVIDOR/gabarito_oficial.zpl'
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Erro na impressão: {resultado.stderr}',
                'comando_executado': ' '.join(comando)
            }), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def gerar_numero_unico():
    """Gera um número único de 5 dígitos verificando APENAS a tabela chapas"""
    import random
    
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    
    max_tentativas = 100
    for _ in range(max_tentativas):
        # Gerar número de 5 dígitos
        numero = random.randint(10000, 99999)
        
        # Verificar se já existe APENAS na tabela chapas
        cursor.execute('SELECT COUNT(*) FROM chapas WHERE id_chapa = ?', (numero,))
        existe = cursor.fetchone()[0]
        
        if existe == 0:
            conn.close()
            return numero
    
    conn.close()
    # Se não conseguir gerar único, usar timestamp
    return int(str(int(datetime.now().timestamp()))[-5:])

@app.route('/etiquetas/gerar', methods=['POST'])
def gerar_etiqueta():
    """Gera etiquetas com múltiplos IDs únicos e quantidade por ID"""
    try:
        import subprocess
        import tempfile
        
        # Obter dados da requisição
        dados = request.get_json() or {}
        # Aceitar tanto os nomes novos quanto os antigos do cliente
        quantidade_ids = dados.get('quantidade_ids', dados.get('quantidade_etiquetas', 1))
        quantidade_por_id = dados.get('quantidade_por_id', dados.get('quantidade_cada', 1))
        
        
        # Ler o gabarito oficial
        with open('/home/maikon/Documents/QualiPatio/SERVIDOR/gabarito_oficial.zpl', 'r') as f:
            gabarito_base = f.read()
        
        # Processar cada ID único
        total_sucessos = 0
        total_erros = []
        ids_gerados = []
        
        for id_index in range(quantidade_ids):
            # Gerar número único para este ID
            numero_etiqueta = gerar_numero_unico()
            ids_gerados.append(numero_etiqueta)
            
            
            # Substituir o número placeholder (12345) pelo número gerado
            zpl_content = gabarito_base.replace('12345', str(numero_etiqueta))
            
            # Salvar arquivo temporário com o número substituído
            with tempfile.NamedTemporaryFile(mode='w', suffix='.zpl', delete=False) as f:
                f.write(zpl_content)
                arquivo_zpl = f.name
            
            # Imprimir múltiplas etiquetas deste ID
            for etiqueta_index in range(quantidade_por_id):
                comando = ['lpr', '-P', '4BARCODE', '-o', 'raw', arquivo_zpl]
                
                resultado = subprocess.run(comando, capture_output=True, text=True, timeout=30)
                
                if resultado.returncode == 0:
                    total_sucessos += 1
                else:
                    total_erros.append(f"Erro na etiqueta {etiqueta_index + 1} do ID {numero_etiqueta}: {resultado.stderr}")
            
            # Limpar arquivo temporário
            os.unlink(arquivo_zpl)
        
        total_solicitado = quantidade_ids * quantidade_por_id
        
        if total_sucessos == total_solicitado:
            return jsonify({
                'success': True,
                'message': f'{total_sucessos} etiquetas impressas com sucesso! ({quantidade_ids} IDs únicos, {quantidade_por_id} etiquetas cada)',
                'ids_gerados': ids_gerados,
                'quantidade_ids': quantidade_ids,
                'quantidade_por_id': quantidade_por_id,
                'total_impresso': total_sucessos,
                'total_solicitado': total_solicitado,
                'gabarito_usado': '/home/maikon/Documents/QualiPatio/SERVIDOR/gabarito_oficial.zpl'
            })
        elif total_sucessos > 0:
            return jsonify({
                'success': True,
                'message': f'{total_sucessos} de {total_solicitado} etiquetas impressas. Alguns erros ocorreram.',
                'ids_gerados': ids_gerados,
                'quantidade_ids': quantidade_ids,
                'quantidade_por_id': quantidade_por_id,
                'total_impresso': total_sucessos,
                'total_solicitado': total_solicitado,
                'erros': total_erros,
                'gabarito_usado': '/home/maikon/Documents/QualiPatio/SERVIDOR/gabarito_oficial.zpl'
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Nenhuma etiqueta foi impressa. Erros: {total_erros}',
                'ids_gerados': ids_gerados,
                'quantidade_ids': quantidade_ids,
                'quantidade_por_id': quantidade_por_id,
                'total_solicitado': total_solicitado,
                'erros': total_erros
            }), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    # O banco de dados é criado automaticamente pelo DatabaseManager
    
    print("SERVIDOR DE CONTROLE DE ESTOQUE - MARMORARIA")
    print("Servidor rodando em: http://localhost:5000")
    print("Para parar o servidor, pressione Ctrl+C")

@app.route('/retalhos', methods=['GET'])
def listar_retalhos():
    """Lista os retalhos cadastrados"""
    try:
        conn = db_manager.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id_retalho, id_chapa_original, nome_material, fornecedor,
                   area_retalho, localizacao, data_transformacao
            FROM retalhos
            ORDER BY data_transformacao DESC
        ''')

        retalhos = []
        for row in cursor.fetchall():
            ret = {
                'id_retalho': row['id_retalho'],
                'id_chapa_original': row['id_chapa_original'],
                'nome_material': row['nome_material'],
                'fornecedor': row['fornecedor'],
                'area_retalho': row['area_retalho'],
                'localizacao': row['localizacao'],
                'data_transformacao': row['data_transformacao']
            }
            retalhos.append(ret)

        conn.close()
        return jsonify({'success': True, 'retalhos': retalhos})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    # Executar servidor Flask
    app.run(host='0.0.0.0', port=5000, debug=True)

