import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';

import 'ner_api.dart';

void main() => runApp(const MedicalNerApp());

const labelColors = {
  'SYMPTOM': Color(0xFFFDE68A), // yellow
  'DRUG': Color(0xFF93C5FD), // blue
  'DISEASE': Color(0xFFFCA5A5), // red
};

class MedicalNerApp extends StatelessWidget {
  const MedicalNerApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'NER in Medical Records',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(colorSchemeSeed: const Color(0xFF0D9488), useMaterial3: true),
      home: const HomePage(),
    );
  }
}

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  final _controller = TextEditingController();
  NerResult? _result;
  String? _error;
  bool _loading = false;

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  Future<void> _run(Future<NerResult> Function() call) async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final result = await call();
      setState(() {
        _result = result;
        _controller.text = result.text; // shows the text read from an uploaded file
      });
    } catch (e) {
      setState(() {
        _result = null; // don't leave an old result under a new error
        _error = e.toString().replaceFirst('Exception: ', '');
      });
    } finally {
      setState(() => _loading = false);
    }
  }

  void _analyzeText() {
    if (_controller.text.trim().isEmpty) return;
    FocusScope.of(context).unfocus();
    _run(() => NerApi.analyze(text: _controller.text));
  }

  Future<void> _pickFile() async {
    final file = await FilePicker.pickFile(
      type: FileType.custom,
      allowedExtensions: ['txt', 'pdf', 'docx', 'png', 'jpg', 'jpeg'],
    );
    if (file == null) return;
    final bytes = await file.readAsBytes();
    _run(() => NerApi.analyze(fileBytes: bytes, fileName: file.name));
  }

  Future<void> _takePhoto() async {
    XFile? photo;
    try {
      photo = await ImagePicker().pickImage(source: ImageSource.camera, imageQuality: 85);
    } catch (_) {
      setState(() => _error = 'Camera is not available on this device. Use Upload file instead.');
      return;
    }
    if (photo == null) return;
    final bytes = await photo.readAsBytes();
    _run(() => NerApi.analyze(fileBytes: bytes, fileName: 'photo.jpg'));
  }

  void _clear() {
    setState(() {
      _controller.clear();
      _result = null;
      _error = null;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          image: DecorationImage(
            image: AssetImage('assets/background.webp'),
            fit: BoxFit.cover,
            // White layer at 80% on top of the photo makes it light, like the website
            colorFilter: ColorFilter.mode(Color(0xCCFFFFFF), BlendMode.srcOver),
          ),
        ),
        child: SafeArea(
          child: Center(
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 860),
              child: ListView(
                padding: const EdgeInsets.all(16),
                children: [
                  const Text(
                    '🩺 NER in Medical Records',
                    style: TextStyle(fontSize: 26, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 16),
                  TextField(
                    controller: _controller,
                    minLines: 6,
                    maxLines: 12,
                    decoration: const InputDecoration(
                      hintText: 'Type or paste a clinical note...',
                      filled: true,
                      fillColor: Colors.white,
                      border: OutlineInputBorder(),
                    ),
                  ),
                  const SizedBox(height: 12),
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: [
                      FilledButton(
                        style: FilledButton.styleFrom(backgroundColor: const Color(0xFF0D9488)),
                        onPressed: _loading ? null : _analyzeText,
                        child: const Text('Analyze'),
                      ),
                      OutlinedButton.icon(
                        onPressed: _loading ? null : _pickFile,
                        icon: const Icon(Icons.upload_file),
                        label: const Text('Upload file'),
                      ),
                      OutlinedButton.icon(
                        onPressed: _loading ? null : _takePhoto,
                        icon: const Icon(Icons.photo_camera),
                        label: const Text('Camera'),
                      ),
                      FilledButton(
                        style: FilledButton.styleFrom(backgroundColor: const Color(0xFFE11D48)),
                        onPressed: _loading ? null : _clear,
                        child: const Text('Clear'),
                      ),
                    ],
                  ),
                  if (_loading) ...[
                    const SizedBox(height: 16),
                    const LinearProgressIndicator(),
                    const SizedBox(height: 6),
                    const Text('Analyzing... the first request can take up to a minute.'),
                  ],
                  if (_error != null)
                    Padding(
                      padding: const EdgeInsets.only(top: 16),
                      child: Text(_error!, style: const TextStyle(color: Color(0xFFDC2626))),
                    ),
                  if (_result != null) ...[
                    const SizedBox(height: 16),
                    Wrap(
                      spacing: 8,
                      runSpacing: 8,
                      children: [
                        for (final entry in labelColors.entries)
                          Chip(
                            label: Text('${entry.key} (${_result!.count(entry.key)})'),
                            backgroundColor: entry.value,
                            side: BorderSide.none,
                          ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Card(
                      color: Colors.white,
                      child: Padding(
                        padding: const EdgeInsets.all(16),
                        child: HighlightedText(result: _result!),
                      ),
                    ),
                  ],
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}

/// Shows the text with each entity on its colour. Negated entities come back unlabelled,
/// so they stay plain text.
class HighlightedText extends StatelessWidget {
  const HighlightedText({super.key, required this.result});

  final NerResult result;

  @override
  Widget build(BuildContext context) {
    return SelectableText.rich(
      TextSpan(
        style: const TextStyle(fontSize: 16, height: 1.8, color: Colors.black87),
        children: [
          for (final piece in result.pieces)
            TextSpan(
              text: piece.text,
              style: piece.label == null
                  ? null
                  : TextStyle(backgroundColor: labelColors[piece.label], fontWeight: FontWeight.w500),
            ),
        ],
      ),
    );
  }
}