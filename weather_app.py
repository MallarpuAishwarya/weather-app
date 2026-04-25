import tkinter as tk
from tkinter import ttk, messagebox
import requests # type: ignore
import io
from PIL import Image, ImageTk # type: ignore
import geocoder # type: ignore
from datetime import datetime
import threading

class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🌤️ Weather Forecast")
        self.root.geometry("1000x700")
        self.root.configure(bg='#1a1a2e')
        
        # YOUR API KEY (Line 28)
        self.API_KEY = "851943b0427992930c115b7d38799f8d"  # ← REPLACE WITH YOUR KEY!
        self.BASE_URL = "http://api.openweathermap.org/data/2.5"
        self.ICON_URL = "http://openweathermap.org/img/wn/"
        
        self.current_city = ""
        self.weather_data = {}
        self.forecast_data = {}
        
        self.status_var = tk.StringVar(value="Ready - Enter API key first")
        self.create_status_bar()
        self.setup_ui()
        
        if self.API_KEY == "YOUR_API_KEY_HERE":
            messagebox.showinfo("API Key", "Get FREE key: openweathermap.org/api → Copy to line 28")
            return
        
        self.get_location_and_weather()
    
    def create_status_bar(self):
        status_frame = tk.Frame(self.root, bg='#16213e', height=25)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        status_frame.pack_propagate(False)
        tk.Label(status_frame, textvariable=self.status_var, bg='#16213e', fg='#00d4ff').pack(side=tk.LEFT, padx=10)
    
    def setup_ui(self):
        title_label = tk.Label(self.root, text="🌤️ Weather Forecast", font=("Arial", 28, "bold"), bg='#1a1a2e', fg='#00d4ff')
        title_label.pack(pady=20)
        
        search_frame = tk.Frame(self.root, bg='#16213e', relief=tk.RAISED, bd=2)
        search_frame.pack(pady=10, padx=30, fill=tk.X)
        
        self.search_entry = tk.Entry(search_frame, font=("Arial", 16), bg='#0f3460', fg='white')
        self.search_entry.pack(side=tk.LEFT, padx=20, pady=15, fill=tk.X, expand=True)
        self.search_entry.bind('<Return>', lambda e: self.search_weather())
        
        tk.Button(search_frame, text="🔍 Search", command=self.search_weather, bg='#e94560', fg='white', font=("Arial", 14, "bold"), relief=tk.FLAT, padx=30).pack(side=tk.RIGHT, padx=20, pady=15)
        
        self.current_frame = tk.LabelFrame(self.root, text="📍 Current Weather", font=("Arial", 16, "bold"), bg='#16213e', fg='white')
        self.current_frame.pack(pady=20, padx=30, fill=tk.X)
        
        self.forecast_frame = tk.LabelFrame(self.root, text="📅 7-Day Forecast", font=("Arial", 16, "bold"), bg='#16213e', fg='white')
        self.forecast_frame.pack(pady=10, padx=30, fill=tk.BOTH, expand=True)
        
        self.forecast_listbox = tk.Listbox(self.forecast_frame, font=("Arial", 12), bg='#0f3460', fg='white')
        self.forecast_listbox.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    def get_location_and_weather(self):
        def fetch():
            try:
                self.status_var.set("🔍 Detecting location...")
                g = geocoder.ip('me')
                city = g.city if g.ok else "London"
                self.root.after(0, lambda: self.fetch_weather(city))
            except:
                self.root.after(0, lambda: self.fetch_weather("London"))
        threading.Thread(target=fetch, daemon=True).start()
    
    def search_weather(self):
        city = self.search_entry.get().strip()
        if city: self.fetch_weather(city)
    
    def fetch_weather(self, city):
        try:
            self.status_var.set(f"🌤️ Loading {city}...")
            url = f"{self.BASE_URL}/weather?q={city}&appid={self.API_KEY}&units=metric"
            data = requests.get(url).json()
            
            if data.get("cod") != 200:
                self.status_var.set("❌ City not found")
                return
            
            self.weather_data = data
            forecast_url = f"{self.BASE_URL}/forecast?q={city}&appid={self.API_KEY}&units=metric"
            self.forecast_data = requests.get(forecast_url).json()
            
            self.root.after(0, self.update_ui)
            self.status_var.set(f"✅ {city} updated")
        except Exception as e:
            self.status_var.set(f"❌ Error: {str(e)[:30]}")
    
    def update_ui(self):
        self.update_current()
        self.update_forecast()
    
    def update_current(self):
        for widget in self.current_frame.winfo_children(): widget.destroy()
        
        data = self.weather_data
        city = data['name']
        temp = data['main']['temp']
        desc = data['weather'][0]['description'].title()
        icon = data['weather'][0]['icon']
        
        tk.Label(self.current_frame, text=f"{city}", font=("Arial", 24, "bold"), bg='#16213e', fg='#00d4ff').pack(pady=10)
        
        main_frame = tk.Frame(self.current_frame, bg='#16213e')
        main_frame.pack()
        
        try:
            img_data = requests.get(f"{self.ICON_URL}{icon}@4x.png").content
            img = Image.open(io.BytesIO(img_data)).resize((100, 100))
            photo = ImageTk.PhotoImage(img)
            tk.Label(main_frame, image=photo, bg='#16213e').pack(side=tk.LEFT)
            main_frame.image = photo
        except: tk.Label(main_frame, text="🌤️", font=("Arial", 60), bg='#16213e').pack(side=tk.LEFT)
        
        tk.Label(main_frame, text=f"{temp:.1f}°C", font=("Arial", 50, "bold"), bg='#16213e', fg='white').pack(side=tk.LEFT, padx=20)
        tk.Label(main_frame, text=desc, font=("Arial", 18), bg='#16213e', fg='#ddd').pack()
    
    def update_forecast(self):
        self.forecast_listbox.delete(0, tk.END)
        for item in self.forecast_data.get('list', [])[:24]:  # Next 24 hours
            dt = datetime.fromtimestamp(item['dt'])
            temp = item['main']['temp']
            desc = item['weather'][0]['main']
            self.forecast_listbox.insert(tk.END, f"{dt.strftime('%H:%M')} | {temp:.0f}°C | {desc}")
    
    def on_closing(self):
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()