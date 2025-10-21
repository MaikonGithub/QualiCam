#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configurações do servidor
"""

import os

class ServerConfig:
    """Configurações do servidor"""
    
    @staticmethod
    def get_database_path():
        """Retorna o caminho do banco de dados"""
        return os.path.join(os.path.dirname(__file__), 'qualicam.db')
    
    @staticmethod
    def get_server_host():
        """Retorna o host do servidor"""
        return '0.0.0.0'
    
    @staticmethod
    def get_server_port():
        """Retorna a porta do servidor"""
        return 5000

