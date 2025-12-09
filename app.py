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
        
        /* Sidebar */
        .sidebar { width: 80px; background: #111; display: flex; flex-direction: column; align-items: center; padding: 20px 0; border-right: 1px solid #2a2a2a; }
        .logo { width: 45px; height: 45px; background: linear-gradient(135deg, #c9a962, #a08339); border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 24px; font-weight: 600; color: #111; margin-bottom: 40px; }
        .nav-item { width: 50px; height: 50px; display: flex; flex-direction: column; align-items: center; justify-content: center; margin: 10px 0; cursor: pointer; border-radius: 12px; transition: all 0.2s; color: #666; font-size: 10px; }
        .nav-item:hover, .nav-item.active { background: #2a2a2a; color: #c9a962; }
        .nav-item svg { width: 22px; height: 22px; margin-bottom: 4px; }
        .nav-bottom { margin-top: auto; }
        .add-btn { width: 45px; height: 45px; background: #c9a962; border-radius: 50%; display: flex; align-items: center; justify-content: center; cursor: pointer; }
        .add-btn svg { width: 20px; height: 20px; color: #111; }
        
        /* Main Content */
        .main { flex: 1; display: flex; }
        .content { flex: 1; padding: 30px; }
        
        /* Header */
        .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; }
        .header h1 { font-size: 24px; font-weight: 500; color: #c9a962; }
        .create-btn { background: #c9a962; color: #111; border: none; padding: 12px 24px; border-radius: 8px; font-weight: 500; cursor: pointer; display: flex; align-items: center; gap: 8px; }
        .create-btn:hover { background: #d4b56d; }
        
        /* Form Card */
        .form-card { background: #242424; border-radius: 16px; padding: 30px; max-width: 500px; }
        .form-card h2 { font-size: 18px; font-weight: 500; margin-bottom: 25px; color: #fff; }
        .form-row { display: flex; gap: 15px; margin-bottom: 15px; }
        .form-row.single { display: block; }
        input, select { flex: 1; background: #1a1a1a; border: 1px solid #333; color: #fff; padding: 14px 16px; border-radius: 10px; font-size: 14px; outline: none; transition: border 0.2s; }
        input::placeholder { color: #666; }
        input:focus, select:focus { border-color: #c9a962; }
        select { cursor: pointer; }
        select option { background: #1a1a1a; }
        
        /* Agents */
        .agents-section { margin-top: 25px; }
        .agents-section h3 { font-size: 14px; color: #888; margin-bottom: 15px; }
        .agents { display: flex; gap: 10px; }
        .agent { width: 45px; height: 45px; border-radius: 50%; background: #333; display: flex; align-items: center; justify-content: center; font-size: 18px; border: 2px solid transparent; transition: all 0.2s; }
        .agent.active { border-color: #c9a962; }
        .agent:hover { transform: scale(1.1); }
        
        /* Submit */
        .submit-btn { width: 100%; background: #c9a962; color: #111; border: none; padding: 16px; border-radius: 10px; font-size: 16px; font-weight: 600; cursor: pointer; margin-top: 25px; transition: all 0.2s; }
        .submit-btn:hover { background: #d4b56d; }
        .submit-btn:disabled { background: #555; color: #888; cursor: not-allowed; }
        
        /* Right Panel */
        .right-panel { width: 320px; background: #111; padding: 30px; border-left: 1px solid #2a2a2a; }
        .panel-section { margin-bottom: 30px; }
        .panel-section h3 { font-size: 14px; color: #888; margin-bottom: 15px; }
        .event-image { width: 100%; height: 150px; border-radius: 12px; background: linear-gradient(135deg, #2a2a2a, #1a1a1a); object-fit: cover; }
        
        /* Activity */
        .activity-item { display: flex; align-items: flex-start; gap: 12px; padding: 12px 0; border-bottom: 1px solid #2a2a2a; }
        .activity-icon { width: 32px; height: 32px; background: #2a2a2a; border-radius: 8px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
        .activity-icon svg { width: 16px; height: 16px; color: #c9a962; }
        .activity-text { font-size: 13px; }
        .activity-text strong { color: #fff; display: block; }
        .activity-text span { color: #666; font-size: 12px; }
        
        /* Results */
        .results { margin-top: 20px; }
        .result-card { background: #1a1a1a; border-left: 3px solid #c9a962; padding: 20px; border-radius: 0 12px 12px 0; margin-bottom: 15px; }
        .result-card h4 { color: #c9a962; margin-bottom: 12px; display: flex; align-items: center; gap: 8px; }
        .result-card p { color: #aaa; font-size: 14px; line-height: 1.6; margin: 6px 0; }
        .result-card .label { color: #fff; font-weight: 500; }
        .status-badge { display: inline-block; background: rgba(201,169,98,0.2); color: #c9a962; padding: 4px 12px; border-radius: 20px; font-size: 12px; }
        
        /* Loading */
        .loading { text-align: center; padding: 40px; }
        .spinner { width: 40px; height: 40px; border: 3px solid #333; border-top-color: #c9a962; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 20px; }
        @keyframes spin { to { transform: rotate(360deg); } }
        .loading p { color: #888; }
        
        /* Error */
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
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path></svg>
            Vendors
        </div>
        <div class="nav-item">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
            Budget
        </div>
        <div class="nav-bottom">
            <div class="add-btn">
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg>
            </div>
        </div>
    </nav>
    
    <main class="main">
        <div class="content">
            <div class="header">
                <h1>Aura Events - Multi-Agent Planner</h1>
                <button class="create-btn" onclick="document.getElementById('event_topic').focus()">
                    Create New Event
                    <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg>
                </button>
            </div>
            
            <div class="form-card">
                <h2>Create New Event</h2>
                <form id="form">
                    <div class="form-row single">
                        <input id="event_topic" name="event_topic" placeholder="Event Topic (e.g., Wedding, Conference)" required>
                    </div>
                    <div class="form-row single">
                        <input name="event_city" placeholder="City" required>
                    </div>
                    <div class="form-row">
                        <input name="tentative_date" type="date" required>
                        <input name="expected_participants" type="number" placeholder="Expected Participants" required>
                    </div>
                    <div class="form-row">
                        <select name="age_group" required>
                            <option value="" disabled selected>Select Age Group</option>
                            <option value="children (under 12)">Children (under 12)</option>
                            <option value="teens (13-17)">Teens (13-17)</option>
                            <option value="young adults (18-30)">Young Adults (18-30)</option>
                            <option value="adults (31-50)">Adults (31-50)</option>
                            <option value="seniors (50+)">Seniors (50+)</option>
                            <option value="mixed ages">Mixed Ages</option>
                        </select>
                        <input name="budget" type="number" placeholder="Budget ($)" required>
                    </div>
                    
                    <div class="agents-section">
                        <h3>Assigned Agents:</h3>
                        <div class="agents">
                            <div class="agent active" title="Venue Coordinator">📍</div>
                            <div class="agent active" title="Logistics Manager">📦</div>
                            <div class="agent active" title="Marketing Agent">📢</div>
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
                <img class="event-image" src="https://images.unsplash.com/photo-1519167758481-83f550bb49b3?w=400&h=200&fit=crop" alt="Event Setup">
            </div>
            
            <div class="panel-section">
                <h3>Recent Activity</h3>
                <div class="activity-item">
                    <div class="activity-icon">
                        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                    </div>
                    <div class="activity-text">
                        <strong>Ready to Plan</strong>
                        <span>3 AI agents standing by</span>
                    </div>
                </div>
                <div class="activity-item">
                    <div class="activity-icon">
                        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
                    </div>
                    <div class="activity-text">
                        <strong>Powered by CrewAI</strong>
                        <span>Multi-agent orchestration</span>
                    </div>
                </div>
            </div>
        </aside>
    </main>
    
    <script>
        document.getElementById('form').onsubmit = async (e) => {
            e.preventDefault();
            const btn = document.getElementById('submitBtn');
            const resultDiv = document.getElementById('result');
            
            btn.disabled = true;
            btn.textContent = 'Planning...';
            resultDiv.innerHTML = '<div class="loading"><div class="spinner"></div><p>AI agents are working...</p><p style="font-size:12px;margin-top:8px;">This may take 1-3 minutes</p></div>';
            
            const data = Object.fromEntries(new FormData(e.target));
            
            try {
                const res = await fetch('/run', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });
                const json = await res.json();
                
                if (json.error) {
                    resultDiv.innerHTML = '<div class="result-card error"><h4>⚠️ Error</h4><p>' + json.error + '</p></div>';
                } else {
                    let html = '';
                    
                    if (json.venue) {
                        html += '<div class="result-card"><h4>📍 Venue</h4>';
                        html += '<p><span class="label">Name:</span> ' + json.venue.name + '</p>';
                        html += '<p><span class="label">Address:</span> ' + json.venue.address + '</p>';
                        html += '<p><span class="label">Capacity:</span> ' + json.venue.capacity + ' guests</p>';
                        html += '<p><span class="label">Status:</span> <span class="status-badge">' + json.venue.booking_status + '</span></p>';
                        html += '</div>';
                    }
                    
                    if (json.logistics) {
                        html += '<div class="result-card"><h4>📦 Logistics</h4>';
                        html += '<p>' + json.logistics.split('\\n').join('<br>') + '</p></div>';
                    }
                    
                    if (json.marketing) {
                        html += '<div class="result-card"><h4>📢 Marketing</h4>';
                        html += '<p>' + json.marketing.split('\\n').join('<br>') + '</p></div>';
                    }
                    
                    if (json.raw) {
                        html += '<div class="result-card"><h4>📋 Results</h4>';
                        html += '<p>' + json.raw.split('\\n').join('<br>') + '</p></div>';
                    }
                    
                    if (!html) {
                        html = '<div class="result-card"><h4>📋 Results</h4><p>' + JSON.stringify(json, null, 2) + '</p></div>';
                    }
                    
                    resultDiv.innerHTML = html;
                }
            } catch (err) {
                resultDiv.innerHTML = '<div class="result-card error"><h4>⚠️ Error</h4><p>' + err.message + '</p></div>';
            }
            
            btn.disabled = false;
            btn.textContent = 'Plan Event';
        };
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
        data['event_description'] = f"{data['event_topic']} for {data['age_group']}"
        
        result = run_crew(data)
        
        response = {}
        
        if hasattr(result, 'tasks_output'):
            for task_output in result.tasks_output:
                output_str = str(task_output)
                if 'venue' in task_output.description.lower():
                    try:
                        import json
                        import re
                        json_match = re.search(r'\{[^{}]*"name"[^{}]*\}', output_str)
                        if json_match:
                            response['venue'] = json.loads(json_match.group().replace('\n', ''))
                    except:
                        pass
                elif 'catering' in task_output.description.lower() or 'logistics' in task_output.description.lower():
                    response['logistics'] = output_str
                elif 'market' in task_output.description.lower() or 'promot' in task_output.description.lower():
                    response['marketing'] = output_str
        else:
            result_str = str(result)
            import json
            import re
            json_match = re.search(r'\{[^{}]*"name"[^{}]*\}', result_str)
            if json_match:
                try:
                    response['venue'] = json.loads(json_match.group().replace('\n', ''))
                except:
                    response['raw'] = result_str
            else:
                response['raw'] = result_str
            
        return jsonify(response)
        
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
