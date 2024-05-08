# AI-ASSISTANT

![img](docs\ezgif-5-b20c080288.gif)

## 📣 There is also a YouTube tutorial 📣

https://www.youtube.com/watch?v=2fD_SAouoOs&ab_channel=2BytesGoat

## SETUP STEPS

### 1. Download Python
My local setup is using python 3.12.0, so in theory any python version greather than that should work.

Download Python from here: https://www.python.org/

### 2. Install the project dependencies

Open powershell in the current folder and run these commands

```
# Install virtual env
python -m pip install virtualenv

# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
.venv/Scripts/acrivate

# Install dependencies
pip install -r requirements.txt
```

### 3. Choose your LLM

Option 1: If you have an OpenAI API key, just add it to the `.env` file

Option 2: If you want to go the freemium route, check the `./models` folder for a URL from where you can download a llama_cpp chat model that you can use. Then do this:

* download the model 
* place the model inside the `./models` directory
* then change the `goat.py` file to point to that model
* aldo change the `goat.py` file to use the `lamacpp` as default

If you have issues with the llama model, you may want to try a bigger model or play around with the prompts such that it will produce a better output.


### 4. Play around with the tools

There is a custom tool I built for doing google searches. You can enable it by replacing line 30 in `goat.py` with the following line:

```
self.custom_tools = self.get_custom_tools(["search"])
```

Additionally, you will need to create a [Google Search engine](https://programmablesearchengine.google.com/controlpanel/create) instance and generate a [Google API key](https://console.cloud.google.com/apis/library). 

### 5. Setup the locator tool

I also hinted in the video that there is a locator tool that you can use. To setup that tool you will need to:

* download the code from this repository: https://github.com/omkarcloud/google-maps-scraper
* install its dependencies and start in on port 3000
* add the `"locator"` too inside the `goat.py` file, line 30
