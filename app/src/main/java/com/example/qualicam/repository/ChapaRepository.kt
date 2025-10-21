package com.example.qualicam.repository

import com.example.qualicam.data.Chapa
import com.example.qualicam.data.Retalho
import com.example.qualicam.network.ApiService
import com.example.qualicam.network.NetworkModule
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

class ChapaRepository {
    private val apiService: ApiService = NetworkModule.apiService
    
    suspend fun getChapa(id: String): Result<Chapa?> = withContext(Dispatchers.IO) {
        try {
            val response = apiService.getChapa(id)
            if (response.isSuccessful) {
                Result.success(response.body())
            } else {
                Result.success(null)
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun createChapa(chapa: Chapa): Result<Chapa> = withContext(Dispatchers.IO) {
        try {
            val response = apiService.createChapa(chapa)
            if (response.isSuccessful) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("Erro ao criar chapa: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun updateChapa(id: String, chapa: Chapa): Result<Chapa> = withContext(Dispatchers.IO) {
        try {
            val response = apiService.updateChapa(id, chapa)
            if (response.isSuccessful) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("Erro ao atualizar chapa: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun createRetalho(retalho: Retalho): Result<Retalho> = withContext(Dispatchers.IO) {
        try {
            val response = apiService.createRetalho(retalho)
            if (response.isSuccessful) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("Erro ao criar retalho: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun deleteChapa(id: String): Result<Unit> = withContext(Dispatchers.IO) {
        try {
            val response = apiService.deleteChapa(id)
            if (response.isSuccessful) {
                Result.success(Unit)
            } else {
                Result.failure(Exception("Erro ao deletar chapa: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun checkConnection(): Result<Unit> = withContext(Dispatchers.IO) {
        try {
            val response = apiService.checkHealth()
            if (response.isSuccessful) {
                Result.success(Unit)
            } else {
                Result.failure(Exception("Servidor não está respondendo"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}

