from multiprocessing import Pool

import speech_recognition as sr
from transformers import pipeline
from pynput.keyboard import Key, Listener

from goat import GOAT
from custom_recognizer import CustomRecognizer

import pyttsx3
engine = pyttsx3.init()

class GOATChat:
    def __init__(self, agent):
        self.agent = agent
        self.r = CustomRecognizer() 
        self.listen = False
        self.take_picture = False
        self.stop = False

        self.image_to_text = pipeline("image-to-text", model="nlpconnect/vit-gpt2-image-captioning")

    def on_press(self, key):
        if key == Key.space:
            self.listen = True
        if 'char' in dir(key):     #check if char method exists,
            if key.char == 'q':    #check if it is 'q' key
                self.take_picture = True

    def on_release(self, key):
        if key == Key.space:
            self.listen = False
            self.r.is_recording = False
        if key == Key.esc:
            # Stop listener
            self.stop = True
            self.listen = False
            self.r.is_recording = False
            return False
    
    def get_audio_data(self):
        audio_data = []
        while self.listen: 
            # Exception handling to handle
            # exceptions at the runtime
            try:
                # use the microphone as source for input.
                with sr.Microphone(3) as source2:    
                    # wait for a second to let the recognizer
                    # adjust the energy threshold based on
                    # the surrounding noise level 
                    self.r.adjust_for_ambient_noise(source2, duration=0.2)
                    #listens for the user's input 
                    audio2 = self.r.listen(source2)
                    audio_data.append(audio2)
            except sr.RequestError as e:
                print("Could not request results; {0}".format(e))
            except sr.UnknownValueError:
                print("unknown error occurred")
        return audio_data

    def convert_audio(self, data):
        MyText = ""
        try: 
            MyText = self.r.recognize_google(data)
        except sr.RequestError as e:
            print("Could not request results; {0}".format(e))
        except sr.UnknownValueError:
            print("unknown error occurred")
        return MyText
    
    def return_text(self, text):
        return text

    def listen_for_sentences(self):
        sentences = []
        audio_data = self.get_audio_data()
        with Pool(10) as p:
            sentences = p.map(self.convert_audio, audio_data)
        return sentences

    def print_input_devices(self):
        import pyaudio
        audio = pyaudio.PyAudio()
        info = audio.get_host_api_info_by_index(0)
        numdevices = info.get('deviceCount')
        for i in range(0, numdevices):
            if (audio.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                print("Input Device id ", i, " - ", audio.get_device_info_by_host_api_device_index(0, i).get('name'))

    def start(self):
        # Collect events until released
        with Listener(
                on_press=self.on_press,
                on_release=self.on_release) as listener:
            while not self.stop:
                if self.listen:
                    sentences = self.listen_for_sentences()
                    prompt = ". ".join(sentences)
                    print(f"I HEARD: {prompt}")
                    result = agent.run(prompt)
                    engine.say(result)
                    engine.runAndWait()
                if self.take_picture:
                    engine.say("Let me boot up the camera for you")
                    engine.runAndWait()
                    self.describe_image_contents()
                    self.take_picture = False
            listener.join()

    def describe_image_contents(self):
        import cv2
        vid = cv2.VideoCapture(0) 

        while(True): 
            # Capture the video frame 
            # by frame 
            ret, frame = vid.read() 
        
            # Display the resulting frame 
            cv2.imshow('frame', frame) 
            
            # the 'q' button is set as the 
            # quitting button you may use any 
            # desired button of your choice 
            if cv2.waitKey(1) & 0xFF == ord('q'): 
                break

        # After the loop release the cap object 
        vid.release() 
        # Destroy all the windows 
        cv2.destroyAllWindows() 
        cv2.imwrite("output.png", frame)

        engine.say("Let me investigate that image for you")
        engine.runAndWait() 

        image_description = self.image_to_text("output.png")[0]["generated_text"]
        fake_memory = f"In the image you just took and saved locally I can see: " + image_description
        self.agent.memory.chat_memory.add_ai_message("Interpret what you see in this last photo I took and saved locally")
        self.agent.memory.chat_memory.add_ai_message(fake_memory)

        engine.say(fake_memory)
        engine.runAndWait()

if __name__ == "__main__":
    agent = GOAT()
    chat = GOATChat(agent)
    chat.print_input_devices()
    chat.start()