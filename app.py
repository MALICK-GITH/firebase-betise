from flask import Flask, render_template, jsonify
import requests

app = Flask(__name__)

# Global variable to store fetched matches (for demonstration purposes)
all_matches = []

# Function for analysis and prediction
def analyze_match(match_data):
    prediction_text = "Aucune prediction sure trouvee (cote entre 1.399 et 3.0)."
    safe_prediction_cote = None
    safe_bets = [] # List to store safe bets

    # Prepare data for the chart (default, empty)
    chart_labels = []
    chart_values = []

    # Iterate through alternative bets
    alternative_bets_groups = match_data.get('AE', [])
    for group in alternative_bets_groups:
        markets = group.get('ME', [])
        for market in markets:
            cote = market.get('C')
            if cote is not None and 1.399 <= cote <= 3.0:
                safe_bets.append(market)
                # Add this bet to the chart data (example)
                chart_labels.append(f"Type {market.get('T')} (P: {market.get('P')})") # Example label
                chart_values.append(cote)

    # TODO: Implement logic to determine the 'most safe' if multiple bets are found.
    # For now, we just use the first safe bet found to update prediction_text and safe_prediction_cote.
    if safe_bets:
        most_safe_bet = safe_bets[0]
        prediction_text = f"Prediction sure trouvee: Type de pari {most_safe_bet.get('T')} avec cote {most_safe_bet.get('C')}"
        if most_safe_bet.get('P') is not None:
             prediction_text += f" (Parametre: {most_safe_bet.get('P')})"
        safe_prediction_cote = most_safe_bet.get('C')

    return {"prediction_text": prediction_text, "safe_prediction_cote": safe_prediction_cote, "chart_labels": chart_labels, "chart_values": chart_values}

@app.route('/')
def index():
    global all_matches # Use the global variable
    api_url = "https://1xbet.com/LiveFeed/Get1x2_VZip?sports=85&count=50&lng=fr&gr=70&mode=4&country=96&getEmpty=true"
    try:
        response = requests.get(api_url)
        response.raise_for_status() # Raise an exception for bad status codes
        data = response.json()

        # Assuming 'Value' contains the list of matches based on the provided JSON structure
        all_matches = data.get('Value', []) # Store matches in the global variable

        # Analyze each match and add the prediction (for display on the index page)
        for match in all_matches:
            analysis_result = analyze_match(match)
            match['prediction_text'] = analysis_result['prediction_text']
            match['safe_prediction_cote'] = analysis_result['safe_prediction_cote']

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from API: {e}")
        all_matches = [] # Return an empty list in case of error

    return render_template('index.html', matches=all_matches)

@app.route('/match/<int:match_id>')
def match_details(match_id):
    # Find the match by its ID in the global list (simplified)
    match = next((m for m in all_matches if m.get('I') == match_id), None)

    if match is None:
        return "Match not found", 404 # Handle case where match is not found

    analysis_result = analyze_match(match)
    return render_template('details.html', match=match, **analysis_result)

if __name__ == '__main__':
    app.run(debug=True)
