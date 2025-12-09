from flask import Flask, render_template_string, request, jsonify
from crew import run_crew

app = Flask(__name__)

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Event Planner AI</title>
    <style>
        body { font-family: Arial; max-width: 600px; margin: 50px auto; padding: 20px; }
        input, select { width: 100%; padding: 10px; margin: 10px 0; }
        button { background: #4CAF50; color: white; padding: 15px; border: none; width: 100%; cursor: pointer; }
        #result { margin-top: 20px; white-space: pre-wrap; background: #f5f5f5; padding: 15px; }
    </style>
</head>
<body>
    <h1>Event Planner AI</h1>
    <form id="form">
        <input name="event_topic" placeholder="Event Topic" required>
        <input name="event_city" placeholder="City" required>
        <input name="tentative_date" type="date" required>
        <input name="expected_participants" type="number" placeholder="Expected Participants" required>
        <input name="budget" type="number" placeholder="Budget ($)" required>
        <button type="submit">Plan Event</button>
    </form>
    <div id="result"></div>
    <script>
        document.getElementById('form').onsubmit = async (e) => {
            e.preventDefault();
            document.getElementById('result').innerText = 'Working... (this may take a few minutes)';
            const data = Object.fromEntries(new FormData(e.target));
            const res = await fetch('/run', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });
            const json = await res.json();
            document.getElementById('result').innerText = JSON.stringify(json, null, 2);
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
    data = request.json
    data['expected_participants'] = int(data['expected_participants'])
    data['budget'] = int(data['budget'])
    data['event_description'] = f"Event about {data['event_topic']}"
    result = run_crew(data)
    return jsonify({"result": str(result)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
