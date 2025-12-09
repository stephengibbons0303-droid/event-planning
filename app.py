from flask import Flask, render_template_string, request, jsonify
from crew import run_crew

app = Flask(__name__)

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Event Planner AI</title>
    <style>
        body { font-family: Arial; max-width: 700px; margin: 50px auto; padding: 20px; background: #f5f5f5; }
        .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #333; margin-bottom: 30px; }
        input, select { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }
        button { background: #4CAF50; color: white; padding: 15px; border: none; width: 100%; cursor: pointer; border-radius: 5px; font-size: 16px; margin-top: 10px; }
        button:hover { background: #45a049; }
        button:disabled { background: #ccc; cursor: not-allowed; }
        #result { margin-top: 30px; }
        .card { background: #fff; border-left: 4px solid #4CAF50; padding: 20px; margin: 15px 0; border-radius: 5px; box-shadow: 0 1px 5px rgba(0,0,0,0.1); }
        .card h3 { margin: 0 0 15px 0; color: #333; }
        .card p { margin: 8px 0; color: #666; line-height: 1.6; }
        .card .label { font-weight: bold; color: #333; }
        .status { display: inline-block; padding: 5px 12px; border-radius: 15px; font-size: 12px; }
        .status.available { background: #e8f5e9; color: #2e7d32; }
        .loading { text-align: center; padding: 40px; color: #666; }
        .spinner { border: 4px solid #f3f3f3; border-top: 4px solid #4CAF50; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin: 0 auto 20px; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .error { background: #ffebee; border-left-color: #f44336; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎉 Event Planner AI</h1>
        <form id="form">
            <input name="event_topic" placeholder="Event Topic (e.g., Wedding, Conference)" required>
            <input name="event_city" placeholder="City" required>
            <input name="tentative_date" type="date" required>
            <input name="expected_participants" type="number" placeholder="Expected Participants" required>
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
            <button type="submit" id="submitBtn">Plan Event</button>
        </form>
        <div id="result"></div>
    </div>
    <script>
        document.getElementById('form').onsubmit = async (e) => {
            e.preventDefault();
            const btn = document.getElementById('submitBtn');
            const resultDiv = document.getElementById('result');
            
            btn.disabled = true;
            btn.textContent = 'Planning...';
            resultDiv.innerHTML = '<div class="loading"><div class="spinner"></div><p>AI agents are working on your event plan...</p><p style="font-size:12px;">This may take 1-3 minutes</p></div>';
            
            const data = Object.fromEntries(new FormData(e.target));
            
            try {
                const res = await fetch('/run', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });
                const json = await res.json();
                
                if (json.error) {
                    resultDiv.innerHTML = '<div class="card error"><h3>Error</h3><p>' + json.error + '</p></div>';
                } else {
                    let html = '';
                    
                    if (json.venue) {
                        html += '<div class="card"><h3>📍 Venue</h3>';
                        html += '<p><span class="label">Name:</span> ' + json.venue.name + '</p>';
                        html += '<p><span class="label">Address:</span> ' + json.venue.address + '</p>';
                        html += '<p><span class="label">Capacity:</span> ' + json.venue.capacity + ' guests</p>';
                        html += '<p><span class="label">Status:</span> <span class="status available">' + json.venue.booking_status + '</span></p>';
                        html += '</div>';
                    }
                    
                    if (json.logistics) {
                        html += '<div class="card"><h3>📦 Logistics</h3>';
                        html += '<p>' + json.logistics.replace(/\n/g, '<br>') + '</p></div>';
                    }
                    
                    if (json.marketing) {
                        html += '<div class="card"><h3>📢 Marketing</h3>';
                        html += '<p>' + json.marketing.replace(/\n/g, '<br>') + '</p></div>';
                    }
                    
                    if (!html) {
                        html = '<div class="card"><h3>Results</h3><p>' + JSON.stringify(json, null, 2) + '</p></div>';
                    }
                    
                    resultDiv.innerHTML = html;
                }
            } catch (err) {
                resultDiv.innerHTML = '<div class="card error"><h3>Error</h3><p>' + err.message + '</p></div>';
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
        
        # Handle CrewOutput object
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
            # Fallback for string result
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
