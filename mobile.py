import gradio as gr
import os
import numpy as np
from pydub import AudioSegment
from rvcpu import VoiceClone
import argparse
import shutil
parser = argparse.ArgumentParser()
parser.add_argument('--share', action='store_true', help='Share the Gradio app', default=False)
args = parser.parse_args()
vc = None
weight_root = os.environ.get('weight_root', '')
index_root = os.environ.get('index_root', '')
model_files = [f for f in os.listdir(weight_root) if f.endswith('.pth')] if os.path.exists(weight_root) and os.listdir(weight_root) else []
index_files = []
for root, dirs, files in os.walk(index_root):
    for file in files:
        if file.endswith('.index'):
            index_files.append(os.path.join(root, file))

def initialize_vc(model, index):
    global vc
    if model in model_files:
        vc = VoiceClone(model, os.path.basename(index))
        print(f"Model Loaded: {model}")
    else:
        gr.Warning(f"Invalid model selection: {model}. Please choose a valid model.")
        return None

# Find the .index under the folder that shares a name with the selected .pth model
def find_matching_index(model_path):
    try:
        model_name = os.path.splitext(os.path.basename(model_path))[0]
        for index_file in index_files:
            if model_name in index_file:
                return index_file
    except:
        pass

def convert_audio(audio_path, use_chunks, chunk_size, f0up_key, f0method, index_rate, protect, model_dropdown, index_dropdown):
    print(audio_path, use_chunks, chunk_size, f0up_key, f0method, index_rate, protect, model_dropdown, index_dropdown)
    global vc
    if vc == None:
        try:
            model_name, index_name = model_dropdown, index_dropdown
            initialize_vc(model_name, index_name)
            print("Model initialized.")
        except:
            gr.Warning("Please select a model and index file.")
            return None
    vc.f0up_key = f0up_key
    vc.f0method = f0method
    vc.index_rate = index_rate
    vc.protect = protect
    if use_chunks:
        rate, data = vc.convert_chunks(audio_path, chunk_size=chunk_size)
    else:
        rate, data = vc.convert(audio_path)
    return (rate, np.array(data))

def stereo(audio_path, delay_ms=0.6):
    sample_rate, audio_array = audio_path
    if len(audio_array.shape) == 1:
        audio_bytes = audio_array.tobytes()
        mono_audio = AudioSegment(
            data=audio_bytes,
            sample_width=audio_array.dtype.itemsize,
            frame_rate=sample_rate,
            channels=1
        )
        samples = np.array(mono_audio.get_array_of_samples())
        delay_samples = int(mono_audio.frame_rate * (delay_ms / 1000.0))
        left_channel = np.zeros_like(samples)
        right_channel = samples
        left_channel[delay_samples:] = samples[:-delay_samples]
        stereo_samples = np.column_stack((left_channel, right_channel))
        return (sample_rate, stereo_samples.astype(np.int16))
    else:
        return audio_path

with gr.Blocks(title="🔊",theme=gr.themes.Base(primary_hue="rose",neutral_hue="zinc")) as app:
    gr.Markdown("# 📱VoiceCloner")
    with gr.Row():
        gr.HTML("<a href='https://ko-fi.com/rejekts' target='_blank'>🤝 Donate </a>")
    with gr.Row():
        with gr.Column():
            model_dropdown = gr.Dropdown(choices=model_files, label="Select Model", value=model_files[0] if len(model_files) > 0 else None)
            try: 
                initialize_vc(model_files[0], find_matching_index(model_files[0]))
            except: 
                pass
            index_dropdown = gr.Dropdown(choices=index_files, label="Select Index", value=find_matching_index(model_files[0] if len(model_files) > 0 else None))
            audio_input = gr.Audio(label="Input Audio", type="filepath")
            with gr.Accordion("Settings",open=False):
                use_chunks = gr.Checkbox(label="Use Chunks", value=True)
                chunk_size = gr.Slider(1, 30, value=10, step=1, label="Chunk Size (seconds)")
                f0up_key = gr.Slider(-12, 12, value=0, step=1, label="Pitch Shift")
                f0method = gr.Dropdown(["pm", "rmvpe"], value="pm", label="F0 Method")
                index_rate = gr.Slider(0, 1, value=0.66, step=0.01, label="Index Rate")
                protect = gr.Slider(0, 0.5, value=0.33, step=0.01, label="Protect")
            convert_btn = gr.Button("Convert")
            audio_output = gr.Audio(label="Converted Audio",interactive=False)
            stereo_output = gr.Audio(label="Stereo Effect",interactive=False)
    # Convert audio when the button is clicked
    convert_btn.click(
        convert_audio,
        inputs=[audio_input, use_chunks, chunk_size, f0up_key, f0method, index_rate, protect, model_dropdown, index_dropdown],
        outputs=[audio_output]
    )
    audio_output.change(
        stereo,
        inputs=[audio_output],
        outputs=[stereo_output]
    )

    # Update the value of the index when the model changes
    model_dropdown.change(
        lambda model: find_matching_index(model) if model else None,
        inputs=[model_dropdown],
        outputs=[index_dropdown]
    )
    model_dropdown.change(
        initialize_vc,
        inputs=[model_dropdown, index_dropdown],
    )
    # Update the value of the index when the index changes
    index_dropdown.change(
        initialize_vc,
        inputs=[model_dropdown, index_dropdown],
    )

app.launch(share=args.share,allowed_paths=["a.png","kofi_button.png"])
