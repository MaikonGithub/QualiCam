package com.example.qualicam.ui.viewmodel

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.qualicam.repository.ChapaRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

data class CameraUiState(
    val isScanning: Boolean = false,
    val scannedId: String = "",
    val navigationAction: String = "",
    val errorMessage: String = ""
)

class CameraViewModel : ViewModel() {
    private val repository = ChapaRepository()
    
    private val _uiState = MutableStateFlow(CameraUiState())
    val uiState: StateFlow<CameraUiState> = _uiState.asStateFlow()
    
    fun onBarcodeDetected(barcode: String) {
        if (_uiState.value.isScanning) return
        
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(
                isScanning = true,
                scannedId = barcode,
                errorMessage = ""
            )
            
            repository.getChapa(barcode)
                .onSuccess { chapa ->
                    if (chapa != null) {
                        // Chapa existe - ir para edição
                        _uiState.value = _uiState.value.copy(
                            isScanning = false,
                            navigationAction = "edit"
                        )
                    } else {
                        // Chapa não existe - ir para adição
                        _uiState.value = _uiState.value.copy(
                            isScanning = false,
                            navigationAction = "add"
                        )
                    }
                }
                .onFailure { exception ->
                    _uiState.value = _uiState.value.copy(
                        isScanning = false,
                        errorMessage = "Erro ao verificar chapa: ${exception.message}",
                        navigationAction = ""
                    )
                }
        }
    }
    
    fun resetNavigationAction() {
        _uiState.value = _uiState.value.copy(navigationAction = "")
    }
}

