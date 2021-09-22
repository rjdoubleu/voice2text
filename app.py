import torch
import zipfile
import torchaudio
from glob import glob
import os
import uuid
from flask import Flask, flash, request, redirect

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'audio\\')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def root():
    return app.send_static_file('index.html')


@app.route('/save-record', methods=['POST'])
def save_record():
    # check if the post request has the file part
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    
    file = request.files['file']

    # if user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)

    # save sample
    file_name = str(uuid.uuid4()) + ".wav"
    full_file_name = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
    file.save(full_file_name)
    
    # format sample for model
    test_files = glob(full_file_name)
    app.logger.info(test_files)
    batches = split_into_batches(test_files, batch_size=10)
    input = prepare_model_input(read_batch(batches[0]),
                                device=device)
    
    # voice to text prediction
    text = ''
    output = model(input)
    for example in output:
        text += decoder(example.cpu())
    app.logger.info(text)
    return '<h1>Success</h1>'
    

if __name__ == "__main__":
    # gpu also works, but our models are fast enough for CPU
    device = torch.device('cpu')  

    # languages also available 'de', 'es'
    model, decoder, utils = torch.hub.load(repo_or_dir='snakers4/silero-models',
                                        model='silero_stt',
                                        language='en', 
                                        device=device)

    # see function signature for details
    (read_batch, split_into_batches,
    read_audio, prepare_model_input) = utils  

    app.run(debug=True, threaded=True)
