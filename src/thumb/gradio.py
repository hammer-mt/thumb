import gradio as gr

with gr.Blocks() as demo:
    with gr.Row():
        response = gr.Textbox(label="Topic", scale=85, value="Memetics")
    with gr.Row():
        thumbs_down = gr.Button("👎", scale=15)
        thumbs_up = gr.Button("👍", scale=15) 

        thumbs_down.click(fn=lambda x: x, inputs=[response], outputs=[], api_name="thumbs_down")
        thumbs_up.click(fn=lambda x: x, inputs=[response], outputs=[], api_name="thumbs_up")
        

if __name__ == "__main__":
    demo.launch()