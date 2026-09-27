// Talks to the Hugging Face Space (Gradio HTTP API) that runs the NER model.
//
// How the Gradio API works:
//   1. (files only) POST /gradio_api/upload        -> ["<server path of the file>"]
//   2. POST /gradio_api/call/analyze {"data": [text, file]} -> {"event_id": "..."}
//   3. GET  /gradio_api/call/analyze/<event_id>    -> "event: complete\ndata: [text, pieces, counts]"
import 'dart:async';
import 'dart:convert';

import 'package:http/http.dart' as http;

const spaceUrl = 'https://yoshitha19-medical-ner.hf.space';

/// A run of the text, with its entity label (SYMPTOM, DRUG, DISEASE) or null for plain text.
class Piece {
  const Piece(this.text, this.label);
  final String text;
  final String? label;
}

class NerResult {
  const NerResult(this.text, this.pieces);
  final String text;
  final List<Piece> pieces;

  int count(String label) => pieces.where((p) => p.label == label).length;
}

class NerApi {
  static final _base = Uri.parse('$spaceUrl/gradio_api/');
  static const _timeout = Duration(minutes: 3); // a sleeping Space can take a while to wake up

  /// Analyze typed text, or a file (txt, pdf, docx, png, jpg) given as bytes.
  static Future<NerResult> analyze({String text = '', List<int>? fileBytes, String? fileName}) async {
    try {
      Map<String, dynamic>? file;
      if (fileBytes != null) {
        final upload = http.MultipartRequest('POST', _base.resolve('upload'))
          ..files.add(http.MultipartFile.fromBytes('files', fileBytes, filename: fileName ?? 'file'));
        final res = await http.Response.fromStream(await upload.send()).timeout(_timeout);
        _check(res);
        final serverPath = (jsonDecode(res.body) as List).first as String;
        file = {'path': serverPath, 'meta': {'_type': 'gradio.FileData'}};
      }

      final start = await http
          .post(_base.resolve('call/analyze'),
              headers: {'Content-Type': 'application/json'}, body: jsonEncode({'data': [text, file]}))
          .timeout(_timeout);
      _check(start);
      final eventId = jsonDecode(start.body)['event_id'] as String;

      final result = await http.get(_base.resolve('call/analyze/$eventId')).timeout(_timeout);
      _check(result);
      return _parseStream(result.body);
    } on TimeoutException {
      throw Exception('The server took too long. Please try again.');
    } on FormatException {
      // An HTML page instead of JSON usually means the Space is asleep or restarting
      throw Exception('The model server is waking up. Try again in a minute.');
    }
  }

  static void _check(http.Response res) {
    if (res.statusCode == 200) return;
    if (res.statusCode == 503) throw Exception('The model server is waking up. Try again in a minute.');
    throw Exception('Server error (${res.statusCode}). Please try again.');
  }

  /// The result arrives as a stream of "event: ..." / "data: ..." lines.
  static NerResult _parseStream(String body) {
    String? event;
    for (final line in const LineSplitter().convert(body)) {
      if (line.startsWith('event:')) {
        event = line.substring(6).trim();
      } else if (line.startsWith('data:') && (event == 'complete' || event == 'error')) {
        final data = jsonDecode(line.substring(5).trim());
        if (event == 'error') {
          final message = data is Map ? data['error'] : null;
          throw Exception(message ?? 'The server returned an error.');
        }
        return _toResult(data as List);
      }
    }
    throw Exception('No result from the server. Please try again.');
  }

  static NerResult _toResult(List data) {
    final pieces = [
      for (final p in data[1] as List) Piece(p['token'] as String, p['class_or_confidence'] as String?),
    ];
    return NerResult(data[0] as String, pieces);
  }
}