# GUI

![Main Entrance GUI Demo](main.png)

### Paper

See our report paper at `NLP_Project_Report___On_the_Application_of_LLM_as_Dungeon_Master_in_Tabletop_RPGs.pdf` in the repo!

## Environment

First, apply for an LLM SPI key and place it in `dnd-storytelling-game-main\config.py`.

The environment requirements are listed in the `requirements.txt` file. You can install them by running the following command:

```bash
pip install -r requirements.txt
```

## Models

### DeepSpeech

Download manually from [Releases · mozilla/DeepSpeech](https://github.com/mozilla/DeepSpeech/releases): 

- deepspeech-0.9.3-models.pbmm
- deepspeech-0.9.3-models.scorer
- deepspeech-0.9.3-models-zh-CN.pbmm
- deepspeech-0.9.3-models-zh-CN.scorer

Then rename them and arrange models like this: 

```
DeepSpeech/
├── models/
│   ├── chinese.pbmm
│   ├── chinese.scorer
│   ├── english.pbmm
│   └── english.scorer
├── audio/
├── chinese.sh
└── english.sh
```

### pyttsx3

```bash
pip install pyttsx3
```

### GPT2 and LlaMA3.2

I will complete this part if necessary. 

### Stable Diffusion

We deployed SD3 on autodl servers, and here are instructions on how to use it.

1. Log in autodl server and launch SD3. You shall contact Xiang Ji to turn on the server. You are also recommended to configure ssh-key authorization on the server.
```
account: ssh -p 14058 root@connect.cqa1.seetacloud.com
password: le2LAenxPLNH
```
2. Launch the stable diffusion webui
```
cd autodl-tmp/stable-diffusion-webui
conda activate sd
./webui.sh
```
Later, you will see an ngrok link in the terminal, like `https://81d9-58-144-141-64.ngrok-free.app`. You shall copy it to `dnd-storytelling-game-main/config.py`.

3. Now the SD is done, you will see progress bar in the server terminal when some image is being generated.

## APIs
### Config

- Directly fill up in `config.py`.

- Stable Diffusion: [SD - Api](https://stablediffusionapi.com/settings/api)

- Deepseek: Follow the instructions in [DeepSeek](https://www.deepseek.com/). 

## Usage

```bash
python gui.py
```

