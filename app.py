from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging
from flask import Flask, render_template, request, jsonify
import base64
import requests
import random
import json
from io import BytesIO
from PIL import Image
import boto3

app = Flask(__name__)

# Default configuration parameters for Img2Img
CONFIG = {
    "STEPS": 60,
    "DENOISING_STRENGTH": 0.6,
    "CFG_SCALE": 7,
    "SAMPLER_NAME": "Euler a",
    "RANDOMNESS": 0.05,
    "API_URL": "http://localhost:7861/sdapi/v1/img2img"
}

# Function to encode an image to base64
def encode_image_to_base64(image_file):
    image = Image.open(image_file)

    # Convert image to RGB if necessary
    if image.mode in ("RGBA", "P"):
        image = image.convert("RGB")
    
    # Save image to a buffer
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    
    # Encode the image to base64
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

# Function to generate the image via an external API
def generate_image(encoded_image, prompt, negative_prompt, config=CONFIG):
    payload = {
        "init_images": [f"data:image/jpeg;base64,{encoded_image}"],
        "resize_mode": 1,
        "denoising_strength": config["DENOISING_STRENGTH"],
        "cfg_scale": config["CFG_SCALE"],
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "sampler_name": config["SAMPLER_NAME"],
        "steps": config["STEPS"],
        "seed": random.randint(0, 2**32 - 1),
        "strength": 0.2,
        "script_name": "img2img alternative test",
        "script_args": [
            "", False, False, "", "", False, config["STEPS"], False, config["CFG_SCALE"], config["RANDOMNESS"], True
        ]
    }
    # script_args: _, override_sampler, override_prompt, original_prompt, original_negative_prompt, 
    #              override_steps, st, override_strength, cfg, randomness, sigma_adjustment

    response = requests.post(config["API_URL"], headers={"Content-Type": "application/json"}, data=json.dumps(payload))
    
    if response.status_code == 200:
        return response.json().get("images", [None])[0]
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

# Route for the main page
@app.route('/')
def index():
    return render_template('index.html')

# Route for processing the image
@app.route('/process_image', methods=['POST'])
def process_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    image_file = request.files['image']
    if not image_file:
        return jsonify({'error': 'Empty image file'}), 400
    
    # Set denoising strength based on realityFantasy input
    reality_fantasy_map = {
        '1': 0.4,
        '2': 0.5,
        '3': 0.6,
        '4': 0.7,
        '5': 0.8
    }
    denoising_strength = reality_fantasy_map.get(request.form.get('realityFantasy'), CONFIG["DENOISING_STRENGTH"])

    # Encode the input image
    encoded_image = encode_image_to_base64(image_file)

    # Prompts
    prompt_choice = request.form.get('promptChoice')
    if prompt_choice == 'pixar':
        prompt = (
            "Create a digital avatar based on the provided headshot, styled like a Pixar character. "
            "Capture the subject's facial features, hairstyle, and expression, with large eyes, smooth lines, and vibrant colors. "
            "Maintain the original pose, hair color, clothes, and gender, with a plain background to emphasize the character."
        )
    elif prompt_choice == 'hylander':
        prompt = (
            "Create a digital avatar based on the original headshot of a person as a Highlander warrior. "
            "Apply traditional green war paint, but only in minimal areas on the face—such as a few stripes across the cheeks and forehead—without covering the entire face. "
            "Ensure the avatar closely resembles the original headshot, capturing the subject's facial features, hairstyle, skin tone, age, and expression with high fidelity. "
            "The background should subtly evoke the Scottish Highlands, with rolling hills and mist, but remain understated to keep the Highlander warrior as the focal point."
        )
    elif prompt_choice == 'cyborg':
        prompt = (
            "Reimagine the original headshot as a cyborg. "
            "Preserve the original clothing and pose, with a plain background to emphasize the avatar's futuristic and cyborg-like appearance."
        )
    else:
        prompt = "Reimagine the original headshot"
    
    negative_prompt = (
        "no change in gender, no removal of facial hair, no removal of glasses, no exaggerated features, "
        "no overly cartoonish appearance, no other characters in the background"
    )

    # Additional prompt
    additional_prompt = request.form.get('additionalPrompt')
    if additional_prompt != '':
        prompt += additional_prompt

    # Adjust the prompt based on gender input
    gender = request.form.get('gender')
    if gender == 'male':
        prompt += ' The avatar is male.'
    elif gender == 'female':
        prompt += ' The avatar is female.'
    
    # Generate the image via API
    generated_image_base64 = generate_image(encoded_image, prompt, negative_prompt, config={**CONFIG, "DENOISING_STRENGTH": denoising_strength})

    if generated_image_base64:
        log_avatar_creation(denoising_strength, gender, prompt_choice, additional_prompt)
        return jsonify({'image': generated_image_base64})
    else:
        return jsonify({'error': 'Failed to generate the image'}), 500
    
# AWS SES Settings, also requires AWS CLI initialized
CHARSET = "UTF-8"
AWS_REGION = "eu-west-1"
BODY_TEXT = (
    "Hi,\r\n"
    "Thank you for attending Hyland CommunityLIVE 2024! We hope you're enjoying the experience.\r\n"
    "You recently created your custom avatar during the event, and we're excited to send it to you, as requested. Your personalized avatar is attached to this email—feel free to share it, use it in your profiles, or keep it as a memento of the event!\r\n"
    "If you have any questions or need further assistance, don’t hesitate to reach out. We’re thrilled to have you as part of the Hyland community, and we look forward to seeing you at future events!\r\n"
    "Best regards,\r\n"
    "Hyland CommunityLIVE Team"
            )
BODY_HTML = """<html>
<head></head>
<body>
  <p>Hi,</p>
  <p>Thank you for attending Hyland CommunityLIVE 2024! We hope you're enjoying the experience.</p>
  <p>You recently created your custom avatar during the event, and we're excited to send it to you, as requested. Your personalized avatar is attached to this email—feel free to share it, use it in your profiles, or keep it as a memento of the event!</p>
  <p>If you have any questions or need further assistance, don’t hesitate to reach out. We’re thrilled to have you as part of the Hyland community, and we look forward to seeing you at future events!</p>
  <br/>
  <p>
    Best regards,<br/>
    Hyland CommunityLIVE Team
  </p>
</body>
</html>
            """

@app.route('/send_email', methods=['POST'])
def send_email():
    data = request.get_json()
    email = data.get('email')
    avatar_data = data.get('avatar')

    if not email or not avatar_data:
        return jsonify({'success': False, 'error': 'Invalid email or avatar data'}), 400

    # Convert base64 image to bytes
    avatar_data = avatar_data.split(',')[1]
    avatar_bytes = BytesIO(base64.b64decode(avatar_data))

    try:
        # Set up the email
        msg = MIMEMultipart()
        msg['From'] = 'Hyland TSE <tse.aws@hyland.com>'
        msg['To'] = email
        msg['Subject'] = 'Your Custom Avatar from Hyland CommunityLIVE 2024!'

        msg_body = MIMEMultipart('alternative')
        msg_body.attach(MIMEText(BODY_TEXT.encode(CHARSET), 'plain', CHARSET))
        msg_body.attach(MIMEText(BODY_HTML.encode(CHARSET), 'html', CHARSET))
        msg.attach(msg_body)

        # Attach the avatar as a file
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(avatar_bytes.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="avatar.jpg"')
        msg.attach(part)

        # Send the email
        client = boto3.client('sesv2',region_name=AWS_REGION)
        body = bytes (str(msg), 'utf-8')

        response = client.send_email(
            FromEmailAddress=msg['From'],
            Destination={
                'ToAddresses': [msg['To']]
            },
            Content={
                'Raw': {
                    'Data': body
                }
            }
        )

        log_email_sending(msg['To'])

        return jsonify({'success': True, 'messageId': response['MessageId']})

    except Exception as e:
        print(f"Error sending email: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    
# Setup logging configuration
logging.basicConfig(filename='usage_log.txt', level=logging.INFO, 
                    format='%(asctime)s - %(message)s')

def log_avatar_creation(style, gender, type, prompt):
    logging.info(f"Avatar Created - Style: {style}, Gender: {gender}, Type: {type}, Prompt: {prompt}")

def log_email_sending(email):
    logging.info(f"Email Sent - Address: {email}")    

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
