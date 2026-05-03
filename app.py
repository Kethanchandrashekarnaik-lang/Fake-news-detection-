from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
import os
from config import Config
from database import init_db, save_prediction, get_history, get_prediction_by_id
from scraper.scraper import get_scraper
from utils.pdf_generator import generate_pdf_report

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize DB (creates file if not exists)
    if not os.path.exists(os.path.dirname(Config.DATABASE_PATH)) and os.path.dirname(Config.DATABASE_PATH):
        os.makedirs(os.path.dirname(Config.DATABASE_PATH), exist_ok=True)
    init_db()

    # No static model loading needed (Dynamic AI logic used instead)

    @app.route('/')
    def home():
        return render_template('home.html')

    @app.route('/analyze')
    def analyze_page():
        return render_template('input.html')

    @app.route('/history')
    def history_page():
        logs = get_history(limit=50)
        return render_template('history.html', history=logs)

    @app.route('/result/<int:pred_id>')
    def result_page(pred_id):
        data = get_prediction_by_id(pred_id)
        if not data:
            return "Result not found", 404
        
        # Parse JSON fields if they are strings (sqlite stores them as text)
        import json
        try:
            data['sources'] = json.loads(data['sources_json'])
            data['keywords'] = json.loads(data['keywords_json'])
        except:
            data['sources'] = []
            data['keywords'] = []
            
        return render_template('result.html', data=data)

    @app.route('/api/predict', methods=['POST'])
    def predict_api():
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No input data provided'}), 400

        text = data.get('text', '').strip()
        url = data.get('url', '').strip()

        source_url = None

        if url:
            scraper = get_scraper()
            scrape_data = scraper.scrape_article(url)
            if scrape_data.get('error'):
                return jsonify({'error': scrape_data['error']}), 400
            text = scrape_data['text']
            source_url = url
            
        if not text:
            return jsonify({'error': 'No text provided or scraped.'}), 400
            
        if len(text) > Config.MAX_INPUT_LENGTH:
            text = text[:Config.MAX_INPUT_LENGTH] # Truncate

        # Get verifier
        from model.verifier import get_verifier
        verifier = get_verifier()
        
        # Analyze
        result = verifier.search_and_verify(url if url else text)
        
        if result.get('error'):
            return jsonify({'error': result['error']}), 500

        # Save to DB
        import json
        pred_id = save_prediction(
            input_text=result.get('original_text', text),
            source_url=result.get('source_url', url),
            prediction=result['prediction'],
            confidence=result['confidence'],
            explanation=result['explanation'],
            sources_json=json.dumps(result['sources']),
            keywords_json=json.dumps(result['highlighted_keywords'])
        )
        
        result['prediction_id'] = pred_id
        return jsonify(result)

    @app.route('/export/<int:pred_id>')
    def export_pdf(pred_id):
        pred_data = get_prediction_by_id(pred_id)
        if not pred_data:
            return "Report not found", 404
            
        # Ensure temp dir exists
        temp_dir = os.path.join(Config.DATABASE_PATH.replace('database.db', ''), 'temp')
        os.makedirs(temp_dir, exist_ok=True)
        pdf_path = os.path.join(temp_dir, f'report_{pred_id}.pdf')
        
        generate_pdf_report(pred_data, pdf_path)
        
        return send_file(pdf_path, as_attachment=True, download_name=f'TruthLens_Report_{pred_id}.pdf')

    return app

if __name__ == "__main__":
    app = create_app()
    # It's best practice on windows with waitress to run it: pip install waitress
    from waitress import serve
    print("Starting server on http://127.0.0.1:5000 ...")
    serve(app, host='127.0.0.1', port=5000, threads=4)