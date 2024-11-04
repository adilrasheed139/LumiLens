import streamlit as st
import requests

# API keys
ARIA_API_KEY = "d17027ba157a42fc8d5c774c975546da"
ALLEGRO_API_KEY = "11c043eee2e043899c28999d9d635688"

# Base URLs for Aria and Allegro APIs
ARIA_BASE_URL = "https://api.rhymes.ai/v1"
ALLEGRO_VIDEO_URL = "https://api.rhymes.ai/v1/generateVideoSyn"
ALLEGRO_VIDEO_QUERY_URL = "https://api.rhymes.ai/v1/videoQuery"

# Streamlit interface
st.title("Aria Content and Allegro Video Generator")
st.write("Enter a prompt below to get a text response and generate a video based on that response.")

# User input for prompt
user_prompt = st.text_input("Your Prompt:", "How can I make toothpaste?")

# Function to generate text response using Aria API
def generate_text_response(prompt):
    headers = {
        "Authorization": f"Bearer {ARIA_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "aria",
        "messages": [{"role": "user", "content": prompt}],
        "stop": ["<|im_end|>"],
        "stream": False,
        "temperature": 0.6,
        "max_tokens": 1024,
        "top_p": 1
    }

    response = requests.post(f"{ARIA_BASE_URL}/chat/completions", headers=headers, json=data)
    response.raise_for_status()  # Raise an error for unsuccessful status
    return response.json()["choices"][0]["message"]["content"]

# Function to generate video using Allegro API
def generate_video(prompt):
    headers = {
        "Authorization": f"Bearer {ALLEGRO_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "refined_prompt": prompt,
        "num_step": 100,
        "cfg_scale": 7.5,
        "user_prompt": prompt,
        "rand_seed": 12345
    }

    response = requests.post(ALLEGRO_VIDEO_URL, headers=headers, json=data)
    response.raise_for_status()
    
    response_data = response.json()
    
    # Debugging: Print the full response if 'request_id' is missing
    if "request_id" not in response_data:
        st.error("Failed to retrieve request ID. Response received:")
        st.write(response_data)  # Display full response in Streamlit for debugging
        return None
    return response_data["request_id"]

# Function to check the status of video generation
def query_video_status(request_id):
    headers = {"Authorization": f"Bearer {ALLEGRO_API_KEY}"}
    params = {"requestId": request_id}

    response = requests.get(ALLEGRO_VIDEO_QUERY_URL, headers=headers, params=params)
    response.raise_for_status()
    return response.json()

# Button to submit prompt
if st.button("Generate Response and Video"):
    # Generate and display the text response
    st.write("### Text Response:")
    text_response = generate_text_response(user_prompt)
    st.write(text_response)

    # Generate video and retrieve request ID
    st.write("### Generating Video, please wait...")
    request_id = generate_video(user_prompt)

    # Proceed only if request_id was successfully retrieved
    if request_id:
        # Poll for video generation status
        video_url = None
        with st.spinner("Waiting for video generation..."):
            while not video_url:
                status_response = query_video_status(request_id)
                if status_response.get("status") == "completed":
                    video_url = status_response.get("video_url")
                elif status_response.get("status") == "failed":
                    st.error("Video generation failed.")
                    break
                else:
                    st.write("Video generation is in progress...")

        # Display the generated video
        if video_url:
            st.write("### Generated Video:")
            st.video(video_url)
    else:
        st.error("Video generation request failed. Please try again.")
