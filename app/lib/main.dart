import 'package:flutter/material.dart';

import 'screens/chat_screen.dart';
import 'services/rag_api_client.dart';

/// Base URL of the RAG API. When using Android emulator, use http://10.0.2.2:8000
/// so the emulator can reach the host machine.
const _kRagBaseUrl = 'http://localhost:8000';

void main() {
  runApp(const RagDemoApp());
}

class RagDemoApp extends StatelessWidget {
  const RagDemoApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'RAG Demo',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.teal),
        useMaterial3: true,
      ),
      home: ChatScreen(
        client: RagApiClient(baseUrl: _kRagBaseUrl),
      ),
    );
  }
}
