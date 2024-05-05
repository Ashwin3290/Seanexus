from flask import Flask, request, render_template, abort, jsonify,send_from_directory
import requests

app = Flask(__name__)
api_base_url = "http://localhost:5000"


@app.route('/')
def index():
    return send_from_directory('templates', 'landingpage.html')

@app.route('/<page>')
def render_page(page):
    try:
        filename = f"{page}.html"
        return send_from_directory('templates', filename)
    except:
        abort(404)

@app.route('/api', methods=['POST'])
def proxy_request():
    try:
        data = request.json
        endpoint = data.get('endpoint')
        payload = data.get('payload')


        client_ip = request.remote_addr

        freegeoip_url = f"http://freegeoip.app/json/{client_ip}"
        response = requests.get(freegeoip_url)
        geolocation_data = response.json()

        response = requests.post(f"{api_base_url}/{endpoint}", json=payload)
        
        return jsonify({
            "response": response.json(),
            "client_ip": client_ip,
            "geolocation": geolocation_data
        }), response.status_code
    except Exception as e:
        print("Error:", e)
        abort(500)

# Error handler for 404
@app.errorhandler(404)
def page_not_found(error):
    return render_template('error.html'), 404

if __name__ == '__main__':
    app.run(debug=True)
