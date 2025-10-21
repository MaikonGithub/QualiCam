package com.example.qualicam.ui.viewmodel

import android.app.Application
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.example.qualicam.network.NetworkModule
import com.example.qualicam.preferences.PreferencesManager
import com.example.qualicam.repository.ChapaRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

data class HomeUiState(
    val serverUrl: String = "",
    val isConnected: Boolean = false,
    val isLoading: Boolean = false,
    val errorMessage: String = ""
)

class HomeViewModel(application: Application) : AndroidViewModel(application) {
    private val preferencesManager = PreferencesManager(application)
    private val repository = ChapaRepository()
    
    private val _uiState = MutableStateFlow(HomeUiState())
    val uiState: StateFlow<HomeUiState> = _uiState.asStateFlow()
    
    init {
        loadServerUrl()
    }
    
    fun loadServerUrl() {
        viewModelScope.launch {
            preferencesManager.serverUrl.collect { url ->
                _uiState.value = _uiState.value.copy(serverUrl = url)
                NetworkModule.updateBaseUrl(url)
                testConnection()
            }
        }
    }
    
    fun updateServerUrl(url: String) {
        _uiState.value = _uiState.value.copy(serverUrl = url)
    }
    
    fun saveAndTestConnection() {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true, errorMessage = "")
            
            try {
                preferencesManager.saveServerUrl(_uiState.value.serverUrl)
                NetworkModule.updateBaseUrl(_uiState.value.serverUrl)
                testConnection()
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    errorMessage = "Erro ao salvar configurações: ${e.message}"
                )
            }
        }
    }
    
    private fun testConnection() {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true, errorMessage = "")
            
            repository.checkConnection()
                .onSuccess {
                    _uiState.value = _uiState.value.copy(
                        isConnected = true,
                        isLoading = false,
                        errorMessage = ""
                    )
                }
                .onFailure { exception ->
                    _uiState.value = _uiState.value.copy(
                        isConnected = false,
                        isLoading = false,
                        errorMessage = "Erro de conexão: ${exception.message}"
                    )
                }
        }
    }
}

