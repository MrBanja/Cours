import subprocess
import enum

import uvicorn
from fastapi import FastAPI, Form, Request, Query
from starlette.templating import Jinja2Templates

app = FastAPI()

templates = Jinja2Templates(directory="templates")


class TCPPortStatus(str, enum.Enum):
    LISTEN = 'listen'
    ESTABLISHED = 'established'


def get_port_from_line(line: str, condition: TCPPortStatus) -> str:
    if condition == TCPPortStatus.LISTEN:
        return line.split()[-2].split(':')[-1]
    return line.split()[-2].split('->')[0].split(':')[-1]


def get_ports(condition: TCPPortStatus) -> list[int]:
    p = subprocess.Popen(
        f'lsof -i tcp -n -P | rg {condition.name}', shell=True,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    response = p.stdout.readlines()
    processed = set()
    for line in map(bytes.decode, response):
        processed.add(int(get_port_from_line(line, condition)))

    return sorted(processed)


@app.get('/')
async def scan(request: Request):
    return templates.TemplateResponse('index.html', {'request': request})


@app.get('/scan')
async def scan(request: Request, condition: str = Query(...)):
    state = TCPPortStatus(condition)
    ports = get_ports(state)
    return templates.TemplateResponse('port_row.html', {'request': request, 'ports': ports, 'state': state.name})


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
