#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerenciamento do banco de dados SQLite
"""

import sqlite3
import random
import time
from typing import Optional, List, Dict, Any
from config import ServerConfig

class DatabaseManager:
    """Gerenciador do banco de dados"""
    
    def __init__(self):
        self.db_path = ServerConfig.get_database_path()
        self._create_tables()
    
    def _create_tables(self):
        """Cria as tabelas necessárias no banco de dados"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Tabela chapas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS chapas (
                    id_chapa INTEGER PRIMARY KEY,
                    nome_material TEXT NOT NULL,
                    fornecedor TEXT NOT NULL,
                    preco_compra_m2 REAL NOT NULL,
                    area_liquida_inicial REAL NOT NULL,
                    area_disponivel REAL NOT NULL,
                    localizacao TEXT NOT NULL,
                    status TEXT DEFAULT 'Disponível',
                    data_entrada TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabela movimentacoes
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS movimentacoes (
                    id_movimentacao INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_chapa INTEGER NOT NULL,
                    tipo_movimentacao TEXT NOT NULL,
                    quantidade_m2 REAL NOT NULL,
                    os_associada TEXT,
                    data_movimentacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (id_chapa) REFERENCES chapas (id_chapa)
                )
            ''')
            
            # Tabela retalhos
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS retalhos (
                    id_retalho INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_chapa_original INTEGER NOT NULL,
                    nome_material TEXT NOT NULL,
                    fornecedor TEXT NOT NULL,
                    area_retalho REAL NOT NULL,
                    localizacao TEXT NOT NULL,
                    data_transformacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (id_chapa_original) REFERENCES chapas (id_chapa)
                )
            ''')
            
            conn.commit()
    
    def get_connection(self) -> sqlite3.Connection:
        """Retorna uma conexão com o banco de dados"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    
    def get_available_slabs(self) -> List[Dict[str, Any]]:
        """Retorna lista de chapas disponíveis"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id_chapa, nome_material, fornecedor, preco_compra_m2,
                       area_liquida_inicial, area_disponivel, localizacao, status, data_entrada
                FROM chapas 
                WHERE status = 'Disponível'
                ORDER BY data_entrada DESC
            ''')
            
            return [dict(row) for row in cursor.fetchall()]
    
    def add_slab(self, slab_data: Dict[str, Any]) -> int:
        """Adiciona uma nova chapa ao estoque"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Usar ID fornecido pelo usuário (NÃO gerar automaticamente)
            id_chapa = slab_data['id_chapa']
            
            # Inserir nova chapa
            cursor.execute('''
                INSERT INTO chapas (id_chapa, nome_material, fornecedor, preco_compra_m2, 
                                  area_liquida_inicial, area_disponivel, localizacao)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (id_chapa, slab_data['nome_material'], slab_data['fornecedor'], 
                  slab_data['preco_compra_m2'], slab_data['area_liquida_inicial'], 
                  slab_data['area_liquida_inicial'], slab_data['localizacao']))
            
            # Registrar movimentação de entrada
            cursor.execute('''
                INSERT INTO movimentacoes (id_chapa, tipo_movimentacao, quantidade_m2)
                VALUES (?, 'ENTRADA', ?)
            ''', (id_chapa, slab_data['area_liquida_inicial']))
            
            conn.commit()
            return id_chapa
    
    def update_slab_area(self, slab_id: int, new_area: Optional[float], 
                        new_location: Optional[str], os_number: str = "") -> Dict[str, Any]:
        """Atualiza área disponível da chapa"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Verificar se a chapa existe
            cursor.execute('''
                SELECT area_disponivel, area_liquida_inicial, nome_material, fornecedor, localizacao
                FROM chapas 
                WHERE id_chapa = ? AND status = 'Disponível'
            ''', (slab_id,))
            
            slab = cursor.fetchone()
            if not slab:
                raise ValueError('Chapa não encontrada ou não disponível')
            
            current_area = slab['area_disponivel']
            initial_area = slab['area_liquida_inicial']
            current_location = slab['localizacao']
            
            updates = []
            params = []
            
            # Atualizar área se fornecida
            if new_area is not None:
                if new_area > initial_area:
                    raise ValueError(f'Nova área não pode exceder a área inicial ({initial_area:.2f}m²)')
                
                area_consumed = initial_area - new_area
                updates.append('area_disponivel = ?')
                params.append(new_area)
                
                # Se área zerou, marcar como consumida
                if new_area <= 0:
                    updates.append('status = ?')
                    params.append('Consumida')
                
                # Registrar movimentação se houve consumo
                if area_consumed > 0:
                    cursor.execute('''
                        INSERT INTO movimentacoes (id_chapa, tipo_movimentacao, quantidade_m2, os_associada)
                        VALUES (?, 'SAÍDA', ?, ?)
                    ''', (slab_id, area_consumed, os_number))
            
            # Atualizar localização se fornecida
            if new_location:
                updates.append('localizacao = ?')
                params.append(new_location)
            
            # Executar atualização
            if updates:
                params.append(slab_id)
                query = f"UPDATE chapas SET {', '.join(updates)} WHERE id_chapa = ?"
                cursor.execute(query, params)
            
            conn.commit()
            
            return {
                'id_chapa': slab_id,
                'area_anterior': current_area,
                'area_atual': new_area if new_area is not None else current_area,
                'localizacao_anterior': current_location,
                'localizacao_atual': new_location if new_location else current_location
            }
    
    def get_material_summary(self) -> List[Dict[str, Any]]:
        """Retorna resumo de metragem por material"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT nome_material, 
                       SUM(area_liquida_inicial) as area_total_inicial,
                       SUM(area_disponivel) as area_total_disponivel,
                       COUNT(*) as quantidade_chapas,
                       AVG(preco_compra_m2) as preco_medio_m2
                FROM chapas 
                GROUP BY nome_material
                ORDER BY nome_material
            ''')
            
            materials = []
            for row in cursor.fetchall():
                material = dict(row)
                material['percentual_disponivel'] = (
                    material['area_total_disponivel'] / material['area_total_inicial'] * 100
                    if material['area_total_inicial'] > 0 else 0
                )
                materials.append(material)
            
            return materials
