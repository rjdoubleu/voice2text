import os
import uuid
import torch
from glob import glob
from flask import Flask, flash, request, redirect
from pydub import AudioSegment

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'audio/')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def root():
    return redirect('https://www.rosenblatt.ai/site', code=301)
    
@app.route('/site')
def site():
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
    app.logger.debug('saving file')
    file_name = str(uuid.uuid4()) + ".wav"
    full_file_name = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
    file.save(full_file_name)

    # overwrite file to correct compatibility issue
    app.logger.debug('overwriting file')
    sound = AudioSegment.from_file(full_file_name)
    sound.export(full_file_name, format="wav")

    # format sample for model
    app.logger.debug('formating file sample')
    test_files = glob(full_file_name)
    app.logger.info(test_files)
    batches = split_into_batches(test_files, batch_size=10)
    input = prepare_model_input(read_batch(batches[0]), device=device)
    
    # remove temporary file
    os.remove(full_file_name)

    # voice to text prediction
    app.logger.debug('performing prediction')
    text = ''
    output = model(input)
    for example in output:
        text += decoder(example.cpu())
    app.logger.debug('prediction: ' +  text)
    return text
    

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

    app.run(debug=True, threaded=True, host='0.0.0.0', port=5000)
