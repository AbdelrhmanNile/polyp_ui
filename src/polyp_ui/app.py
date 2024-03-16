import gradio as gr
import cv2
import time
from ultralytics import YOLO
import supervision as sv
import os


class ModelSingleton:
    _instance = None

    def __new__(cls, model_path):
        if cls._instance is None:
            print("Creating the model instance")
            cls._instance = super(ModelSingleton, cls).__new__(cls)
            # Assuming the model initialization is resource-intensive
            cls._instance.model = YOLO(model_path)
        return cls._instance.model

    @staticmethod
    def get_instance():
        if ModelSingleton._instance is None:
            raise ValueError("ModelSingleton instance is not initialized!")
        return ModelSingleton._instance


class DetectionModel:
    def __init__(self, model_path):
        self.model = ModelSingleton(model_path)

    def detectPolyps(self, image):
        return sv.Detections.from_ultralytics(self.model(image)[0])


class EndoscopeDevice:
    def __init__(self, model, serialNumber):
        self.model = model
        self.serialNumber = serialNumber
        self.bbox_annotator = sv.BoxAnnotator()
        self.mask_annotator = sv.MaskAnnotator()

    def captureImages(self, frame, detections, detection_enabled, segmentation_enabled):
        if detection_enabled:
            annotated_frame = self.bbox_annotator.annotate(
                frame, detections, labels=["Polyp"]
            )
        else:
            annotated_frame = frame

        if segmentation_enabled:
            display_frame = self.mask_annotator.annotate(annotated_frame, detections)
        else:
            display_frame = annotated_frame

        return cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)


class Examination:
    def __init__(self, device):
        self.device = device
        self.detection_enabled = True
        self.segmentation_enabled = True
        self.is_paused = False

    def toggle_pause_resume(self):
        self.is_paused = not self.is_paused

    def update_detection_state(self, change):
        self.detection_enabled = change

    def update_segmentation_state(self, change):
        self.segmentation_enabled = change

    def perform(self, input_video):
        cap = cv2.VideoCapture(input_video)
        detection_model = DetectionModel(
            "./src/polyp_ui/models/best.pt"
        )  # For detection

        iterating, frame = cap.read()
        while iterating:
            while self.is_paused:
                time.sleep(0.001)

            detections = detection_model.detectPolyps(frame)
            display_frame = self.device.captureImages(
                frame, detections, self.detection_enabled, self.segmentation_enabled
            )

            yield display_frame

            iterating, frame = cap.read()

        cap.release()


# Gradio interface setup with Examination and EndoscopeDevice integration
def setup_gradio_interface():
    device = EndoscopeDevice(model="Endoscope Model X", serialNumber="123456789")
    examination = Examination(device=device)

    with gr.Blocks() as demo:
        with gr.Row():
            with gr.Column():
                input_video = gr.Video(label="Camera Input")
                examples = gr.Examples(
                    os.path.join(os.path.dirname(__file__), "examples"),
                    inputs=input_video,
                )
                process_video_btn = gr.Button("Feed to Endoscope")

            with gr.Column():
                processed_frames = gr.Image(label="Display")
                with gr.Row():
                    pause_btn = gr.Button("Pause")
                    resume_btn = gr.Button("Resume")
                detection_checkbox = gr.Checkbox(label="Bounding Boxes", value=True)
                segmentation_checkbox = gr.Checkbox(
                    label="Segmentation masks", value=True
                )

        process_video_btn.click(
            examination.perform, inputs=[input_video], outputs=[processed_frames]
        )
        detection_checkbox.change(
            examination.update_detection_state, inputs=[detection_checkbox]
        )
        segmentation_checkbox.change(
            examination.update_segmentation_state, inputs=[segmentation_checkbox]
        )
        pause_btn.click(fn=examination.toggle_pause_resume)
        resume_btn.click(fn=examination.toggle_pause_resume)

    return demo


demo = setup_gradio_interface()
demo.queue()
demo.launch(share=True)
