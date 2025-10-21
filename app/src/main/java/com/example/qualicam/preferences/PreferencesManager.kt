package com.example.qualicam.preferences

import android.content.Context
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map

private val Context.dataStore: DataStore<Preferences> by preferencesDataStore(name = "settings")

class PreferencesManager(private val context: Context) {
    private val serverUrlKey = stringPreferencesKey("server_url")
    
    val serverUrl: Flow<String> = context.dataStore.data.map { preferences ->
        preferences[serverUrlKey] ?: "http://10.0.2.2:5000"
    }
    
    suspend fun saveServerUrl(url: String) {
        context.dataStore.edit { preferences ->
            preferences[serverUrlKey] = url
        }
    }
}

