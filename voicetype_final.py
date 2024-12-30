from tkinter import *
import os
import threading
import speech_recognition as sr
import time
import queue

class voiceloop(threading.Thread):

    def run(self) -> None:
        while True:
            if myThread.rflag == False:
                break
            voice = self.CollectVoice()
            if voice != False and myThread.rflag == True:
                print(f"Recognized voice: {voice}")
                operation_queue.put(lambda: self.Pasting(voice))
    
    def Pasting(self, myvoice):
        # Focus on the desired application window
        root.focus_force()
        text_widget.focus_set()  # Ensure the text widget is focused
        time.sleep(0.1)  # Give some time for the window to gain focus
        print(f"Inserting text: {myvoice}")
        text_widget.insert(END, myvoice + " ")
        update_word_count()
        print("Inserted text and space")

    def CollectVoice(self):
        listener = sr.Recognizer()
        voice_data = ""
        
        with sr.Microphone() as raw_voice:
            try:
                # Adjust for ambient noise
                listener.adjust_for_ambient_noise(raw_voice, duration=0.5)
                
                # Fine-tune recognition settings
                listener.dynamic_energy_adjustment_damping = 0.1
                listener.pause_threshold = 0.8  # Increased threshold to avoid assertion error
                listener.non_speaking_duration = 0.5  # Ensure non_speaking_duration is less than pause_threshold
                listener.energy_threshold = 300  # Adjusted threshold for better sensitivity
                
                # Listen for audio input
                audio = listener.listen(raw_voice, timeout=3, phrase_time_limit=5)
                
                # Recognize speech using Google's online service
                voice_data = listener.recognize_google(audio, language='es')
                
            except sr.WaitTimeoutError:
                print("Listening timed out while waiting for phrase to start")
                return False
            
            except sr.UnknownValueError:
                print("Could not understand audio")
                return False
            
            except sr.RequestError as e:
                print(f"Could not request results from Google Speech Recognition service; {e}")
                return False
            
            return str(voice_data)

def on_closing():
    myThread.rflag = False
    print("finish work")
    os._exit(1)

def stop_recording():
    global myThread
    myThread.rflag = False
    stop_button.config(bg="red", fg="white")
    resume_button.config(bg="black", fg="white")
    print("Recording stopped")

def resume_recording():
    global myThread
    if not myThread.is_alive():
        myThread = voiceloop()
        myThread.rflag = True
        myThread.start()
    else:
        myThread.rflag = True
    resume_button.config(bg="green", fg="white")
    stop_button.config(bg="black", fg="white")
    print("Recording resumed")

def save_to_file():
    with open("output.txt", "w", encoding="utf-8") as file:
        file.write(text_widget.get("1.0", END))
    print("Text saved to output.txt")

def handle_enter(event):
    operation_queue.put(lambda: insert_period_and_newline())
    return "break"

def insert_period_and_newline():
    text_widget.focus_set()  # Ensure the text widget is focused
    cursor_position = text_widget.index(INSERT)
    text_widget.insert(cursor_position, ".\n")
    update_word_count()

def ensure_focus():
    text_widget.focus_set()  # Ensure the text widget is focused
    root.after(1000, ensure_focus)  # Call this function again after 1 second

def process_queue():
    while not operation_queue.empty():
        operation = operation_queue.get()
        operation()
    root.after(100, process_queue)  # Check the queue every 100 milliseconds

def update_word_count(event=None):
    text_content = text_widget.get("1.0", END)
    words = [word for word in text_content.split() if word.isalpha()]
    word_count = len(words)
    word_count_label.config(text=f"Words: {word_count}")

root = Tk()
root.title("Voice Collector")
root.geometry("400x400+50+50")

# Invert colors
root.config(bg="black")
main_frame = Frame(root, bg="black")
main_frame.grid(row=0, column=0, sticky="nsew")

root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

word_count_label = Label(main_frame, text="Words: 0", bg="black", fg="white")
word_count_label.grid(row=0, column=0, columnspan=3, sticky="ew")

text_widget = Text(main_frame, wrap='word', bg="black", fg="white", insertbackground="white")
text_widget.grid(row=1, column=0, columnspan=3, sticky="nsew")

text_widget.bind("<Return>", handle_enter)
text_widget.bind("<KeyRelease>", update_word_count)  # Update word count on key release

main_frame.grid_rowconfigure(1, weight=1)
main_frame.grid_columnconfigure(0, weight=1)
main_frame.grid_columnconfigure(1, weight=1)
main_frame.grid_columnconfigure(2, weight=1)

stop_button = Button(main_frame, text="Stop Recording", command=stop_recording, height=3, bg="black", fg="white")
stop_button.grid(row=2, column=0, sticky="ew")

resume_button = Button(main_frame, text="Resume Recording", command=resume_recording, height=3, bg="black", fg="white")
resume_button.grid(row=2, column=1, sticky="ew")

save_button = Button(main_frame, text="Save to File", command=save_to_file, height=3, bg="black", fg="white")
save_button.grid(row=2, column=2, sticky="ew")

operation_queue = queue.Queue()

myThread = voiceloop()
myThread.rflag = False  # Set default mode to not recording
stop_button.config(bg="red", fg="white")  # Indicate that recording is stopped

myThread.start()

text_widget.focus_set()  # Ensure the text widget is focused when the application starts
ensure_focus()  # Start the focus ensuring loop
process_queue()  # Start processing the queue

root.protocol("WM_DELETE_WINDOW", on_closing)
root.wm_attributes("-topmost",1)
root.mainloop()
