import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:file_picker/file_picker.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:io';

void main() {
  runApp(const EngramApp());
}

class EngramApp extends StatelessWidget {
  const EngramApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider(
      create: (context) => EngramState(),
      child: MaterialApp(
        title: 'Engram',
        theme: ThemeData(
          useMaterial3: true,
          colorScheme: ColorScheme.fromSeed(
            seedColor: const Color(0xFF6366F1), // Indigo
            brightness: Brightness.dark,
          ).copyWith(
            surface: const Color(0xFF0F0F23), // Deep dark blue
            onSurface: const Color(0xFFE2E8F0), // Light gray text
            primary: const Color(0xFF6366F1), // Indigo
            secondary: const Color(0xFF8B5CF6), // Purple
            tertiary: const Color(0xFF06B6D4), // Cyan
          ),
          scaffoldBackgroundColor: const Color(0xFF0F0F23),
          cardColor: const Color(0xFF1E1E3F),
          appBarTheme: const AppBarTheme(
            backgroundColor: Color(0xFF1E1E3F),
            foregroundColor: Color(0xFFE2E8F0),
          ),
        ),
        home: const MainPage(),
      ),
    );
  }
}



class EngramState extends ChangeNotifier {
  List<Fragment> fragments = [];
  bool isLoading = false;
  bool isBuilding = false;
  String? error;
  String? successMessage;
  String? availableModel; // Store the available model name
  
  // Content for building workflow
  String? rawContent;
  String? builtContent;
  String? contentSource; // 'text_input' or filename
  
  static const String apiBase = 'http://localhost:5000';
  static const String vllmApiBase = 'http://localhost:8000';

  // Navigate to build memory page with text content
  void navigateToBuildMemory(String content, String source) {
    rawContent = content;
    contentSource = source;
    builtContent = null; // Reset previous build
    notifyListeners();
  }

  Future<void> addTextFragments(String text, {String? sessionName}) async {
    if (text.trim().isEmpty) return;
    
    setLoading(true);
    try {
      final response = await http.post(
        Uri.parse('$apiBase/fragments'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'text': text,
          'source': 'flutter_app',
          if (sessionName != null) 'session_name': sessionName,
        }),
      );

      final result = jsonDecode(response.body);
      if (result['success'] == true) {
        successMessage = 'Added ${result['fragments_added']} fragments';
        // Navigate to build memory page
        navigateToBuildMemory(text, 'text_input');
      } else {
        error = result['error'] ?? 'Unknown error';
      }
    } catch (e) {
      error = 'Connection error: $e';
    }
    setLoading(false);
  }

  Future<void> uploadFile(PlatformFile file) async {
    setLoading(true);
    try {
      final bytes = file.bytes ?? await File(file.path!).readAsBytes();
      final content = String.fromCharCodes(bytes);
      final base64Content = base64Encode(bytes);

      final response = await http.post(
        Uri.parse('$apiBase/fragments/file'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'file_content': base64Content,
          'filename': file.name,
          'source': 'flutter_app',
        }),
      );

      final result = jsonDecode(response.body);
      if (result['success'] == true) {
        successMessage = 'Extracted ${result['fragments_added']} fragments from ${file.name}';
        // Navigate to build memory page with file content
        navigateToBuildMemory(content, file.name);
      } else {
        error = result['error'] ?? 'Unknown error';
      }
    } catch (e) {
      error = 'File processing error: $e';
    }
    setLoading(false);
  }

  Future<void> _fetchAvailableModels() async {
    if (availableModel != null) return; // Already fetched
    
    try {
      final response = await http.get(
        Uri.parse('$vllmApiBase/v1/models'),
        headers: {'Content-Type': 'application/json'},
      );
      
      if (response.statusCode == 200) {
        final result = jsonDecode(response.body);
        if (result['data'] != null && result['data'].isNotEmpty) {
          availableModel = result['data'][0]['id'];
          print('Found model: $availableModel');
        }
      }
    } catch (e) {
      print('Could not fetch available models: $e');
      // Set a known working model as fallback
      availableModel = '../models/Qwen2.5-3B-Instruct-GPTQ-Int8/';
    }
  }



  Future<void> buildMemory() async {
    if (rawContent == null) return;
    
    await _fetchAvailableModels();
    setBuilding(true);
    
    try {
      final prompt = """You are helping build memories from fragments of text. Try to infer what the user is writing about. Then, complete the thoughts so they are full sentences. Your task is add text to make the fragments the user provides seem like a complete journal entry. Do not add any new details but try to add words so there is clarity.

Text to build into memory:
${rawContent!}""";

      final response = await http.post(
        Uri.parse('$vllmApiBase/v1/chat/completions'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'model': availableModel ?? '../models/Qwen2.5-3B-Instruct-GPTQ-Int8/',
          'messages': [
            {'role': 'user', 'content': prompt}
          ],
          'max_tokens': 1000,
          'temperature': 0.7,
        }),
      );

      if (response.statusCode == 200) {
        final result = jsonDecode(response.body);
        builtContent = result['choices'][0]['message']['content'];
        successMessage = 'Memory built successfully!';
      } else {
        error = 'Memory building failed: ${response.statusCode}';
      }
    } catch (e) {
      error = 'Memory building error: $e';
    }
    setBuilding(false);
  }

  Future<void> approveBuild() async {
    if (builtContent == null || rawContent == null) return;
    
    setLoading(true);
    try {
      // Save fragments to SQLite (already done during upload, but mark as processed)
      // TODO: Save built memory to Letta database
      
      successMessage = 'Memory approved and saved!';
      
      // Reset state and go back to main page
      rawContent = null;
      builtContent = null;
      contentSource = null;
      
    } catch (e) {
      error = 'Save error: $e';
    }
    setLoading(false);
  }

  void rejectBuild() {
    builtContent = null;
    notifyListeners();
  }

  void backToMainPage() {
    rawContent = null;
    builtContent = null;
    contentSource = null;
    notifyListeners();
  }

  void setLoading(bool loading) {
    isLoading = loading;
    if (loading) {
      error = null;
      successMessage = null;
    }
    notifyListeners();
  }

  void setBuilding(bool building) {
    isBuilding = building;
    notifyListeners();
  }

  void clearMessages() {
    error = null;
    successMessage = null;
    notifyListeners();
  }
}

class Fragment {
  final String id;
  final String content;
  final String source;
  final DateTime createdAt;
  final bool processed;

  Fragment({
    required this.id,
    required this.content,
    required this.source,
    required this.createdAt,
    required this.processed,
  });

  factory Fragment.fromJson(Map<String, dynamic> json) {
    return Fragment(
      id: json['id'],
      content: json['content'],
      source: json['source'],
      createdAt: DateTime.parse(json['created_at']),
      processed: json['processed'] == 1 || json['processed'] == true,
    );
  }
}

class MainPage extends StatelessWidget {
  const MainPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Consumer<EngramState>(
      builder: (context, state, child) {
        // Show build memory page if we have raw content
        if (state.rawContent != null) {
          return const BuildMemoryPage();
        }
        // Otherwise show the main input page
        return const HomePage();
      },
    );
  }
}

class HomePage extends StatefulWidget {
  const HomePage({Key? key}) : super(key: key);

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  final TextEditingController _textController = TextEditingController();
  final TextEditingController _sessionController = TextEditingController();
  bool _hasText = false;

  @override
  void initState() {
    super.initState();
    // Listen to text changes to enable/disable button
    _textController.addListener(_onTextChanged);
  }

  void _onTextChanged() {
    final hasText = _textController.text.trim().isNotEmpty;
    if (hasText != _hasText) {
      setState(() {
        _hasText = hasText;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      body: Consumer<EngramState>(
        builder: (context, state, child) {
          return SafeArea(
            child: Padding(
              padding: const EdgeInsets.all(24.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Header
                  Container(
                    margin: const EdgeInsets.only(bottom: 32),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Container(
                              padding: const EdgeInsets.all(12),
                              decoration: BoxDecoration(
                                color: Theme.of(context).colorScheme.primary.withOpacity(0.1),
                                borderRadius: BorderRadius.circular(12),
                              ),
                              child: Icon(
                                Icons.psychology,
                                color: Theme.of(context).colorScheme.primary,
                                size: 32,
                              ),
                            ),
                            const SizedBox(width: 16),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    'Engram',
                                    style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                                      fontWeight: FontWeight.bold,
                                      color: Theme.of(context).colorScheme.onSurface,
                                    ),
                                  ),
                                  Text(
                                    "Save you.",
                                    style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                                      color: Theme.of(context).colorScheme.onSurface.withOpacity(0.7),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),

                  // Status Messages
                  if (state.error != null) ...[
                    Container(
                      width: double.infinity,
                      padding: const EdgeInsets.all(16),
                      margin: const EdgeInsets.only(bottom: 24),
                      decoration: BoxDecoration(
                        color: Colors.red.shade900.withOpacity(0.2),
                        border: Border.all(color: Colors.red.shade600),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Row(
                        children: [
                          Icon(Icons.error, color: Colors.red.shade400, size: 20),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Text(
                              state.error!,
                              style: TextStyle(color: Colors.red.shade300),
                            ),
                          ),
                          IconButton(
                            onPressed: state.clearMessages,
                            icon: Icon(Icons.close, color: Colors.red.shade400),
                            iconSize: 20,
                          ),
                        ],
                      ),
                    ),
                  ],
                  
                  if (state.successMessage != null) ...[
                    Container(
                      width: double.infinity,
                      padding: const EdgeInsets.all(16),
                      margin: const EdgeInsets.only(bottom: 24),
                      decoration: BoxDecoration(
                        color: Colors.green.shade900.withOpacity(0.2),
                        border: Border.all(color: Colors.green.shade600),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Row(
                        children: [
                          Icon(Icons.check_circle, color: Colors.green.shade400, size: 20),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Text(
                              state.successMessage!,
                              style: TextStyle(color: Colors.green.shade300),
                            ),
                          ),
                          IconButton(
                            onPressed: state.clearMessages,
                            icon: Icon(Icons.close, color: Colors.green.shade400),
                            iconSize: 20,
                          ),
                        ],
                      ),
                    ),
                  ],

                  // Main Text Input Section
                  Expanded(
                    child: Container(
                      padding: const EdgeInsets.all(24),
                      decoration: BoxDecoration(
                        color: Theme.of(context).cardColor,
                        borderRadius: BorderRadius.circular(16),
                        border: Border.all(
                          color: Theme.of(context).colorScheme.primary.withOpacity(0.2),
                        ),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Add fragments',
                            style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                              fontWeight: FontWeight.bold,
                              color: Theme.of(context).colorScheme.primary,
                            ),
                          ),
                          const SizedBox(height: 8),
                          Text(
                          'This will build your fragments into a memory.',
                            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                              color: Theme.of(context).colorScheme.onSurface.withOpacity(0.7),
                            ),
                          ),
                          const SizedBox(height: 24),
                          
                          // Session Name Input
                          TextField(
                            controller: _sessionController,
                            decoration: InputDecoration(
                              labelText: 'Tags (Optional)',
                              hintText: 'e.g., Morning thoughts, Work notes',
                              border: OutlineInputBorder(
                                borderRadius: BorderRadius.circular(12),
                              ),
                              prefixIcon: const Icon(Icons.label_outline),
                            ),
                          ),
                          const SizedBox(height: 16),
                          
                          // Main Text Input
                          Expanded(
                            child: TextField(
                              controller: _textController,
                              maxLines: null,
                              expands: true,
                              textAlignVertical: TextAlignVertical.top,
                              decoration: InputDecoration(
                                hintText: 'Free write here...',
                                border: OutlineInputBorder(
                                  borderRadius: BorderRadius.circular(12),
                                ),
                                contentPadding: const EdgeInsets.all(16),
                              ),
                              style: Theme.of(context).textTheme.bodyLarge,
                            ),
                          ),
                          const SizedBox(height: 16),
                          
                          // Action Buttons
                          Row(
                            children: [
                              // Upload File Button
                              OutlinedButton.icon(
                                onPressed: state.isLoading
                                    ? null
                                    : () async {
                                        final result = await FilePicker.platform.pickFiles(
                                          type: FileType.custom,
                                          allowedExtensions: ['txt', 'md', 'json'],
                                        );
                                        
                                        if (result != null && result.files.isNotEmpty) {
                                          await state.uploadFile(result.files.first);
                                        }
                                      },
                                icon: const Icon(Icons.upload_file),
                                label: const Text('Upload File'),
                                style: OutlinedButton.styleFrom(
                                  padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
                                ),
                              ),
                              const SizedBox(width: 16),
                              
                              // Process Text Button
                              Expanded(
                                child: ElevatedButton.icon(
                                  onPressed: state.isLoading || !_hasText
                                      ? null
                                      : () async {
                                          await state.addTextFragments(
                                            _textController.text,
                                            sessionName: _sessionController.text.isEmpty
                                                ? null
                                                : _sessionController.text,
                                          );
                                          _textController.clear();
                                          _sessionController.clear();
                                          setState(() {
                                            _hasText = false;
                                          });
                                        },
                                  icon: state.isLoading
                                      ? const SizedBox(
                                          width: 20,
                                          height: 20,
                                          child: CircularProgressIndicator(strokeWidth: 2),
                                        )
                                      : const Icon(Icons.auto_fix_high),
                                  label: Text(state.isLoading ? 'Processing...' : 'Process Memory'),
                                  style: ElevatedButton.styleFrom(
                                    backgroundColor: Theme.of(context).colorScheme.primary,
                                    foregroundColor: Colors.white,
                                    padding: const EdgeInsets.symmetric(vertical: 16),
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }


  @override
  void dispose() {
    _textController.removeListener(_onTextChanged);
    _textController.dispose();
    _sessionController.dispose();
    super.dispose();
  }
}

class BuildMemoryPage extends StatelessWidget {
  const BuildMemoryPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('🧠 Memory Staging Area'),
        backgroundColor: Theme.of(context).appBarTheme.backgroundColor,
        foregroundColor: Theme.of(context).appBarTheme.foregroundColor,
        leading: Consumer<EngramState>(
          builder: (context, state, child) {
            return IconButton(
              icon: const Icon(Icons.arrow_back),
              onPressed: state.backToMainPage,
            );
          },
        ),
      ),
      body: Consumer<EngramState>(
        builder: (context, state, child) {
          return SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Status Messages
                if (state.error != null) ...[
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(16),
                    margin: const EdgeInsets.only(bottom: 24),
                    decoration: BoxDecoration(
                      color: Colors.red.shade900.withOpacity(0.2),
                      border: Border.all(color: Colors.red.shade600),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Row(
                      children: [
                        Icon(Icons.error, color: Colors.red.shade400, size: 20),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Text(
                            state.error!,
                            style: TextStyle(color: Colors.red.shade300),
                          ),
                        ),
                        IconButton(
                          onPressed: state.clearMessages,
                          icon: Icon(Icons.close, color: Colors.red.shade400),
                          iconSize: 20,
                        ),
                      ],
                    ),
                  ),
                ],
                
                if (state.successMessage != null) ...[
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(16),
                    margin: const EdgeInsets.only(bottom: 24),
                    decoration: BoxDecoration(
                      color: Colors.green.shade900.withOpacity(0.2),
                      border: Border.all(color: Colors.green.shade600),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Row(
                      children: [
                        Icon(Icons.check_circle, color: Colors.green.shade400, size: 20),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Text(
                            state.successMessage!,
                            style: TextStyle(color: Colors.green.shade300),
                          ),
                        ),
                        IconButton(
                          onPressed: state.clearMessages,
                          icon: Icon(Icons.close, color: Colors.green.shade400),
                          iconSize: 20,
                        ),
                      ],
                    ),
                  ),
                ],

                // Original Content Section
                Container(
                  padding: const EdgeInsets.all(24),
                  decoration: BoxDecoration(
                    color: Theme.of(context).cardColor,
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(
                      color: Theme.of(context).colorScheme.primary.withOpacity(0.2),
                    ),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Icon(
                            Icons.description, 
                            size: 24,
                            color: Theme.of(context).colorScheme.primary,
                          ),
                          const SizedBox(width: 12),
                          Text(
                            'Fragments',
                            style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                              fontWeight: FontWeight.bold,
                              color: Theme.of(context).colorScheme.primary,
                            ),
                          ),
                          const Spacer(),
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                            decoration: BoxDecoration(
                              color: Theme.of(context).colorScheme.secondary.withOpacity(0.2),
                              borderRadius: BorderRadius.circular(20),
                              border: Border.all(
                                color: Theme.of(context).colorScheme.secondary.withOpacity(0.3),
                              ),
                            ),
                            child: Text(
                              state.contentSource == 'text_input' 
                                  ? 'Text Input' 
                                  : 'File: ${state.contentSource}',
                              style: TextStyle(
                                fontSize: 12,
                                color: Theme.of(context).colorScheme.secondary,
                                fontWeight: FontWeight.w500,
                              ),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 20),
                      Container(
                        width: double.infinity,
                        height: 200,
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          color: Theme.of(context).colorScheme.surface.withOpacity(0.5),
                          border: Border.all(
                            color: Theme.of(context).colorScheme.onSurface.withOpacity(0.2),
                          ),
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: SingleChildScrollView(
                          child: Text(
                            state.rawContent ?? '',
                            style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                              height: 1.6,
                              color: Theme.of(context).colorScheme.onSurface,
                            ),
                          ),
                        ),
                      ),
                        const SizedBox(height: 20),
                        SizedBox(
                          width: double.infinity,
                          child: ElevatedButton.icon(
                            onPressed: state.isBuilding ? null : state.buildMemory,
                            icon: state.isBuilding 
                                ? const SizedBox(
                                    width: 20,
                                    height: 20,
                                    child: CircularProgressIndicator(strokeWidth: 2),
                                  )
                                : const Icon(Icons.auto_fix_high),
                            label: Text(state.isBuilding ? 'Building...' : 'Build Memory'),
                            style: ElevatedButton.styleFrom(
                              backgroundColor: Theme.of(context).colorScheme.primary,
                              foregroundColor: Colors.white,
                              padding: const EdgeInsets.symmetric(vertical: 16),
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),

                // Built Content Section (shown after building)
                if (state.builtContent != null) ...[
                  const SizedBox(height: 32),
                  Container(
                    padding: const EdgeInsets.all(24),
                    decoration: BoxDecoration(
                      color: Theme.of(context).cardColor,
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(
                        color: Theme.of(context).colorScheme.primary.withOpacity(0.2),
                      ),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Icon(
                              Icons.psychology, 
                              size: 24, 
                              color: Theme.of(context).colorScheme.primary,
                            ),
                            const SizedBox(width: 12),
                            Text(
                              'Finished Engram',
                              style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                                fontWeight: FontWeight.bold,
                                color: Theme.of(context).colorScheme.primary,
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 20),
                        Container(
                          width: double.infinity,
                          padding: const EdgeInsets.all(16),
                          decoration: BoxDecoration(
                            color: Theme.of(context).colorScheme.primary.withOpacity(0.05),
                            border: Border.all(
                              color: Theme.of(context).colorScheme.primary.withOpacity(0.3),
                            ),
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: Text(
                            state.builtContent!,
                            style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                              height: 1.6,
                              color: Theme.of(context).colorScheme.onSurface,
                            ),
                          ),
                        ),
                        const SizedBox(height: 24),
                        Row(
                          children: [
                            Expanded(
                              child: ElevatedButton.icon(
                                onPressed: state.isLoading ? null : state.approveBuild,
                                icon: state.isLoading 
                                    ? const SizedBox(
                                        width: 16,
                                        height: 16,
                                        child: CircularProgressIndicator(strokeWidth: 2),
                                      )
                                    : const Icon(Icons.check),
                                label: Text(state.isLoading ? 'Saving...' : 'Approve & Save'),
                                style: ElevatedButton.styleFrom(
                                  backgroundColor: Colors.green.shade600,
                                  foregroundColor: Colors.white,
                                  padding: const EdgeInsets.symmetric(vertical: 16),
                                ),
                              ),
                            ),
                            const SizedBox(width: 16),
                            Expanded(
                              child: OutlinedButton.icon(
                                onPressed: state.rejectBuild,
                                icon: const Icon(Icons.close),
                                label: const Text('Reject'),
                                style: OutlinedButton.styleFrom(
                                  foregroundColor: Colors.red.shade400,
                                  side: BorderSide(color: Colors.red.shade400),
                                  padding: const EdgeInsets.symmetric(vertical: 16),
                                ),
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  )
                ],],
            ));
            }
            ));}
        }