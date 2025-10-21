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
import com.example.qualicam.ui.viewmodel.AddChapaViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AddChapaScreen(
    chapaId: String,
    onNavigateBack: () -> Unit,
    viewModel: AddChapaViewModel = viewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    
    LaunchedEffect(chapaId) {
        viewModel.setChapaId(chapaId)
    }
    
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        // Header
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Button(onClick = onNavigateBack) {
                Text("Cancelar")
            }
            
            Text(
                text = "Adicionar Chapa",
                fontSize = 20.sp,
                fontWeight = FontWeight.Bold
            )
        }
        
        // ID da chapa (readonly)
        OutlinedTextField(
            value = chapaId,
            onValueChange = {},
            label = { Text("ID da Chapa") },
            modifier = Modifier.fillMaxWidth(),
            enabled = false
        )
        
        // Nome do material
        OutlinedTextField(
            value = uiState.nomeMaterial,
            onValueChange = viewModel::updateNomeMaterial,
            label = { Text("Nome do Material") },
            modifier = Modifier.fillMaxWidth()
        )
        
        // Fornecedor
        OutlinedTextField(
            value = uiState.fornecedor,
            onValueChange = viewModel::updateFornecedor,
            label = { Text("Fornecedor") },
            modifier = Modifier.fillMaxWidth()
        )
        
        // Tamanho
        OutlinedTextField(
            value = uiState.tamanho,
            onValueChange = viewModel::updateTamanho,
            label = { Text("Tamanho (m²)") },
            modifier = Modifier.fillMaxWidth(),
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal)
        )
        
        // Preço
        OutlinedTextField(
            value = uiState.preco,
            onValueChange = viewModel::updatePreco,
            label = { Text("Preço (R$/m²)") },
            modifier = Modifier.fillMaxWidth(),
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal)
        )
        
        // Localização
        OutlinedTextField(
            value = uiState.localizacao,
            onValueChange = viewModel::updateLocalizacao,
            label = { Text("Localização") },
            modifier = Modifier.fillMaxWidth()
        )
        
        Spacer(modifier = Modifier.height(16.dp))
        
        // Botões
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            Button(
                onClick = onNavigateBack,
                modifier = Modifier.weight(1f),
                colors = ButtonDefaults.buttonColors(
                    containerColor = Color(0xFF757575)
                )
            ) {
                Text("Cancelar")
            }
            
            Button(
                onClick = { viewModel.saveChapa() },
                modifier = Modifier.weight(1f),
                enabled = uiState.isFormValid && !uiState.isLoading
            ) {
                if (uiState.isLoading) {
                    CircularProgressIndicator(
                        modifier = Modifier.size(16.dp),
                        color = Color.White
                    )
                } else {
                    Text("Salvar")
                }
            }
        }
        
        // Mensagem de erro
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
        
        // Mensagem de sucesso
        if (uiState.successMessage.isNotEmpty()) {
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(containerColor = Color(0xFFE8F5E8))
            ) {
                Text(
                    text = uiState.successMessage,
                    color = Color(0xFF2E7D32),
                    modifier = Modifier.padding(16.dp)
                )
            }
        }
    }
    
    // Navegação de volta após sucesso
    LaunchedEffect(uiState.shouldNavigateBack) {
        if (uiState.shouldNavigateBack) {
            onNavigateBack()
        }
    }
}

