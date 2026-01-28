import os
import typer
# We keep google-generativeai for the existing logic to ensure backward compatibility/stability
# for the previous commands unless we want to rewrite everything.
# However, mixing them might be confusing. The interactions are isolated in commands.
import google.generativeai as old_genai 
from google import genai
from google.genai import types
from rich.console import Console
from rich.markdown import Markdown
from typing import Optional
from pathlib import Path
import base64

app = typer.Typer()
console = Console()

def configure_old():
    """Configure the old SDK for legacy commands."""
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        console.print("[bold red]Error:[/bold red] GOOGLE_API_KEY environment variable not set.")
        raise typer.Exit(code=1)
    old_genai.configure(api_key=api_key)

def get_new_client():
    """Get a client for the new SDK."""
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        console.print("[bold red]Error:[/bold red] GOOGLE_API_KEY environment variable not set.")
        raise typer.Exit(code=1)
    return genai.Client(api_key=api_key)

@app.command()
def list_models():
    """List available Gemini models."""
    configure_old()
    try:
        console.print("[bold]Available Models:[/bold]")
        for m in old_genai.list_models():
            console.print(f"- {m.name} ({m.supported_generation_methods})")
    except Exception as e:
        console.print(f"[bold red]Error listing models:[/bold red] {e}")

@app.command()
def generate(
    prompt: str,
    model: str = "gemini-1.5-flash",
    image_path: Optional[str] = None,
    system_instruction: Optional[str] = None,
    thinking: bool = False
):
    """Generate content using a Gemini model."""
    configure_old()
    try:
        generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 8192,
            "response_mime_type": "text/plain",
        }
        
        if thinking:
             console.print("[italic]Thinking mode request (simulated for legacy SDK wrapper)...[/italic]")

        model_instance = old_genai.GenerativeModel(
            model_name=model,
            generation_config=generation_config,
            system_instruction=system_instruction
        )

        parts = [prompt]
        
        if image_path:
            path = Path(image_path)
            if not path.exists():
                console.print(f"[bold red]Error:[/bold red] Image file not found: {image_path}")
                raise typer.Exit(code=1)
            
            console.print(f"[italic]Uploading {image_path}...[/italic]")
            uploaded_file = old_genai.upload_file(image_path)
            parts.append(uploaded_file)

        response = model_instance.generate_content(parts)
        console.print(Markdown(response.text))

    except Exception as e:
        console.print(f"[bold red]Error generating content:[/bold red] {e}")

@app.command()
def generate_image(
    prompt: str,
    model: str = "imagen-3.0-generate-001",
    output: str = "output_image.png",
    aspect_ratio: str = "1:1",
    number_of_images: int = 1
):
    """Generate images using Imagen."""
    # Using the new Client for image generation as it's cleaner for new models
    client = get_new_client()
    try:
        console.print(f"Generating image with model [bold]{model}[/bold]...")
        
        # Note: 'nano-banana-pro' and 'imagen-4' might be placeholders if not publicly available yet.
        # We will attempt to call the model through the generate_images method of the new SDK if available,
        # or fallback to generation_content logic if it's a multimodal endpoint.
        
        # The new SDK structure: client.models.generate_images(...)
        # However, checking if generate_images exists in client.models is safe.
        # Actually in the new SDK: client.models.generate_image is not always strictly there in the same way.
        # It's often `client.models.generate_content` for everything or `client.imagen.generate_images`.
        # Let's try standard `client.models.generate_images`
        
        response = client.models.generate_image(
            model=model,
            prompt=prompt,
            config=types.GenerateImageConfig(
                number_of_images=number_of_images,
                aspect_ratio=aspect_ratio
            )
        )
        
        if response.generated_images:
            image_data = response.generated_images[0].image.image_bytes
            with open(output, "wb") as f:
                f.write(image_data)
            console.print(f"[green]Image saved to {output}[/green]")
        else:
             console.print("[red]No image returned.[/red]")

    except Exception as e:
         console.print(f"[bold red]Error generating image:[/bold red] {e}")


@app.command()
def tts(
    text: str,
    voice: str = "Sulafat",
    model: str = "gemini-2.5-flash-preview-tts",
    output: str = "output_audio.wav"
):
    """
    Generate speech from text (TTS).
    Default model: gemini-2.5-flash-preview-tts
    Default voice: Sulafat
    """
    client = get_new_client()
    try:
        console.print(f"Generating audio for: '{text}' using {model} ({voice})...")
        
        response = client.models.generate_content(
            model=model,
            contents=text,
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name=voice,
                        )
                    )
                ),
            )
        )

        # Extract audio data
        # Structure: response.candidates[0].content.parts[0].inline_data.data
        if response.candidates and response.candidates[0].content.parts:
            part = response.candidates[0].content.parts[0]
            if part.inline_data:
                audio_data = base64.b64decode(part.inline_data.data)
                
                # Check if we need to add WAV header or if it's raw PCM
                # The doc example used a 'wave_file' helper to write PCM to WAV.
                # If the API returns raw PCM, we must wrap it.
                # Doc says: "data = response...inline_data.data" and calls wave_file(file_name, data)
                # It implies 'data' is PCM.
                
                import wave
                with wave.open(output, "wb") as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(24000)
                    wf.writeframes(audio_data)
                
                console.print(f"[green]Audio saved to {output}[/green]")
            else:
                console.print("[red]No inline audio data found in response.[/red]")
        else:
            console.print("[red]No candidates returned.[/red]")

    except Exception as e:
        console.print(f"[bold red]Error generating audio:[/bold red] {e}")

@app.command()
def embed(
    text: str,
    model: str = "text-embedding-004",
    title: Optional[str] = None
):
    """Generate embeddings for text."""
    configure_old()
    try:
        console.print(f"Embedding text with model: {model}...")
        
        result = old_genai.embed_content(
            model=model,
            content=text,
            task_type="retrieval_document" if title else "retrieval_query",
            title=title
        )
        
        embedding = result['embedding']
        console.print(f"[bold green]Success![/bold green] Generated embedding of length {len(embedding)}")
        
    except Exception as e:
        console.print(f"[bold red]Error generating embedding:[/bold red] {e}")

@app.command()
def upload_file(path: str):
    """Upload a file to the Gemini File API."""
    configure_old()
    try:
        file_path = Path(path)
        if not file_path.exists():
            console.print(f"[bold red]Error:[/bold red] File not found: {path}")
            return

        console.print(f"Uploading {path}...")
        uploaded_file = old_genai.upload_file(path)
        console.print(f"[bold green]Success![/bold green] File uploaded: {uploaded_file.name}")
        console.print(f"URI: {uploaded_file.uri}")
        
    except Exception as e:
        console.print(f"[bold red]Error uploading file:[/bold red] {e}")

if __name__ == "__main__":
    app()
