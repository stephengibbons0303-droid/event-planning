from flask import Flask, render_template_string, request, jsonify
from crew import run_crew

app = Flask(__name__)

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Aura Events - Multi-Agent Planner</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Inter', sans-serif; background: #1a1a1a; color: #fff; display: flex; min-height: 100vh; }
        
        .sidebar { width: 80px; background: #111; display: flex; flex-direction: column; align-items: center; padding: 20px 0; border-right: 1px solid #2a2a2a; }
        .logo { width: 45px; height: 45px; background: linear-gradient(135deg, #c9a962, #a08339); border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 24px; font-weight: 600; color: #111; margin-bottom: 40px; }
        .nav-item { width: 50px; height: 50px; display: flex; flex-direction: column; align-items: center; justify-content: center; margin: 10px 0; cursor: pointer; border-radius: 12px; transition: all 0.2s; color: #666; font-size: 10px; }
        .nav-item:hover, .nav-item.active { background: #2a2a2a; color: #c9a962; }
        .nav-item svg { width: 22px; height: 22px; margin-bottom: 4px; }
        
        .main { flex: 1; display: flex; }
        .content { flex: 1; padding: 30px; }
        
        .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; }
        .header h1 { font-size: 24px; font-weight: 500; color: #c9a962; }
        
        .form-card { background: #242424; border-radius: 16px; padding: 30px; max-width: 500px; }
        .form-card h2 { font-size: 18px; font-weight: 500; margin-bottom: 25px; color: #fff; }
        .form-row { display: flex; gap: 15px; margin-bottom: 15px; }
        .form-row.single { display: block; }
        input, select { flex: 1; background: #1a1a1a; border: 1px solid #333; color: #fff; padding: 14px 16px; border-radius: 10px; font-size: 14px; outline: none; width: 100%; }
        input::placeholder { color: #666; }
        input:focus, select:focus { border-color: #c9a962; }
        select option { background: #1a1a1a; }
        
        .agents-section { margin-top: 25px; }
        .agents-section h3 { font-size: 14px; color: #888; margin-bottom: 15px; }
        .agents { display: flex; gap: 10px; }
        .agent { width: 45px; height: 45px; border-radius: 50%; background: #333; display: flex; align-items: center; justify-content: center; font-size: 18px; border: 2px solid #c9a962; }
        
        .submit-btn { width: 100%; background: #c9a962; color: #111; border: none; padding: 16px; border-radius: 10px; font-size: 16px; font-weight: 600; cursor: pointer; margin-top: 25px; }
        .submit-btn:hover { background: #d4b56d; }
        .submit-btn:disabled { background: #555; color: #888; cursor: not-allowed; }
        
        .right-panel { width: 320px; background: #111; padding: 30px; border-left: 1px solid #2a2a2a; }
        .panel-section { margin-bottom: 30px; }
        .panel-section h3 { font-size: 14px; color: #888; margin-bottom: 15px; }
        .event-image { width: 100%; height: 150px; border-radius: 12px; background: #2a2a2a; object-fit: cover; }
        
        .results { margin-top: 20px; }
        .result-card { background: #1a1a1a; border-left: 3px solid #c9a962; padding: 20px; border-radius: 0 12px 12px 0; margin-bottom: 15px; }
        .result-card h4 { color: #c9a962; margin-bottom: 12px; }
        .result-card p { color: #aaa; font-size: 14px; line-height: 1.6; margin: 6px 0; }
        .result-card .label { color: #fff; font-weight: 500; }
        .status-badge { display: inline-block; background: rgba(201,169,98,0.2); color: #c9a962; padding: 4px 12px; border-radius: 20px; font-size: 12px; }
        
        .loading { text-align: center; padding: 40px; }
        .spinner { width: 40px; height: 40px; border: 3px solid #333; border-top-color: #c9a962; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 20px; }
        @keyframes spin { to { transform: rotate(360deg); } }
        .loading p { color: #888; }
        
        .error { border-left-color: #e74c3c; }
        .error h4 { color: #e74c3c; }
        
        @media (max-width: 900px) {
            .right-panel { display: none; }
            .sidebar { width: 60px; }
        }
    </style>
</head>
<body>
    <nav class="sidebar">
        <div class="logo">A</div>
        <div class="nav-item active">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"></path></svg>
            Projects
        </div>
        <div class="nav-item">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"></path></svg>
            Clients
        </div>
        <div class="nav-item">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
            Budget
        </div>
    </nav>
    
    <main class="main">
        <div class="content">
            <div class="header">
                <h1>Aura Events - Multi-Agent Planner</h1>
            </div>
            
            <div class="form-card">
                <h2>Create New Event</h2>
                <form id="eventForm">
                    <div class="form-row single">
                        <input name="event_topic" placeholder="Event Topic (e.g., Wedding, Conference)" required>
                    </div>
                    <div class="form-row single">
                        <input name="event_city" placeholder="City" required>
                    </div>
                    <div class="form-row">
                        <input name="tentative_date" type="date" required>
                        <input name="expected_participants" type="number" placeholder="Participants" required>
                    </div>
                    <div class="form-row">
                        <select name="age_group" required>
                            <option value="" disabled selected>Select Age Group</option>
                            <option value="children">Children (under 12)</option>
                            <option value="teens">Teens (13-17)</option>
                            <option value="young adults">Young Adults (18-30)</option>
                            <option value="adults">Adults (31-50)</option>
                            <option value="seniors">Seniors (50+)</option>
                            <option value="mixed">Mixed Ages</option>
                        </select>
                        <input name="budget" type="number" placeholder="Budget ($)" required>
                    </div>
                    
                    <div class="agents-section">
                        <h3>Assigned Agents:</h3>
                        <div class="agents">
                            <div class="agent" title="Venue Coordinator">📍</div>
                            <div class="agent" title="Logistics Manager">📦</div>
                            <div class="agent" title="Marketing Agent">📢</div>
                        </div>
                    </div>
                    
                    <button type="submit" class="submit-btn" id="submitBtn">Plan Event</button>
                </form>
                
                <div id="result" class="results"></div>
            </div>
        </div>
        
        <aside class="right-panel">
            <div class="panel-section">
                <h3>Event Setups</h3>
                <img class="event-image" src="https://images.unsplash.com/photo-1519167758481-83f550bb49b3?w=400&h=200&fit=crop" alt="Event">
            </div>
            <div class="panel-section">
                <h3>Status</h3>
                <p style="color:#666;font-size:13px;">3 AI agents ready</p>
            </div>
        </aside>
    </main>
    
    <script>
        var form = document.getElementById('eventForm');
        var btn = document.getElementById('submitBtn');
        var resultDiv = document.getElementById('result');
        
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            btn.disabled = true;
            btn.textContent = 'Planning...';
            resultDiv.innerHTML = '<div class="loading"><div class="spinner"></div><p>AI agents working...</p></div>';
            
            var formData = new FormData(form);
            var data = {};
            formData.forEach(function(value, key) {
                data[key] = value;
            });
            
            fetch('/run', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            })
            .then(function(res) { return res.json(); })
            .then(function(json) {
                var html = '';
                
                if (json.error) {
                    html = '<div class="result-card error"><h4>Error</h4><p>' + json.error + '</p></div>';
                } else {
                    if (json.venue) {
                        html += '<div class="result-card"><h4>📍 Venue</h4>';
                        html += '<p><span class="label">Name:</span> ' + json.venue.name + '</p>';
                        html += '<p><span class="label">Address:</span> ' + json.venue.address + '</p>';
                        html += '<p><span class="label">Capacity:</span> ' + json.venue.capacity + ' guests</p>';
                        html += '<p><span class="label">Status:</span> <span class="status-badge">' + json.venue.booking_status + '</span></p>';
                        html += '</div>';
                    }
                    
                    if (json.logistics) {
                        html += '<div class="result-card"><h4>📦 Logistics</h4><p>' + json.logistics + '</p></div>';
                    }
                    
                    if (json.marketing) {
                        html += '<div class="result-card"><h4>📢 Marketing</h4><p>' + json.marketing + '</p></div>';
                    }
                    
                    if (json.raw) {
                        html += '<div class="result-card"><h4>📋 Results</h4><p>' + json.raw + '</p></div>';
                    }
                    
                    if (!html) {
                        html = '<div class="result-card"><h4>📋 Results</h4><p>No results returned</p></div>';
                    }
                }
                
                resultDiv.innerHTML = html;
                btn.disabled = false;
                btn.textContent = 'Plan Event';
            })
            .catch(function(err) {
                resultDiv.innerHTML = '<div class="result-card error"><h4>Error</h4><p>' + err.message + '</p></div>';
                btn.disabled = false;
                btn.textContent = 'Plan Event';
            });
        });
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HTML)

@app.route('/run', methods=['POST'])
def run():
    try:
        data = request.json
        data['expected_participants'] = int(data['expected_participants'])
        data['budget'] = int(data['budget'])
        data['event_description'] = data['event_topic'] + ' for ' + data['age_group']
        
        result = run_crew(data)
        
        response = {}
        
        if hasattr(result, 'tasks_output'):
            for task_output in result.tasks_output:
                output_str = str(task_output)
                desc = task_output.description.lower()
                if 'venue' in desc:
                    try:
                        import json
                        import re
                        match = re.search(r'\{[^{}]*name[^{}]*\}', output_str)
                        if match:
                            response['venue'] = json.loads(match.group())
                    except:
                        pass
                elif 'catering' in desc or 'logistics' in desc:
                    response['logistics'] = output_str
                elif 'market' in desc or 'promot' in desc:
                    response['marketing'] = output_str
        else:
            response['raw'] = str(result)
            
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
