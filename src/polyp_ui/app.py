import gradio as gr
import cv2
import time
from ultralytics import YOLO
import supervision as sv
import os
import database as db
import random

db.init_database()


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
    def __init__(self, model, location):
        self.model = model
        self.location = location
        self.bbox_annotator = sv.BoxAnnotator(thickness=10, text_thickness=2)
        self.mask_annotator = sv.MaskAnnotator()

        self.counter = 0

    def captureImages(self, frame, detections, detection_enabled, segmentation_enabled):

        raw_path = "/home/pirate/projects/polyp_ui/output/raw/"
        segmented_path = "/home/pirate/projects/polyp_ui/output/segmented/"
        # cv2.imwrite(f"{raw_path}{self.counter}.jpg", frame)

        # db.insert_ColonoscopyImage(1, f"{raw_path}{self.counter}.jpg")

        if detection_enabled:
            annotated_frame = self.bbox_annotator.annotate(
                frame, detections, labels=["Polyp"]
            )
        else:
            annotated_frame = frame

        if segmentation_enabled:
            display_frame = self.mask_annotator.annotate(annotated_frame, detections)
            # cv2.imwrite(f"{segmented_path}{self.counter}.jpg", display_frame)
            # db.insert_SegmentationOutput(1, 1, f"{segmented_path}{self.counter}.jpg")
        else:
            display_frame = annotated_frame

        # db.insert_DetectedPolyps(self.counter, 1, len(detections))

        self.counter += 1

        return cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)


class Examination:
    def __init__(self, device):
        self.device = device
        self.detection_enabled = True
        self.segmentation_enabled = True
        self.is_paused = False

        self.detection_model = DetectionModel("./src/polyp_ui/models/best.pt")

    def toggle_pause_resume(self):
        self.is_paused = not self.is_paused

    def update_detection_state(self, change):
        self.detection_enabled = change

    def update_segmentation_state(self, change):
        self.segmentation_enabled = change

    def perform(self, input_video):
        cap = cv2.VideoCapture(input_video)
        # For detection

        iterating, frame = cap.read()
        while iterating:
            while self.is_paused:
                time.sleep(0.001)

            detections = self.detection_model.detectPolyps(frame)
            display_frame = self.device.captureImages(
                frame, detections, self.detection_enabled, self.segmentation_enabled
            )

            yield display_frame

            iterating, frame = cap.read()

        cap.release()


def log_patient_start_session(patient_name, patient_dob, patient_gender):
    # db.insert_Patient(patient_name, patient_dob, patient_gender)

    db.insert_ColonoscopySession(1, 1, 1, time.strftime("%Y-%m-%d %H:%M:%S"))


# Gradio interface setup with Examination and EndoscopeDevice integration
def setup_gradio_interface():

    ed = db.query_EndoscopeDevice(1)
    device = EndoscopeDevice(model=ed[0], location=ed[1])

    examination = Examination(device=device)

    with gr.Blocks() as demo:

        """ with gr.Tab("Patient Information"):
            with gr.Row():
                with gr.Column():
                    patient_name = gr.Textbox(label="Patient Name", type="text")
                    p_dob = gr.Textbox(label="Date of Birth", type="text")
                    p_gender = gr.Dropdown(label="Gender", choices=["Male", "Female"])

                    log_p_info = gr.Button("Log Patient Information") """

        with gr.Tab(label="Endoscope Interface"):
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

        """ log_p_info.click(
            log_patient_start_session,
            inputs=[patient_name, p_dob, p_gender],
        ) """

    return demo


demo = setup_gradio_interface()
demo.queue()
demo.launch(share=True)
