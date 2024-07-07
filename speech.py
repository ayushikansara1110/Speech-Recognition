import pyaudio
import wave
import requests
 
API_KEY_ASSEMBLYAI = '19a73d08df5048b690029100e60c5061'

FRAMES_PER_BUFFER = 3200
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 18000
p = pyaudio.PyAudio()
 
# starts recording
stream = p.open(
   format=FORMAT,
   channels=CHANNELS,
   rate=RATE,
   input=True,
   frames_per_buffer=FRAMES_PER_BUFFER
)

print("start recording...")

frames = []
seconds = 7
for i in range(0, int(RATE / FRAMES_PER_BUFFER * seconds)):
    data = stream.read(FRAMES_PER_BUFFER)
    frames.append(data)

print("recording stopped")

stream.stop_stream()
stream.close()
p.terminate()

wf = wave.open("output.wav", 'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(p.get_sample_size(FORMAT))
wf.setframerate(RATE)
wf.writeframes(b''.join(frames))
wf.close()

headers = {'authorization' : API_KEY_ASSEMBLYAI}
upload_endpoint = 'https://api.assemblyai.com/v2/upload'
filename = "output.wav"

def upload():
    def read_file(filename, chunk_size = 5242880):
        with open(filename, 'rb') as _file:
            while True:
                data = _file.read(chunk_size)
                if not data:
                    break
                yield data

    response = requests.post(upload_endpoint,
                            headers = headers, 
                            data = read_file(filename))

    print(response.json())

    audio_url = response.json()['upload_url']
    return audio_url

transcript_endpoint = "https://api.assemblyai.com/v2/transcript"

def transcribe(audio_url):
    json = {'audio_url' : audio_url}
    response = requests.post(transcript_endpoint, 
                            json = json,
                            headers = headers)
    job_id = response.json()['id']
    return job_id

def poll(transcript_id):
    polling_endpoint = transcript_endpoint + '/' + transcript_id
    polling_response = requests.get(polling_endpoint, headers = headers)
    return polling_response.json()

def results_url(audio_url):
    transcipt_id = transcribe(audio_url)
    while True: 
        data = poll(transcipt_id)
        if data['status'] == 'completed':
            return data, None
        elif data['status'] == 'error':
            return data, data['error']

audio_url = upload()
data, error = results_url(audio_url)

transcription = data['text']
print(transcription)