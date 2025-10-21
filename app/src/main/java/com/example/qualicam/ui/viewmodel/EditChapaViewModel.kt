package com.example.qualicam.ui.viewmodel

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.qualicam.data.Chapa
import com.example.qualicam.data.Retalho
import com.example.qualicam.repository.ChapaRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

data class EditChapaUiState(
    val chapaId: String = "",
    val nomeMaterial: String = "",
    val fornecedor: String = "",
    val tamanho: String = "",
    val preco: String = "",
    val localizacao: String = "",
    val isLoading: Boolean = false,
    val errorMessage: String = "",
    val successMessage: String = "",
    val shouldNavigateBack: Boolean = false
) {
    val isFormValid: Boolean
        get() = nomeMaterial.isNotBlank() && 
                fornecedor.isNotBlank() && 
                tamanho.isNotBlank() && 
                preco.isNotBlank() && 
                localizacao.isNotBlank()
}

class EditChapaViewModel : ViewModel() {
    private val repository = ChapaRepository()
    
    private val _uiState = MutableStateFlow(EditChapaUiState())
    val uiState: StateFlow<EditChapaUiState> = _uiState.asStateFlow()
    
    fun loadChapa(id: String) {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true, errorMessage = "")
            
            repository.getChapa(id)
                .onSuccess { chapa ->
                    if (chapa != null) {
                        _uiState.value = _uiState.value.copy(
                            chapaId = chapa.id,
                            nomeMaterial = chapa.nomeMaterial,
                            fornecedor = chapa.fornecedor,
                            tamanho = chapa.tamanho.toString(),
                            preco = chapa.preco.toString(),
                            localizacao = chapa.localizacao,
                            isLoading = false
                        )
                    } else {
                        _uiState.value = _uiState.value.copy(
                            isLoading = false,
                            errorMessage = "Chapa não encontrada"
                        )
                    }
                }
                .onFailure { exception ->
                    _uiState.value = _uiState.value.copy(
                        isLoading = false,
                        errorMessage = "Erro ao carregar chapa: ${exception.message}"
                    )
                }
        }
    }
    
    fun updateNomeMaterial(value: String) {
        _uiState.value = _uiState.value.copy(nomeMaterial = value)
    }
    
    fun updateFornecedor(value: String) {
        _uiState.value = _uiState.value.copy(fornecedor = value)
    }
    
    fun updateTamanho(value: String) {
        _uiState.value = _uiState.value.copy(tamanho = value)
    }
    
    fun updatePreco(value: String) {
        _uiState.value = _uiState.value.copy(preco = value)
    }
    
    fun updateLocalizacao(value: String) {
        _uiState.value = _uiState.value.copy(localizacao = value)
    }
    
    fun updateChapa() {
        if (!_uiState.value.isFormValid) return
        
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(
                isLoading = true,
                errorMessage = "",
                successMessage = ""
            )
            
            try {
                val chapa = Chapa(
                    id = _uiState.value.chapaId,
                    nomeMaterial = _uiState.value.nomeMaterial,
                    fornecedor = _uiState.value.fornecedor,
                    tamanho = _uiState.value.tamanho.toDouble(),
                    preco = _uiState.value.preco.toDouble(),
                    localizacao = _uiState.value.localizacao
                )
                
                repository.updateChapa(_uiState.value.chapaId, chapa)
                    .onSuccess {
                        _uiState.value = _uiState.value.copy(
                            isLoading = false,
                            successMessage = "Chapa atualizada com sucesso!",
                            shouldNavigateBack = true
                        )
                    }
                    .onFailure { exception ->
                        _uiState.value = _uiState.value.copy(
                            isLoading = false,
                            errorMessage = "Erro ao atualizar chapa: ${exception.message}"
                        )
                    }
            } catch (e: NumberFormatException) {
                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    errorMessage = "Valores de tamanho e preço devem ser números válidos"
                )
            }
        }
    }
    
    fun transformToRetalho() {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(
                isLoading = true,
                errorMessage = "",
                successMessage = ""
            )
            
            try {
                val retalho = Retalho(
                    id = _uiState.value.chapaId,
                    nomeMaterial = _uiState.value.nomeMaterial,
                    fornecedor = _uiState.value.fornecedor,
                    tamanho = _uiState.value.tamanho.toDouble(),
                    preco = _uiState.value.preco.toDouble(),
                    localizacao = _uiState.value.localizacao
                )
                
                repository.createRetalho(retalho)
                    .onSuccess {
                        repository.deleteChapa(_uiState.value.chapaId)
                            .onSuccess {
                                _uiState.value = _uiState.value.copy(
                                    isLoading = false,
                                    successMessage = "Chapa transformada em retalho com sucesso!",
                                    shouldNavigateBack = true
                                )
                            }
                            .onFailure { exception ->
                                _uiState.value = _uiState.value.copy(
                                    isLoading = false,
                                    errorMessage = "Erro ao remover chapa: ${exception.message}"
                                )
                            }
                    }
                    .onFailure { exception ->
                        _uiState.value = _uiState.value.copy(
                            isLoading = false,
                            errorMessage = "Erro ao transformar em retalho: ${exception.message}"
                        )
                    }
            } catch (e: NumberFormatException) {
                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    errorMessage = "Valores de tamanho e preço devem ser números válidos"
                )
            }
        }
    }
}

