package com.example.qualicam.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.example.qualicam.ui.viewmodel.HomeViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HomeScreen(
    onNavigateToCamera: () -> Unit,
    viewModel: HomeViewModel = viewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    
    LaunchedEffect(Unit) {
        viewModel.loadServerUrl()
    }
    
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(24.dp)
    ) {
        Text(
            text = "QualiCam",
            fontSize = 32.sp,
            fontWeight = FontWeight.Bold,
            color = MaterialTheme.colorScheme.primary
        )
        
        // Status de conectividade
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(
                containerColor = if (uiState.isConnected) 
                    Color(0xFF4CAF50) else Color(0xFFF44336)
            )
        ) {
            Row(
                modifier = Modifier.padding(16.dp),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                Text(
                    text = if (uiState.isConnected) "Conectado" else "Desconectado",
                    color = Color.White,
                    fontWeight = FontWeight.Bold
                )
            }
        }
        
        // Campo de IP/Porta
        OutlinedTextField(
            value = uiState.serverUrl,
            onValueChange = viewModel::updateServerUrl,
            label = { Text("IP/Porta do Servidor") },
            placeholder = { Text("Ex: 10.0.2.2:5000 (simulador) ou 192.168.15.7:5000 (dispositivo)") },
            modifier = Modifier.fillMaxWidth(),
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Uri)
        )
        
        // Botão Salvar
        Button(
            onClick = { viewModel.saveAndTestConnection() },
            modifier = Modifier.fillMaxWidth(),
            enabled = !uiState.isLoading
        ) {
            if (uiState.isLoading) {
                CircularProgressIndicator(
                    modifier = Modifier.size(16.dp),
                    color = Color.White
                )
            } else {
                Text("Salvar e Testar Conexão")
            }
        }
        
        Spacer(modifier = Modifier.height(16.dp))
        
        // Botão Prosseguir
        Button(
            onClick = onNavigateToCamera,
            modifier = Modifier.fillMaxWidth(),
            enabled = uiState.isConnected && !uiState.isLoading
        ) {
            Text("Prosseguir para Câmera")
        }
        
        if (uiState.errorMessage.isNotEmpty()) {
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(containerColor = Color(0xFFFFEBEE))
            ) {
                Text(
                    text = uiState.errorMessage,
                    color = Color(0xFFD32F2F),
                    modifier = Modifier.padding(16.dp)
                )
            }
        }
    }
}

