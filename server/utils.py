import logging
import gradio as gr


logger = logging.getLogger(__name__)

def raise_error(err_msg):
    logger.error(err_msg)
    raise gr.Error(err_msg)