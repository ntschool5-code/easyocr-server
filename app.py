from flask import Flask, request, jsonify
import easyocr
import base64
import io
import numpy as np
from PIL import Image
import os

app = Flask(__name__)

# Language map
LANG_MAP = {
    'eng': 'en',
    'hin': 'hi',
    'tel': 'te',
    'tam': 'ta',
    'kan': 'kn',
    'en': 'en',
    'hi': 'hi',
    'te': 'te',
}

readers = {}

def get_reader(langs):
    key = ','.join(sorted(langs))
    if key not in readers:
        readers[key] = easyocr.Reader(langs, gpu=False)
    return readers[key]

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'service': 'EasyOCR'})

@app.route('/ocr', methods=['POST'])
def ocr():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON body'}), 400

        image_base64 = data.get('image')
        raw_langs = data.get('languages', ['en'])

        if not image_base64:
            return jsonify({'error': 'No image provided'}), 400

        # Convert language codes
        langs = list(set(LANG_MAP.get(l, 'en') for l in raw_langs))
        if not langs:
            langs = ['en']

        # Decode image
        image_bytes = base64.b64decode(image_base64)
        image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        image_array = np.array(image)

        # Run OCR
        reader = get_reader(langs)
        results = reader.readtext(image_array, detail=1)

        # Build response
        full_text = '\n'.join([r[1] for r in results])
        blocks = [
            {
                'text': r[1],
                'confidence': float(r[2]),
                'bbox': r[0]
            }
            for r in results
        ]

        return jsonify({
            'text': full_text,
            'blocks': blocks,
            'languages': langs
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=False)
