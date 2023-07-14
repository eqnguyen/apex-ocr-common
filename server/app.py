import logging

import gradio as gr
from PIL import Image
from rich.logging import RichHandler

from apex_ocr.engine import ApexOCREngine

logging.captureWarnings(True)
logger = logging.getLogger(__name__)

engine = ApexOCREngine()


def process_image(image):
    results = engine.process_screenshot(Image.fromarray(image))
    return results


if __name__ == "__main__":
    # Configure logger
    logging.basicConfig(
        level=logging.INFO,
        format=" %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        force=True,
        handlers=[
            RichHandler(omit_repeated_times=False, rich_tracebacks=True),
        ],
    )

    with gr.Blocks(title="Apex OCR") as interface:
        input = gr.inputs.Image(label="Input").style(height=480)
        btn = gr.Button(label="Submit")
        output = gr.outputs.JSON(label="Result")
        btn.click(process_image, input, output, api_name="process_image")
        interface.launch(debug=True, inbrowser=True)
