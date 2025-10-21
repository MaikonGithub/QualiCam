package com.example.qualicam.network

import com.example.qualicam.data.Chapa
import com.example.qualicam.data.Retalho
import retrofit2.Response
import retrofit2.http.*

interface ApiService {
    // Rotas específicas do app QualiCam (prefixo /app)
    @GET("app/chapas/{id}")
    suspend fun getChapa(@Path("id") id: String): Response<Chapa>
    
    @POST("app/chapas")
    suspend fun createChapa(@Body chapa: Chapa): Response<Chapa>
    
    @PUT("app/chapas/{id}")
    suspend fun updateChapa(@Path("id") id: String, @Body chapa: Chapa): Response<Chapa>
    
    @POST("app/retalhos")
    suspend fun createRetalho(@Body retalho: Retalho): Response<Retalho>
    
    @DELETE("app/chapas/{id}")
    suspend fun deleteChapa(@Path("id") id: String): Response<Unit>
    
    @GET("app/health")
    suspend fun checkHealth(): Response<Unit>
    
    @GET("app/chapas")
    suspend fun listChapas(): Response<List<Chapa>>
    
    @GET("app/retalhos")
    suspend fun listRetalhos(): Response<List<Retalho>>
}

