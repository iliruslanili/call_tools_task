import io
from io import BytesIO

import soundfile
import uvicorn
from fastapi import FastAPI, UploadFile, Response, File, Form
from fastapi.responses import FileResponse
import librosa
from fastapi.responses import ORJSONResponse

app = FastAPI()


@app.post('/modify_audio_file')
async def modify_audio_file(
        file: UploadFile = File(media_type='audio/wav'),
        speed: float = Form(le=2, gt=0, default=1),
        volume: int = Form(le=200, gt=0, default=100)
):
    x, sr = librosa.load(file.file)

    target_volume = volume / 100
    target_sample_rate = int(sr * speed)

    print(sr, target_sample_rate)

    x = x * target_volume
    x = librosa.resample(x, orig_sr=sr, target_sr=target_sample_rate)

    result = io.BytesIO()
    soundfile.write(result, samplerate=44100, data=x, format='wav')

    headers = {'Content-Disposition': f'attachment; filename="{file.filename}"'}
    return Response(content=result.getvalue(), media_type='application/octet-stream', headers=headers)
    # return FileResponse(file_path, media_type='audio/wav')
    # return ORJSONResponse(content=data)
    # return file


if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=True)
