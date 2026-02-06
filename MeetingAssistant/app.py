import gradio as gr
from transcriber import Transcriber
from summarizer import Summarizer
from utils import validate_audio_file, format_transcription_info, save_to_file, get_safe_filename
from config import Config
import os


class MeetingAssistantApp:
    def __init__(self):
        self.transcriber = Transcriber()
        self.summarizer = Summarizer()
        self.current_transcription = ""
        self.current_summary = ""
        self.current_filename = ""
    
    def process_audio(
        self,
        audio_file,
        summary_length
    ):
        if audio_file is None:
            yield "", "", "Please upload an audio file."
            return
        
        audio_path = audio_file if isinstance(audio_file, str) else audio_file.name
        self.current_filename = os.path.basename(audio_path)
        
        is_valid, error_msg = validate_audio_file(audio_path)
        if not is_valid:
            yield "", "", error_msg
            return
        
        try:
            status = f"Processing: {self.current_filename}\n"
            yield status, "", ""
            
            transcription_result = self.transcriber.transcribe_sync(
                audio_path,
                progress=lambda p, desc: self._update_progress(p, desc)
            )
            
            self.current_transcription = transcription_result.get("text", "")
            
            transcription_output = format_transcription_info(transcription_result)
            
            status = f"Transcription complete!\nGenerating summary...\n"
            yield transcription_output, "", status
            
            self.current_summary = self.summarizer.summarize(
                self.current_transcription,
                summary_length,
                progress=lambda p, desc: self._update_progress(p, desc)
            )
            
            summary_output = f"MEETING SUMMARY\n{'=' * 50}\n\n{self.current_summary}"
            
            status = f"Processing complete!\n\nTranscription and summary generated for: {self.current_filename}"
            
            yield transcription_output, summary_output, status
            
        except Exception as e:
            error_status = f"Error processing audio: {str(e)}"
            yield "", "", error_status
    
    def _update_progress(self, progress: float, description: str):
        return (progress, description)
    
    def download_transcription(self):
        if not self.current_transcription:
            return None
        filename = get_safe_filename(self.current_filename, "transcription")
        filepath = save_to_file(self.current_transcription, filename)
        return filepath
    
    def download_summary(self):
        if not self.current_summary:
            return None
        filename = get_safe_filename(self.current_filename, "summary")
        filepath = save_to_file(self.current_summary, filename)
        return filepath


def create_interface():
    app = MeetingAssistantApp()
    
    with gr.Blocks(title="Meeting Assistant", theme=gr.themes.Soft()) as interface:
        gr.Markdown("# 🎙️ Meeting Assistant")
        gr.Markdown("Upload an audio recording of a meeting to transcribe and summarize it.")
        
        with gr.Row():
            with gr.Column(scale=1):
                audio_input = gr.Audio(
                    label="Upload Meeting Audio",
                    type="filepath",
                    sources=["upload", "microphone"]
                )
                
                summary_length = gr.Radio(
                    choices=["brief", "detailed", "very_brief"],
                    value="brief",
                    label="Summary Length",
                    info="Choose how detailed the summary should be"
                )
                
                process_btn = gr.Button(
                    "Transcribe and Summarize",
                    variant="primary",
                    size="lg"
                )
            
            with gr.Column(scale=2):
                status_box = gr.Textbox(
                    label="Status",
                    lines=2,
                    interactive=False,
                    placeholder="Upload an audio file to begin..."
                )
        
        with gr.Row():
            with gr.Column():
                transcription_output = gr.Textbox(
                    label="Transcription",
                    lines=15,
                    interactive=False,
                    placeholder="Transcription will appear here..."
                )
                
                transcript_download_btn = gr.Button(
                    "⬇️ Download Transcription",
                    variant="secondary"
                )
                
                transcript_download = gr.File(
                    label="",
                    visible=False
                )
            
            with gr.Column():
                summary_output = gr.Textbox(
                    label="Summary",
                    lines=15,
                    interactive=False,
                    placeholder="Summary will appear here..."
                )
                
                summary_download_btn = gr.Button(
                    "⬇️ Download Summary",
                    variant="secondary"
                )
                
                summary_download = gr.File(
                    label="",
                    visible=False
                )
        
        gr.Markdown("---")
        gr.Markdown("### Features")
        gr.Markdown("- ✅ Transcribes audio using Whisper")
        gr.Markdown("- ✅ Summarizes meetings using Ollama (gemma3:latest)")
        gr.Markdown("- ✅ Configurable summary length")
        gr.Markdown("- ✅ Real-time progress updates")
        gr.Markdown("- ✅ Download transcripts and summaries")
        
        process_btn.click(
            fn=app.process_audio,
            inputs=[audio_input, summary_length],
            outputs=[transcription_output, summary_output, status_box]
        )
        
        transcript_download_btn.click(
            fn=app.download_transcription,
            outputs=[transcript_download]
        ).then(
            lambda: gr.update(visible=True),
            outputs=[transcript_download]
        )
        
        summary_download_btn.click(
            fn=app.download_summary,
            outputs=[summary_download]
        ).then(
            lambda: gr.update(visible=True),
            outputs=[summary_download]
        )
    
    return interface


if __name__ == "__main__":
    interface = create_interface()
    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        # show_api=False
    )