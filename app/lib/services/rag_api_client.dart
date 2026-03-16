import 'dart:convert';

import 'package:http/http.dart' as http;

/// Client for the RAG demo API (Python FastAPI backend).
/// Mirrors the flow used in production: send question -> get answer + sources.
class RagApiClient {
  RagApiClient({required this.baseUrl});

  final String baseUrl;

  /// POST /query with [question]. Returns (answer, sources).
  /// Throws on network or API error.
  Future<({String answer, List<String> sources})> query(String question) async {
    final uri = Uri.parse('$baseUrl/query');
    final response = await http.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'question': question}),
    );
    if (response.statusCode != 200) {
      final body = response.body;
      throw Exception(
        'RAG API error ${response.statusCode}: ${body.length > 200 ? body.substring(0, 200) : body}',
      );
    }
    final map = jsonDecode(response.body) as Map<String, dynamic>;
    final answer = map['answer'] as String? ?? '';
    final sourcesList = map['sources'];
    final sources = sourcesList is List
        ? sourcesList.map((e) => e?.toString() ?? '').where((s) => s.isNotEmpty).toList()
        : <String>[];
    return (answer: answer, sources: sources);
  }

  /// GET /health to check if the backend is up.
  Future<bool> health() async {
    try {
      final uri = Uri.parse('$baseUrl/health');
      final response = await http.get(uri).timeout(const Duration(seconds: 2));
      return response.statusCode == 200;
    } catch (_) {
      return false;
    }
  }
}
