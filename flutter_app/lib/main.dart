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
        title: 'Engram - Brain Memory System',
        theme: ThemeData(
          primarySwatch: Colors.deepPurple,
          useMaterial3: true,
          colorScheme: ColorScheme.fromSeed(
            seedColor: Colors.deepPurple,
            brightness: Brightness.light,
          ),
        ),
        home: const HomePage(),
      ),
    );
  }
}

class ChatMessage {
  final String content;
  final bool isUser;
  final DateTime timestamp;

  ChatMessage({
    required this.content,
    required this.isUser,
    required this.timestamp,
  });
}

class EngramState extends ChangeNotifier {
  List<Fragment> fragments = [];
  List<ChatMessage> chatMessages = [];
  bool isLoading = false;
  bool isChatLoading = false;
  String? error;
  String? successMessage;
  String? availableModel; // Store the available model name
  
  static const String apiBase = 'http://localhost:5000';
  static const String vllmApiBase = 'http://localhost:8000';

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

  Future<void> sendChatMessage(String message) async {
    if (message.trim().isEmpty) return;

    // Fetch available models if we haven't already
    await _fetchAvailableModels();

    // Add user message
    chatMessages.add(ChatMessage(
      content: message,
      isUser: true,
      timestamp: DateTime.now(),
    ));
    notifyListeners();

    setChatLoading(true);
    try {
      final response = await http.post(
        Uri.parse('$vllmApiBase/v1/chat/completions'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'model': availableModel ?? '../models/Qwen2.5-3B-Instruct-GPTQ-Int8/', // Use fetched model or known working model
          'messages': [
            {'role': 'user', 'content': message}
          ],
          'max_tokens': 500,
          'temperature': 0.7,
        }),
      );

      if (response.statusCode == 200) {
        final result = jsonDecode(response.body);
        final aiResponse = result['choices'][0]['message']['content'];
        
        // Add AI response
        chatMessages.add(ChatMessage(
          content: aiResponse,
          isUser: false,
          timestamp: DateTime.now(),
        ));
      } else {
        error = 'AI server error: ${response.statusCode}';
        // Add error message to chat
        chatMessages.add(ChatMessage(
          content: 'Sorry, I encountered an error. Please make sure the vLLM server is running.',
          isUser: false,
          timestamp: DateTime.now(),
        ));
      }
    } catch (e) {
      error = 'Chat connection error: $e';
      // Add error message to chat
      chatMessages.add(ChatMessage(
        content: 'Sorry, I cannot connect to the AI server. Please make sure the vLLM server is running.',
        isUser: false,
        timestamp: DateTime.now(),
      ));
    }
    setChatLoading(false);
  }

  void clearChat() {
    chatMessages.clear();
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

  void setChatLoading(bool loading) {
    isChatLoading = loading;
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

class HomePage extends StatefulWidget {
  const HomePage({Key? key}) : super(key: key);

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  final TextEditingController _textController = TextEditingController();
  final TextEditingController _sessionController = TextEditingController();
  final TextEditingController _chatController = TextEditingController();
  final ScrollController _chatScrollController = ScrollController();
  bool _showTextInput = true; // Toggle between text input and file upload

  @override
  void initState() {
    super.initState();
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_chatScrollController.hasClients) {
        _chatScrollController.animateTo(
          _chatScrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('🧠 Engram - Cortex Interface'),
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
      ),
      body: Consumer<EngramState>(
        builder: (context, state, child) {
          // Auto-scroll chat when new messages arrive
          if (state.chatMessages.isNotEmpty) {
            _scrollToBottom();
          }

          return Column(
            children: [
              // Status Messages
              if (state.error != null)
                Container(
                  width: double.infinity,
                  margin: const EdgeInsets.all(16),
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.red.shade100,
                    border: Border.all(color: Colors.red.shade300),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Row(
                    children: [
                      Expanded(
                        child: Text(
                          state.error!,
                          style: TextStyle(color: Colors.red.shade700),
                        ),
                      ),
                      IconButton(
                        onPressed: state.clearMessages,
                        icon: const Icon(Icons.close),
                        iconSize: 16,
                      ),
                    ],
                  ),
                ),
              
              if (state.successMessage != null)
                Container(
                  width: double.infinity,
                  margin: const EdgeInsets.all(16),
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.green.shade100,
                    border: Border.all(color: Colors.green.shade300),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Row(
                    children: [
                      Expanded(
                        child: Text(
                          state.successMessage!,
                          style: TextStyle(color: Colors.green.shade700),
                        ),
                      ),
                      IconButton(
                        onPressed: state.clearMessages,
                        icon: const Icon(Icons.close),
                        iconSize: 16,
                      ),
                    ],
                  ),
                ),

              // Start a Memory Section (Combined)
              Container(
                margin: const EdgeInsets.all(16),
                child: Card(
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          '💭 Start a Memory',
                          style: TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 16),
                        
                        // Toggle buttons
                        Row(
                          children: [
                            Expanded(
                              child: ElevatedButton.icon(
                                onPressed: () => setState(() => _showTextInput = true),
                                icon: const Icon(Icons.edit),
                                label: const Text('Write Text'),
                                style: ElevatedButton.styleFrom(
                                  backgroundColor: _showTextInput 
                                      ? Theme.of(context).primaryColor 
                                      : Colors.grey.shade300,
                                  foregroundColor: _showTextInput 
                                      ? Colors.white 
                                      : Colors.black54,
                                ),
                              ),
                            ),
                            const SizedBox(width: 8),
                            Expanded(
                              child: ElevatedButton.icon(
                                onPressed: () => setState(() => _showTextInput = false),
                                icon: const Icon(Icons.upload_file),
                                label: const Text('Upload File'),
                                style: ElevatedButton.styleFrom(
                                  backgroundColor: !_showTextInput 
                                      ? Theme.of(context).primaryColor 
                                      : Colors.grey.shade300,
                                  foregroundColor: !_showTextInput 
                                      ? Colors.white 
                                      : Colors.black54,
                                ),
                              ),
                            ),
                          ],
                        ),
                        
                        const SizedBox(height: 16),
                        
                        // Content based on selection
                        if (_showTextInput) ...[
                          TextField(
                            controller: _textController,
                            maxLines: 4,
                            decoration: const InputDecoration(
                              labelText: 'Enter your thoughts or fragments',
                              hintText: 'Type your thoughts here...',
                              border: OutlineInputBorder(),
                            ),
                          ),
                          const SizedBox(height: 12),
                          TextField(
                            controller: _sessionController,
                            decoration: const InputDecoration(
                              labelText: 'Session Name (optional)',
                              hintText: 'e.g., Morning thoughts, Work notes',
                              border: OutlineInputBorder(),
                            ),
                          ),
                          const SizedBox(height: 16),
                          SizedBox(
                            width: double.infinity,
                            child: ElevatedButton(
                              onPressed: state.isLoading
                                  ? null
                                  : () async {
                                      await state.addTextFragments(
                                        _textController.text,
                                        sessionName: _sessionController.text.isEmpty
                                            ? null
                                            : _sessionController.text,
                                      );
                                      _textController.clear();
                                    },
                              child: state.isLoading
                                  ? const CircularProgressIndicator()
                                  : const Text('Extract Fragments'),
                            ),
                          ),
                        ] else ...[
                          const Text(
                            'Select a file to upload and extract fragments from:',
                            style: TextStyle(fontSize: 14, color: Colors.grey),
                          ),
                          const SizedBox(height: 16),
                          SizedBox(
                            width: double.infinity,
                            child: ElevatedButton.icon(
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
                              label: const Text('Select & Upload File'),
                            ),
                          ),
                        ],
                      ],
                    ),
                  ),
                ),
              ),

              // AI Chat Section
              Expanded(
                child: Container(
                  margin: const EdgeInsets.fromLTRB(16, 0, 16, 16),
                  child: Card(
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              const Text(
                                '🤖 AI Chat',
                                style: TextStyle(
                                  fontSize: 18,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                              if (state.chatMessages.isNotEmpty)
                                TextButton.icon(
                                  onPressed: state.clearChat,
                                  icon: const Icon(Icons.clear_all, size: 16),
                                  label: const Text('Clear'),
                                  style: TextButton.styleFrom(
                                    foregroundColor: Colors.grey,
                                  ),
                                ),
                            ],
                          ),
                          const SizedBox(height: 8),
                          const SizedBox(height: 16),
                          
                          // Chat Messages
                          Expanded(
                            child: state.chatMessages.isEmpty
                                ? const Center(
                                    child: Text(
                                      '👋 Start a conversation with your AI assistant!\n\nMake sure the vLLM server is running:\n./launch_vllm_server.sh',
                                      textAlign: TextAlign.center,
                                      style: TextStyle(
                                        fontSize: 16,
                                        color: Colors.grey,
                                      ),
                                    ),
                                  )
                                : ListView.builder(
                                    controller: _chatScrollController,
                                    itemCount: state.chatMessages.length,
                                    itemBuilder: (context, index) {
                                      final message = state.chatMessages[index];
                                      
                                      return Container(
                                        margin: const EdgeInsets.only(bottom: 12),
                                        child: Row(
                                          crossAxisAlignment: CrossAxisAlignment.start,
                                          children: [
                                            Container(
                                              width: 32,
                                              height: 32,
                                              decoration: BoxDecoration(
                                                color: message.isUser 
                                                    ? Colors.blue.shade100 
                                                    : Colors.green.shade100,
                                                borderRadius: BorderRadius.circular(16),
                                              ),
                                              child: Icon(
                                                message.isUser ? Icons.person : Icons.smart_toy,
                                                size: 18,
                                                color: message.isUser 
                                                    ? Colors.blue.shade700 
                                                    : Colors.green.shade700,
                                              ),
                                            ),
                                            const SizedBox(width: 12),
                                            Expanded(
                                              child: Column(
                                                crossAxisAlignment: CrossAxisAlignment.start,
                                                children: [
                                                  Text(
                                                    message.isUser ? 'You' : 'AI Assistant',
                                                    style: TextStyle(
                                                      fontWeight: FontWeight.bold,
                                                      fontSize: 12,
                                                      color: message.isUser 
                                                          ? Colors.blue.shade700 
                                                          : Colors.green.shade700,
                                                    ),
                                                  ),
                                                  const SizedBox(height: 4),
                                                  Container(
                                                    padding: const EdgeInsets.all(12),
                                                    decoration: BoxDecoration(
                                                      color: message.isUser 
                                                          ? Colors.blue.shade50 
                                                          : Colors.grey.shade50,
                                                      borderRadius: BorderRadius.circular(8),
                                                      border: Border.all(
                                                        color: message.isUser 
                                                            ? Colors.blue.shade200 
                                                            : Colors.grey.shade200,
                                                      ),
                                                    ),
                                                    child: Text(
                                                      message.content,
                                                      style: const TextStyle(fontSize: 14),
                                                    ),
                                                  ),
                                                  const SizedBox(height: 4),
                                                  Text(
                                                    message.timestamp.toLocal().toString().split('.')[0],
                                                    style: const TextStyle(
                                                      fontSize: 10,
                                                      color: Colors.grey,
                                                    ),
                                                  ),
                                                ],
                                              ),
                                            ),
                                          ],
                                        ),
                                      );
                                    },
                                ),
                          ),
                          
                          // Chat Input
                          const SizedBox(height: 16),
                          Row(
                            children: [
                              Expanded(
                                child: TextField(
                                  controller: _chatController,
                                  decoration: const InputDecoration(
                                    hintText: 'Type your message...',
                                    border: OutlineInputBorder(),
                                    contentPadding: EdgeInsets.symmetric(
                                      horizontal: 12,
                                      vertical: 8,
                                    ),
                                  ),
                                  onSubmitted: (value) async {
                                    if (value.trim().isNotEmpty && !state.isChatLoading) {
                                      await state.sendChatMessage(value);
                                      _chatController.clear();
                                    }
                                  },
                                ),
                              ),
                              const SizedBox(width: 8),
                              ElevatedButton(
                                onPressed: state.isChatLoading || _chatController.text.trim().isEmpty
                                    ? null
                                    : () async {
                                        await state.sendChatMessage(_chatController.text);
                                        _chatController.clear();
                                      },
                                child: state.isChatLoading
                                    ? const SizedBox(
                                        width: 16,
                                        height: 16,
                                        child: CircularProgressIndicator(strokeWidth: 2),
                                      )
                                    : const Icon(Icons.send),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              ),
            ],
          );
        },
      ),
    );
  }

  @override
  void dispose() {
    _textController.dispose();
    _sessionController.dispose();
    _chatController.dispose();
    _chatScrollController.dispose();
    super.dispose();
  }
} 