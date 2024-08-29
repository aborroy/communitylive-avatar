# Avatar Generator for Hyland CommunityLIVE 2024

This project provides a web application that generates avatars from headshots captured via webcam or uploaded files. It leverages the `img2img` functionality of the [Stable Diffusion](https://stability.ai) REST API, which is integrated through the [Stable Diffusion WebUI](https://github.com/AUTOMATIC1111/stable-diffusion-webui).

## Features

- **Avatar Creation**: Generate personalized avatars from headshots.
- **Flexible Input**: Accepts images from both webcam captures and file uploads.
- **Customizable**: Adjust the fantasy and gender preferences for the generated avatar.

## Requirements

- **Python**: Version 3.10
- **Stable Diffusion WebUI**: [GitHub Repository](https://github.com/AUTOMATIC1111/stable-diffusion-webui)
- **GPU**: Recommended for optimal performance

## Project Structure

The project is centered around a Python application (`app.py`) that exposes a REST API. This API processes an original image along with optional parameters (fantasy level and gender preference) and returns the generated avatar. The following directories and files are included:

```bash
.
├── app.py           # Main application file exposing REST API
├── static           # Static resources for the web application
│   ├── Hyland_logo.png
│   └── style.css
└── templates        # HTML templates
    └── index.html
```

## Setting Up Stable Diffusion WebUI

The Python application is configured to connect to the Stable Diffusion REST API at `http://localhost:7861/sdapi/v1/img2img` by default. Follow these steps to install and set up the REST API locally:

1. **Clone the Stable Diffusion WebUI Repository**

   ```bash
   git clone https://github.com/AUTOMATIC1111/stable-diffusion-webui
   cd stable-diffusion-webui
   ```

2. **Download a Stable Diffusion Model from Hugging Face**

   ```bash
   cd models/Stable-diffusion
   wget https://huggingface.co/lllyasviel/fav_models/resolve/main/fav/realisticVisionV51_v51VAE.safetensors
   cd ../..
   ```

3. **Create a Virtual Environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

4. **Install Dependencies and Start the WebUI**

   Run the script to install requirements and start the application:

   ```bash
   ./webui.sh
   ```

   Once the application is running at `http://127.0.0.1:7860`, you can stop it with `Ctrl+C`.  
   _Note: This step is required only during the initial setup._

5. **Start the REST API**

   If you don't have a GPU, you can start the API using the CPU:

   ```bash
   python3 launch.py --nowebui --skip-python-version-check --always-cpu --skip-torch-cuda-test
   ```

   The API will be accessible via your browser at `http://localhost:7861/docs#/default/img2imgapi_sdapi_v1_img2img_post`.

## Local Testing

To test the application locally:

1. **Start the Stable Diffusion REST API** and ensure `http://localhost:7861/sdapi/v1/img2img` is reachable.

2. **Start the Web Application**

   Set up the Python environment and run the application:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install flask requests Pillow
   python3 app.py
   ```

3. **Access the Web Application**

   Open a web browser and navigate to `http://localhost:5000` to use the avatar generator.

## Deployment on AWS EC2

To deploy the application on an AWS EC2 instance, follow the usual process of setting up a server, ensuring that Python 3.10, the Stable Diffusion WebUI, and other dependencies are properly installed. Adjust security groups and instance types based on whether you are using a GPU. Refer to the [AWS documentation](https://docs.aws.amazon.com/ec2/index.html) for detailed instructions.