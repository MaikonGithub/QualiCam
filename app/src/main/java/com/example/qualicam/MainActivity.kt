package com.example.qualicam

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.example.qualicam.ui.screens.*
import com.example.qualicam.ui.theme.QualiCamTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            QualiCamTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    QualiCamApp()
                }
            }
        }
    }
}

@Composable
fun QualiCamApp() {
    val navController = rememberNavController()
    
    NavHost(
        navController = navController,
        startDestination = "home"
    ) {
        composable("home") {
            HomeScreen(
                onNavigateToCamera = {
                    navController.navigate("camera")
                }
            )
        }
        
        composable("camera") {
            CameraScreen(
                onNavigateBack = {
                    navController.popBackStack()
                },
                onNavigateToAddChapa = { chapaId ->
                    navController.navigate("add_chapa/$chapaId")
                },
                onNavigateToEditChapa = { chapaId ->
                    navController.navigate("edit_chapa/$chapaId")
                }
            )
        }
        
        composable("add_chapa/{chapaId}") { backStackEntry ->
            val chapaId = backStackEntry.arguments?.getString("chapaId") ?: ""
            AddChapaScreen(
                chapaId = chapaId,
                onNavigateBack = {
                    navController.popBackStack()
                }
            )
        }
        
        composable("edit_chapa/{chapaId}") { backStackEntry ->
            val chapaId = backStackEntry.arguments?.getString("chapaId") ?: ""
            EditChapaScreen(
                chapaId = chapaId,
                onNavigateBack = {
                    navController.popBackStack()
                }
            )
        }
    }
}