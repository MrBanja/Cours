import pathlib

import uvicorn
from fastapi import FastAPI, Request, File, Form
from fastapi.responses import HTMLResponse
from rsa.pkcs1 import VerificationError
from starlette.templating import Jinja2Templates

from src.signatures import sign_file, validate_signature, get_key_pair_bytes
from src.encryption import aes_encrypt_file, aes_decrypt_file, des_encrypt_file, des_decrypt_file

app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.get('/')
async def index(request: Request):
    return templates.TemplateResponse('index.html', {'request': request})


@app.get('/generate_keys', response_class=HTMLResponse)
async def generate_keys():
    pub, priv = get_key_pair_bytes()
    with pathlib.Path(__file__).resolve().parent.parent.joinpath('static/pub.pem').open('wb') as pub_fp,\
            pathlib.Path(__file__).resolve().parent.parent.joinpath('static/priv.pem').open('wb') as priv_fp:
        pub_fp.write(pub)
        priv_fp.write(priv)
    return HTMLResponse('Success')


@app.post('/sign_file', response_class=HTMLResponse)
async def sign_file_api(file: bytes = File(...), private_key: bytes = File(...)):
    with pathlib.Path(__file__).resolve().parent.parent.joinpath('static/sign').open('wb') as sign_fp:
        sign_fp.write(sign_file(file, private_key))
    return HTMLResponse('Success')


@app.post('/verify_file', response_class=HTMLResponse)
async def verify_file(file: bytes = File(...), signature_key: bytes = File(...), public_key: bytes = File(...)):

    try:
        validate_signature(file, signature_key, public_key)
        message = 'Valid!'
    except VerificationError:
        message = 'Invalid!'
    return HTMLResponse(message)


@app.post('/encrypt', response_class=HTMLResponse)
async def verify_file(file: bytes = File(...), passkey: str = Form(...), algo_name: str = Form(...)):
    if algo_name == 'AES':
        app.extra['nonce'], app.extra['tag'] = aes_encrypt_file(passkey, file)
        return HTMLResponse('Success')

    des_encrypt_file(passkey, file)
    return HTMLResponse('Success')


@app.post('/decrypt', response_class=HTMLResponse)
async def verify_file(file: bytes = File(...), passkey: str = Form(...), algo_name: str = Form(...)):
    if algo_name == 'AES':
        if 'nonce' not in app.extra:
            return HTMLResponse('File was not encrypted int that session')
        try:
            aes_decrypt_file(passkey, file, app.extra['nonce'], app.extra['tag'])
        except ValueError:
            return HTMLResponse('Wrong key!')
        return HTMLResponse('Success')

    try:
        des_decrypt_file(passkey, file)
        return HTMLResponse('Success')
    except UnicodeDecodeError:
        return HTMLResponse('Wrong key!')


if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)
