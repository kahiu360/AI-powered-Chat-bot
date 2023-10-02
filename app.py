from flask import Flask, render_template, request, jsonify
import requests
from wit import Wit

app = Flask(__name__)

# Wit.ai access token
access_token = "ESMD6DOJ2SK7PVB66JG6HL3LVKAPQJNP"
client = Wit(access_token)

# List of electric cars
cars = [
    {"model": "Model X", "price": "$69,420", "color": ["black", "blue", "silver"], "features": ["Autopilot", "Supercharging"]},
    {"model": "Model Y", "price": "$79,990", "color": ["white"], "features": ["Falcon Wing Doors", "Autopilot"]},
    {"model": "Model Z", "price": "$35,000", "color": ["red"], "features": ["Autopilot", "Long Range Battery"]},
    {"model": "Model Q", "price": "$31,600", "color": ["blue", "black"], "features": ["ProPILOT Assist", "e-Pedal"]}
]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/car')
def get_car():
    # Get car model from Wit.ai
    model = request.args.get('model')

    # Search for car in list of cars
    for car in cars:
        if car['model'].lower() == model.lower():
            return jsonify(car)

    # If car not found, return error message
    return jsonify({"error": "Car not found"})

@app.route('/message', methods=['POST'])
def handle_message():
    # Get user message from request
    message_text = request.json['message']

    # Call wit.ai API to detect user intent and extract entities
    headers = {'Authorization': f'Bearer {access_token}'}
    params = {'q': message_text}
    resp = requests.get('https://api.wit.ai/message', headers=headers, params=params)
    resp.raise_for_status()
    data = resp.json()
    intent = data['intents'][0]['name'] if len(data['intents']) > 0 else None
    entities = data['entities']

    # Perform action based on detected intent
    if intent == 'getPrice':
        model = entities.get('vehicleModel:vehicleModel', [{'value': None}])[0]['value']
        if model:
            for car in cars:
                if car['model'].lower() == model.lower():
                    return jsonify({"response": f"The {car['model']} costs {car['price']}"})
            return jsonify({"response": "I'm sorry, I couldn't find information about that car."})
        else:
            return jsonify({"response": "I'm sorry, I didn't understand which car you are asking for."})
        
    elif intent == 'getFeatures':
        model = entities.get('vehicleModel:vehicleModel', [{'value': None}])[0]['value']
        if model:
            for car in cars:
                if car['model'].lower() == model.lower():
                    features = ' and '.join(car['features'])
                    return jsonify({"response": f"The {car['model']} features include {features}"})
            return jsonify({"response": "I'm sorry, I couldn't find information about that car."})
        else:
            return jsonify({"response": "I'm sorry, I didn't understand which car you are asking for."})

    elif intent == 'getColorOptions':
        model = entities.get('vehicleModel:vehicleModel', [{'value': None}])[0]['value']
        if model:
            for car in cars:
                if car['model'].lower() == model.lower():
                    color = ' and '.join(car['color'])
                    return jsonify({"response": f"The {car['model']} comes in {color}"})
            return jsonify({"response": "I'm sorry, I couldn't find information about that car."})
        else:
            return jsonify({"response": "I'm sorry, I didn't understand which car you are asking for."})
        
    elif intent == 'getModels':
        models = [car['model'] for car in cars]
        models_str = ',\n'.join(models)
        return jsonify({"response": f"The car models available are:\n{models_str}"})

    else:
        return jsonify({"response": "I'm sorry, I didn't understand what you're asking."})

        
@app.route('/message', methods=['GET'])   
def get_car_info(response):
    model = response['entities']['car:car'][0]['value']
    for car in cars:
        if car['model'].lower() == model.lower():
            features = 'and '.join(car['features'])
            return f"The {car['model']} costs {car['price']} and comes in {car['color']}. Its features include {features}."
    return "I'm sorry, I couldn't find information about that car."

if __name__ == '__main__':
    app.run()