import time
import os
from google import genai
from google.genai import types
from google.genai.types import GenerateVideosConfig

# Only run this block for Gemini Developer API
client = genai.Client(api_key='YOUR_API_KEY')

client = genai.Client()

veo_model_name = "veo-2.0-generate-001"
prompt_text = "This high-quality dynamic movement video features a stylish, attractive woman with medium brown skin, wearing a black leather jacket, matching high-waisted leather pants, and gloves. She has a slender physique, small breasts. She is giving attitude towards the viewer."

veo_config = {
    "person_generation": "ALLOW_ADULT",  # Map string to API value
    "aspect_ratio": "16:9",    # Map string to API value
}
print(f"VEO Config: {veo_config}")

operation = None
try:
    print(f"Initiating VEO video generation for prompt: '{prompt_text}' with model '{veo_model_name}'...")
    # The generate_videos method is on client.models
    # Check if client is valid and has the necessary methods
    if client is None:
         raise RuntimeError("Gemini client was not initialized before initiating generation.") # Should not happen
    if not hasattr(client, 'models') or not hasattr(client.models, 'generate_videos'):
         raise AttributeError("Client object or its 'models' attribute does not have 'generate_videos'. Library version issue?")

    operation = client.models.generate_videos(
        model=veo_model_name,
        prompt=prompt_text,
        config=veo_config, # Pass the dictionary config
    )
    print(f"VEO operation initiated. Operation name: {operation.name}")

except AttributeError as e:
    print(f"Error initiating VEO generation: {e}. This likely means your installed 'google-generativeai' library version does not support VEO generation methods on the Client object.")
    print(f"You have 'google-generativeai' version {genai.__version__ if hasattr(genai, '__version__') else 'unknown'}.")
    print("Try upgrading the library in your ComfyUI environment: `python_embeded\python.exe -m pip install --upgrade google-generativeai` (adjust path if needed).")
    exit()
except Exception as e:
    print(f"Error initiating VEO generation API call: {e}")
    # Attempt to get error details from the exception's response attribute if available
    error_message = str(e)
    # ... (rest of error handling for API call initiation)
    if hasattr(e, 'response') and e.response:
         if hasattr(e.response, 'text'):
              try:
                   error_json = json.loads(e.response.text)
                   if 'error' in error_json and 'message' in error_json['error']:
                        api_error_message = error_json['error']['message']
                        print(f"API Error Message from response: {api_error_message}")
                        error_message = f"API Error: {api_error_message}"
                   elif hasattr(e.response, 'status_code') and hasattr(e.response, 'reason'):
                        error_message = f"HTTP Error: {e.response.status_code} {e.response.reason}"
              except (json.JSONDecodeError, AttributeError):
                   if hasattr(e.response, 'status_code') and hasattr(e.response, 'reason'):
                        error_message = f"HTTP Error: {e.response.status_code} {e.response.reason}"
    print(f"Error initiating VEO generation: {error_message}")
    exit()

while not operation.done:
    time.sleep(20)
    operation = client.operations.get(operation)

# --- Process Response and Save Video(s) ---
generated_video_paths = []
# Define a default save directory (e.g., current script directory)
save_dir = os.path.dirname(os.path.abspath(__file__)) # Save in the same directory as the script

if not save_dir:
    print("Error: Save directory could not be determined.")
    exit()

# Ensure the save directory exists
try:
    os.makedirs(save_dir, exist_ok=True)
    print(f"Ensured save directory exists: {save_dir}")
except Exception as e:
    print(f"Error creating save directory '{save_dir}': {e}")
    exit()


# Try to access generated_videos using both attribute and key access, based on type check
generated_videos_list = None
if isinstance(operation.response, dict) and 'generated_videos' in operation.response and isinstance(operation.response['generated_videos'], list):
    generated_videos_list = operation.response['generated_videos'] # Access as dict key
elif hasattr(operation.response, 'generated_videos') and isinstance(operation.response.generated_videos, list):
    generated_videos_list = operation.response.generated_videos # Access as attribute

# Process the list if we successfully found it
if generated_videos_list:
    print(f"Processing {len(generated_videos_list)} generated video item(s)...")
    for n, generated_video_item in enumerate(generated_videos_list):

        video_object = None
        # Try accessing the 'video' part using attribute or key access
        # based on the debugging output, it seems to be an attribute on a Video object
        if hasattr(generated_video_item, 'video'): # Try dot notation (if item is an object)
             video_object = generated_video_item.video
             print(f"DEBUG: Accessed video object for item {n} using dot notation.")
        elif isinstance(generated_video_item, dict) and 'video' in generated_video_item: # Try key notation (if item is a dictionary)
             video_object = generated_video_item['video']
             print(f"DEBUG: Accessed video object for item {n} using key notation.")
        else:
             print(f"Warning: Generated video item {n} has no 'video' attribute or key.")
             continue # Skip this item if video data is missing


        # Check if the obtained video_object is valid for download
        if video_object:
            # Construct the filename
            safe_prompt = "".join([c for c in prompt_text if c.isalnum() or c in (' ', '-', '_')]).replace(' ', '_')[:50].strip('_') # Added strip
            if not safe_prompt: safe_prompt = "veo_video"
            timestamp_str = str(int(time.time()))
            filename = f"{safe_prompt}_{timestamp_str}_{n}.mp4"
            full_save_path = os.path.join(save_dir, filename)

            print(f"Attempting to download and save video {n} to {full_save_path} using client.files.download()...")
            try:
                # Use client.files.download() to download the remote video object
                # Pass the remote video object (or its name/ID) and the local destination path
                # The error 'unexpected keyword argument destination_path' means this method signature is wrong.
                # We previously confirmed client.files.download(file=video_object) returns bytes.

                print(f"DEBUG: Calling client.files.download(file=video_object)...")
                if not hasattr(client, 'files') or not hasattr(client.files, 'download'):
                     raise AttributeError("Client object or its 'files' attribute does not have 'download'. Library version issue?")

                # Call download - assume it returns bytes
                video_content_bytes = client.files.download(file=video_object)
                print(f"DEBUG: client.files.download returned type: {type(video_content_bytes)}")
                print(f"DEBUG: Length of returned content: {len(video_content_bytes) if hasattr(video_content_bytes, '__len__') else 'N/A'}")

                # Check if returned content is bytes and non-empty
                if isinstance(video_content_bytes, bytes) and video_content_bytes:
                    # Write the bytes to the local file
                    print(f"DEBUG: Writing {len(video_content_bytes)} bytes to local file {full_save_path}...")
                    with open(full_save_path, 'wb') as f:
                        f.write(video_content_bytes)
                    print(f"Successfully saved video {n} to {full_save_path}.")
                    generated_video_paths.append(full_save_path)
                else:
                     # This handles cases where download might return None, an empty bytes object, or something else unexpected
                     print(f"Error: client.files.download() returned unexpected content type ({type(video_content_bytes)}) or empty content for video {n}.")
                     print(f"DEBUG: Full content returned by download: {video_content_bytes}") # Print content for more info


            except AttributeError as e:
                 # Catch specific AttributeError for missing client.files.download
                 error_message = f"Error downloading video {n}: {e}. This likely means your installed 'google-generativeai' library version does not support file downloads via this method."
                 print(error_message)
                 print(f"You have 'google-generativeai' version {genai.__version__ if hasattr(genai, '__version__') else 'unknown'}.")
                 # In a script, exit here or just warn
                 # In the node, you'd return an error
                 exit()
            except Exception as e:
                print(f"Error downloading and saving video {n} to {full_save_path}: {e}")
                # For this script, just print error and continue to next video
                # For the node, you might return here or collect errors

        else:
             print(f"Warning: Generated video item {n} has no downloadable video object after checking attributes/keys.")


    # Check if any videos were actually saved
    if not generated_video_paths:
         print("Warning: Operation completed, but no video files were successfully saved.")
         # Check for block reason in prompt feedback if available (logic from node)
         if hasattr(operation, 'response') and operation.response and hasattr(operation.response, 'prompt_feedback') and operation.response.prompt_feedback:
              if hasattr(operation.response.prompt_feedback, 'block_reason') and operation.response.prompt_feedback.block_reason and hasattr(operation.response.prompt_feedback.block_reason, 'name') and operation.response.prompt_feedback.block_reason.name != 'UNASSIGNED':
                   block_reason = operation.response.prompt_feedback.block_reason.name
                   print(f"Prompt Block Reason in Response: {block_reason}")

         # In a script, you might just print an error message here
         print("Error: No videos were successfully generated or saved after processing response.")


else:
     # Handle cases where generated_videos_list was not found in the expected structure
     print("Error: VEO operation completed, but the 'generated_videos' list was not found in the response structure.")
     print(f"Full operation response object: {operation.response}") # Debugging print
     # In a script, you might exit here or print an error.


# --- Output the path(s) ---
if generated_video_paths:
    print("\nSuccessfully generated and saved video(s) at:")
    for p in generated_video_paths:
        print(p)
else:
    print("\nNo videos were successfully generated or saved.")