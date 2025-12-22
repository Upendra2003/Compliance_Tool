from flask import Flask, render_template, request, jsonify, send_file, Response, session
import json
from datetime import datetime
from io import BytesIO
from utils.policies import get_policy
from checker import run_all_checks_with_progress
from utils.utils import get_policy_doc
from utils.pdf_generator import generate_compliance_pdf
from scorer import calculate_compliance_score
import secrets
import threading

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Store for progress updates
progress_store = {}
# Lock for thread-safe access to progress_store
progress_lock = threading.Lock()

@app.route("/")
def hello_world():
    return render_template('index.html')

@app.route("/report")
def report():
    """Serve the report page - data will be loaded from sessionStorage"""
    return render_template('report.html')

@app.route("/send_number", methods=['POST'])
def send_number():
    data = request.get_json()
    policy_id = data.get('number')

    # Generate a session ID for progress tracking
    session_id = secrets.token_hex(8)
    session['check_session_id'] = session_id

    with progress_lock:
        progress_store[session_id] = []

    print(f"\n=== Created session {session_id} for policy {policy_id} ===")

    # Return session ID immediately so frontend can start listening to progress
    return jsonify({"session_id": session_id, "policy_id": policy_id})

@app.route("/progress/<session_id>")
def progress_stream(session_id):
    """Server-Sent Events endpoint for progress updates"""
    def generate():
        import time

        print(f"SSE: Client connected to session {session_id}")

        # Send initial connection message
        yield f"data: {json.dumps({'type': 'connected', 'data': {'message': 'Connected to progress stream'}})}\n\n"

        last_index = 0
        max_wait = 3000  # Maximum 300 seconds (5 minutes) with 0.1s sleep
        wait_count = 0
        no_update_count = 0

        while wait_count < max_wait:
            with progress_lock:
                if session_id in progress_store:
                    updates = progress_store[session_id][last_index:]

                    if updates:
                        no_update_count = 0
                        for update in updates:
                            print(f"SSE: Sending update: {update['type']}")
                            yield f"data: {json.dumps(update)}\n\n"
                            last_index += 1

                            # Check if this is the final update
                            if update.get('type') == 'complete':
                                print(f"SSE: Session {session_id} complete, closing stream")
                                return
                    else:
                        no_update_count += 1

            time.sleep(0.1)
            wait_count += 1

            # Send keepalive every 5 seconds
            if wait_count % 50 == 0:
                yield f": keepalive\n\n"

        print(f"SSE: Session {session_id} timeout after {wait_count * 0.1}s")
        yield f"data: {json.dumps({'type': 'error', 'data': {'message': 'Session timeout'}})}\n\n"

    return Response(generate(), mimetype='text/event-stream', headers={
        'Cache-Control': 'no-cache',
        'X-Accel-Buffering': 'no'
    })

@app.route("/run_checks", methods=['POST'])
def run_checks():
    """Actually run the compliance checks in background thread"""
    data = request.get_json()
    session_id = data.get('session_id')
    policy_id = data.get('policy_id')

    print(f"\n=== DEBUG: Starting compliance check for policy ID: {policy_id}, session: {session_id} ===")

    def run_checks_background():
        """Background task to run checks"""
        def progress_callback(message_type, msg_data):
            """Thread-safe callback to store progress updates"""
            with progress_lock:
                if session_id in progress_store:
                    update = {
                        'type': message_type,
                        'data': msg_data
                    }
                    progress_store[session_id].append(update)
                    print(f"PROGRESS: Added {message_type} update to session {session_id}")

        try:
            policy_url = get_policy(policy_id)
            print(f"DEBUG: Retrieved policy URL: {policy_url}")

            policy_doc = get_policy_doc(policy_id, policy_url)
            print(f"DEBUG: Loaded policy document for: {policy_doc.get('provider')}")

            # Run all compliance checks with progress callback
            print("DEBUG: Running all compliance checks...")
            check_results = run_all_checks_with_progress(policy_doc, progress_callback)
            print(f"DEBUG: Completed {len(check_results)} checks")

            # Calculate scores from check results (ALL CALCULATION IN BACKEND)
            print("DEBUG: Calculating compliance scores...")
            progress_callback('status', {'message': 'Calculating final scores...'})
            scoring_report = calculate_compliance_score(check_results)
            print(f"DEBUG: Overall score: {scoring_report['overall']['score']}")
            print(f"DEBUG: Grade: {scoring_report['overall']['grade']}")
            print("=== DEBUG: Processing complete ===\n")

            # Send completion with scoring data
            progress_callback('complete', {
                'scoring_data': scoring_report,
                'provider': policy_id
            })

        except Exception as e:
            print(f"ERROR in background task: {str(e)}")
            import traceback
            traceback.print_exc()
            with progress_lock:
                if session_id in progress_store:
                    progress_store[session_id].append({
                        'type': 'error',
                        'data': {'message': f'Processing error: {str(e)}'}
                    })

    # Start background thread
    thread = threading.Thread(target=run_checks_background)
    thread.daemon = True
    thread.start()

    print(f"DEBUG: Background thread started for session {session_id}")

    return jsonify({"status": "started"})

@app.route("/download_pdf", methods=['POST'])
def download_pdf():
    data = request.get_json()
    provider = data.get('provider', 'Unknown')
    scoring_data = data.get('scoring_data', {})

    # Convert scoring data back to results format for PDF generator
    # (PDF generator still uses old format)
    results = []
    for category in scoring_data.get('categories', []):
        if category.get('implemented'):
            for check in category.get('breakdown', []):
                results.append({
                    'group': category['category'].lower().replace(' & ', '_').replace(' ', '_'),
                    'id': check['id'],
                    'section': category['category'],
                    'description': check['label'],
                    'passed': check['passed'],
                    'message': check['message']
                })

    # Generate PDF
    pdf_data = generate_compliance_pdf(results, provider)

    # Create filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{provider}_dpdp_compliance_report_{timestamp}.pdf"

    # Send PDF as response
    return send_file(
        BytesIO(pdf_data),
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename
    )

if __name__=='__main__':
    app.run(debug=True, use_reloader=True)