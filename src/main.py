import io
import torch
import librosa
import uvicorn
import soundfile
from io import BytesIO
from transformers import pipeline
from fastapi import FastAPI, UploadFile, Response, File, Form

app = FastAPI()

device = "cuda:0" if torch.cuda.is_available() else "cpu"

print(f'device: {device}')
#
pipe = pipeline(
  "automatic-speech-recognition",
  model="/tmp/model",
  # model="openai/whisper-small",
  # model_path="/tmp/model",
  # chunk_length_s=20,
  device=device,
)

@app.post('/modify_audio_file')
async def modify_audio_file(
        file: UploadFile = File(media_type='audio/wav', description='Звуковая дорожка для изменения'),
        speed: float = Form(le=2, gt=0, default=1, description='Множитель скорости: 2 - в 2 раза быстрее, 0.5 - в 2 раза медленнее'),
        volume: int = Form(le=200, gt=0, default=100, description='Множитель громкости: 200 - в 2 раза громче, 50 - в 2 раза тише')
):
    x, sr = librosa.load(file.file)

    target_volume = volume / 100
    target_sample_rate = int(sr * speed)

    print(sr, target_sample_rate)

    x = x * target_volume
    # x_hat = librosa.resample(x, orig_sr=sr, target_sr=target_sample_rate)

    result = io.BytesIO()
    soundfile.write(result, samplerate=target_sample_rate, data=x, format='wav')

    headers = {'Content-Disposition': f'attachment; filename="{file.filename}"'}
    return Response(content=result.getvalue(), media_type='application/octet-stream', headers=headers)


@app.post('/speech_to_text')
async def stt(file: UploadFile = File(description='Звуковая дорожка для распознавания')):
    x, sr = librosa.load(file.file)
    prediction = pipe(
        x.copy(),
        batch_size=4,
        return_timestamps=True
    )
    # print(prediction
    return prediction


if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=True)
