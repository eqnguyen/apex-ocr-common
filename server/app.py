import logging

import gradio as gr
from PIL import Image
from PIL import ImageDraw
from rich.logging import RichHandler
from pathlib import Path

from apex_ocr.engine import ApexOCREngine
from utils import raise_error
from bounding_boxes import adjust_image_bbox, adjust_slider_vals, adjust_slider_maximums, store_bbox_template_data, apply_bbox_template

logging.captureWarnings(True)
logger = logging.getLogger(__name__)

engine = ApexOCREngine()
        

def process_image(image):
    if image is None:
        raise_error("Please select an image to analyze")
    results = engine.process_screenshot(Image.fromarray(image), debug=True)
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
        with gr.Tab("Upload and Analyze Summary"):
            input = gr.inputs.Image(label="Input").style(height=480)
            btn = gr.Button(label="Submit")
            output = gr.outputs.JSON(label="Result")
            btn.click(process_image, input, output, api_name="process_image")

        with gr.Tab("Create BBox Template"):
            with gr.Row():
                with gr.Column():
                    sample_image = gr.inputs.Image(label="bbox_image")
                    template_image = gr.inputs.Image(label="bbox_image").style(height=720)

                with gr.Column():
                    with gr.Row():
                        x_min_slider = gr.Slider(
                            label="X min",
                            interactive=True,
                            value=0,
                            minimum=0,
                            # maximum=args.max_width,
                            step=1,
                        )
                        
                        x_max_slider = gr.Slider(
                            label="X max",
                            interactive=True,
                            value=0,
                            minimum=0,
                            # maximum=args.max_width,
                            step=1,
                        )

                    with gr.Row():
                        y_min_slider = gr.Slider(
                            label="Y min",
                            interactive=True,
                            value=0,
                            minimum=0,
                            # maximum=args.max_height,
                            step=1,
                        )
                        
                        y_max_slider = gr.Slider(
                            label="Y max",
                            interactive=True,
                            value=0,
                            minimum=0,
                            # maximum=args.max_height,
                            step=1,
                        )
                        
                    
                    bbox_fields = ["damage","kakn","player","respawns","revives","survival_time"]
                    ["P1" + x for x in bbox_fields]
                    with gr.Row():
                        bbox_label_dropdown = gr.Dropdown(
                            label="bbox_label",
                            choices=
                            ["Squad_Place", "Total_Kills"] +
                            ["P1 " + x for x in bbox_fields] +
                            ["P2 " + x for x in bbox_fields] +
                            ["P3 " + x for x in bbox_fields],
                        )
                    
                    sliders = [x_min_slider, y_min_slider, x_max_slider, y_max_slider]

                    sample_image.change(adjust_slider_maximums, sample_image, sliders)
                    sample_image.change(adjust_slider_vals, [sample_image, bbox_label_dropdown], sliders)
                    sample_image.change(apply_bbox_template, sample_image, template_image)

                    bbox_label_dropdown.change(adjust_slider_vals, [sample_image, bbox_label_dropdown] + sliders, sliders)
                    
                    update_template_args = (adjust_image_bbox, sliders + [sample_image, bbox_label_dropdown], template_image)
                    
                    x_min_slider.release(*update_template_args)
                    y_min_slider.release(*update_template_args)
                    x_max_slider.release(*update_template_args)
                    y_max_slider.release(*update_template_args)

                    with gr.Row():
                        add_bbox_annotation = gr.Button(
                            "Add bbox annotation",
                            label="Add bbox annotation",
                            variant="primary",
                        )
                        add_bbox_annotation.click(store_bbox_template_data, [sample_image, x_min_slider, y_min_slider, x_max_slider, y_max_slider, bbox_label_dropdown], template_image, api_name="store_bbox_template_data")
        
        interface.launch(debug=True, inbrowser=False, show_error=True)
            

