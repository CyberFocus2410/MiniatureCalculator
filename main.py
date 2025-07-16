from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView  # 📱 Helps mobile screens handle overflow
import pyrebase

from calculation_fn import calculator, run_conversion_tools, view_saved_problems

# 🔐 Firebase configuration
firebase_config = {
    "apiKey": "AIzaSyDVrcB1OCPw08iqZnpECEp2AkfHthG-74s",
    "authDomain": "miniaturecalculator.firebaseapp.com",
    "databaseURL": "https://miniaturecalculator-default-rtdb.firebaseio.com",
    "storageBucket": "miniaturecalculator.appspot.com"
}

# ⚙️ Initialize Firebase
firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()
db = firebase.database()

# 📦 Global variables to track current user
user_email = ""
user_uid = ""

# ------------ LOGIN SCREEN CLASS ------------
class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)

        layout.add_widget(Label(text="🔐 Miniature Calculator Login", font_size=24, size_hint=(1, 0.2)))

        self.email_input = TextInput(hint_text="Enter Email", multiline=False, size_hint=(1, 0.1))
        self.password_input = TextInput(hint_text="Enter Password", multiline=False, password=True, size_hint=(1, 0.1))
        self.status_label = Label(text="", font_size=16, size_hint=(1, 0.1))

        login_button = Button(text="Log In", size_hint=(1, 0.2))
        signup_button = Button(text="Sign Up", size_hint=(1, 0.2))

        login_button.bind(on_press=self.login)
        signup_button.bind(on_press=self.signup)

        layout.add_widget(self.email_input)
        layout.add_widget(self.password_input)
        layout.add_widget(login_button)
        layout.add_widget(signup_button)
        layout.add_widget(self.status_label)

        self.add_widget(layout)

    def login(self, instance):
        global user_email, user_uid
        email = self.email_input.text.strip()
        password = self.password_input.text.strip()

        if not email or not password:
            self.status_label.text = "❌ Email and password are required."
            return

        try:
            user = auth.sign_in_with_email_and_password(email, password)
            user_uid = user['localId']
            user_email = email
            self.status_label.text = f"✅ Logged in as {email}"
            self.manager.current = 'mainmenu'
        except Exception as e:
            self.status_label.text = f"❌ Login failed."

    def signup(self, instance):
        email = self.email_input.text.strip()
        password = self.password_input.text.strip()

        if not email or not password:
            self.status_label.text = "❌ Email and password are required to sign up."
            return

        try:
            auth.create_user_with_email_and_password(email, password)
            self.status_label.text = "✅ Account created! You can now log in."
        except Exception as e:
            self.status_label.text = f"❌ Sign-up failed."

class MainMenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', spacing=15, padding=20)

        layout.add_widget(Label(text="📂 Welcome to Main Menu", font_size=24, size_hint=(1, 0.2)))

        # Functional buttons with screen navigation
        btn_data = [
            ("🔢 Calculator", 'calculator'),
            ("🔄 Unit Converter", 'converter'),
            ("📁 Saved Problems", 'history'),
            ("❌ Log Out", 'login')
        ]
        for text, screen_name in btn_data:
            btn = Button(text=text, size_hint=(1, 0.2))
            btn.bind(on_press=lambda x, s=screen_name: self.manager.current = s)
            layout.add_widget(btn)

        self.add_widget(layout)


class CalculatorScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', spacing=15, padding=20)

        layout.add_widget(Label(text="🔢 Calculator", font_size=24, size_hint=(1, 0.15)))

        self.input1 = TextInput(hint_text="Enter first number", multiline=False, input_filter='float', size_hint=(1, 0.1))
        self.input2 = TextInput(hint_text="Enter second number", multiline=False, input_filter='float', size_hint=(1, 0.1))
        self.operation = TextInput(hint_text="Enter operation (+, -, *, /)", multiline=False, size_hint=(1, 0.1))
        self.problem_name = TextInput(hint_text="Problem label (e.g. Ch2_Q1)", multiline=False, size_hint=(1, 0.1))

        self.save_toggle = Button(text="✅ Save this problem", size_hint=(1, 0.1))
        self.save_toggle.bind(on_press=self.toggle_save)

        calculate_btn = Button(text="🧮 Calculate & Save", size_hint=(1, 0.15))
        back_btn = Button(text="🔙 Back to Menu", size_hint=(1, 0.15))

        calculate_btn.bind(on_press=self.calculate_and_save)
        back_btn.bind(on_press=lambda x: self.manager.current = 'mainmenu')

        self.result_label = Label(text="Result will appear here", font_size=16, size_hint=(1, 0.15))

        widgets = [
            self.input1, self.input2, self.operation,
            self.problem_name, self.save_toggle,
            calculate_btn, self.result_label, back_btn
        ]
        for w in widgets:
            layout.add_widget(w)

        self.add_widget(layout)

    def toggle_save(self, instance):
        self.save_toggle.text = "❌ Don’t save" if self.save_toggle.text == "✅ Save this problem" else "✅ Save this problem"
   def calculate_and_save(self, instance):
    try:
        from datetime import datetime

        num1 = float(self.input1.text)
        num2 = float(self.input2.text)
        op = self.operation.text.strip()
        problem = self.problem_name.text.strip()

        # ⏱️ Auto-label if no problem name entered
        if not problem:
            problem = f"calc_{datetime.now().strftime('%Y%m%d_%H%M')}"

        # 🔢 Modular logic call — uses your backend function
        result = calculator(user_uid, problem, op, num1, num2)

        # 🧠 Handle response and show save status
        if self.save_toggle.text == "✅ Save this problem":
            self.result_label.text = f"✅ Result: {result} (saved)"
        else:
            self.result_label.text = f"✅ Result: {result} (not saved)"

    except Exception as e:
        self.result_label.text = f"❌ Error: {e}"

class ConversionScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', spacing=15, padding=20)

        self.value_input = TextInput(hint_text="Enter value to convert", multiline=False, input_filter='float')
        self.unit_from = TextInput(hint_text="Convert from (e.g. kg)", multiline=False)
        self.unit_to = TextInput(hint_text="Convert to (e.g. g)", multiline=False)
        self.problem_label = TextInput(hint_text="Conversion label (optional)", multiline=False)

        self.save_toggle = Button(text="✅ Save this conversion", size_hint=(1, 0.2))
        self.save_toggle.bind(on_press=self.toggle_save)

        self.result_label = Label(text="Converted result will appear here", font_size=16)
        convert_btn = Button(text="🔁 Convert", size_hint=(1, 0.2))
        back_btn = Button(text="🔙 Back to Menu", size_hint=(1, 0.2))

        convert_btn.bind(on_press=self.convert_and_optionally_save)
        back_btn.bind(on_press=lambda x: self.manager.current = 'mainmenu')

        layout.add_widget(Label(text="🔄 Unit Converter", font_size=24))
        layout.add_widget(self.value_input)
        layout.add_widget(self.unit_from)
        layout.add_widget(self.unit_to)
        layout.add_widget(self.problem_label)
        layout.add_widget(self.save_toggle)
        layout.add_widget(convert_btn)
        layout.add_widget(self.result_label)
        layout.add_widget(back_btn)

        self.add_widget(layout)

    def toggle_save(self, instance):
        if self.save_toggle.text == "✅ Save this conversion":
            self.save_toggle.text = "❌ Don’t save"
        else:
            self.save_toggle.text = "✅ Save this conversion"

    def convert_and_optionally_save(self, instance):
        try:
            value = float(self.value_input.text)
            from_unit = self.unit_from.text.strip()
            to_unit = self.unit_to.text.strip()
            problem_name = self.problem_label.text.strip()

            result = run_conversion_tools(user_uid, value, from_unit, to_unit)
            if not problem_name:
                problem_name = f"conv_{datetime.now().strftime('%Y%m%d_%H%M')}"
            # 🧠 Your modular conversion logic

            if self.save_toggle.text == "✅ Save this conversion":
                if not problem_name:
                    self.result_label.text = "❌ Please enter a label to save."
                    return
                self.result_label.text = f"✅ Result: {result} (saved)"
            else:
                self.result_label.text = f"✅ Result: {result} (not saved)"

            if self.save_toggle.text == "✅ Save this conversion":
                from datetime import datetime
                data = {
                    "value": value,
                    "from_unit": from_unit,
                    "to_unit": to_unit,
                    "converted_result": result,
                    "timestamp": datetime.now().isoformat()
                }
                db.child("users").child(user_uid).child("conversions").child(problem_name).set(data)

        except Exception as e:
            self.result_label.text = f"❌ Error: {e}"

class HistoryScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        from kivy.uix.scrollview import ScrollView

        self.layout = BoxLayout(orientation='vertical', spacing=10, padding=20)

        self.search_input = TextInput(hint_text="🔍 Search by label", multiline=False, size_hint=(1, 0.1))
        search_btn = Button(text="Search", size_hint=(1, 0.15))
        search_btn.bind(on_press=self.search_entries)

        refresh_btn = Button(text="🔄 Refresh All", size_hint=(1, 0.15))
        delete_btn = Button(text="🗑️ Delete by Label", size_hint=(1, 0.15))
        delete_btn.bind(on_press=self.delete_entry)
        clear_all_btn = Button(text="🚫 Clear All History", size_hint=(1, 0.15))
        clear_all_btn.bind(on_press=self.clear_all_data)

        back_btn = Button(text="🔙 Back to Menu", size_hint=(1, 0.15))
        back_btn.bind(on_press=lambda x: self.manager.current = 'mainmenu')
        refresh_btn.bind(on_press=self.load_data)

        self.output_label = Label(text="📁 Your saved data will appear here", font_size=16, size_hint_y=None)
        self.output_label.bind(texture_size=self._update_label_height)

        scroll = ScrollView(size_hint=(1, 0.4))
        scroll.add_widget(self.output_label)

        self.layout.add_widget(Label(text="📁 Saved History", font_size=24, size_hint=(1, 0.15)))
        for widget in [self.search_input, search_btn, refresh_btn, delete_btn, clear_all_btn, scroll, back_btn]:
            self.layout.add_widget(widget)

        self.add_widget(self.layout)

    def _update_label_height(self, instance, value):
        self.output_label.height = self.output_label.texture_size[1]


    def load_data(self, instance):
        try:
            problems = db.child("users").child(user_uid).child("problems").get().val()
            conversions = db.child("users").child(user_uid).child("conversions").get().val()

            display = ""
            if problems:
                display += "🧮 Saved Calculations:\n"
                for label, data in problems.items():
                    op = data.get("operation", "?")
                    i1 = data.get("input1", "?")
                    i2 = data.get("input2", "?")
                    res = data.get("result", "?")
                    display += f"{label}: {i1} {op} {i2} = {res}\n"

            if conversions:
                display += "\n🔄 Saved Conversions:\n"
                for label, data in conversions.items():
                    val = data.get("value", "?")
                    fr = data.get("from_unit", "?")
                    to = data.get("to_unit", "?")
                    res = data.get("converted_result", "?")
                    display += f"{label}: {val} {fr} → {res} {to}\n"

            self.output_label.text = display if display else "ℹ️ No saved entries found."

        except Exception as e:
            self.output_label.text = f"❌ Error fetching data: {e}"

    def search_entries(self, instance):
        label = self.search_input.text.strip()
        if not label:
            self.output_label.text = "❌ Enter a label to search."
            return

        try:
            prob = db.child("users").child(user_uid).child("problems").child(label).get().val()
            conv = db.child("users").child(user_uid).child("conversions").child(label).get().val()

            result = ""
            if prob:
                result += f"🧮 Calculation:\n{label}: {prob['input1']} {prob['operation']} {prob['input2']} = {prob['result']}\n"
            if conv:
                result += f"🔄 Conversion:\n{label}: {conv['value']} {conv['from_unit']} → {conv['converted_result']} {conv['to_unit']}\n"

            self.output_label.text = result if result else "🔍 No data found for that label."

        except Exception as e:
            self.output_label.text = f"❌ Search error: {e}"

    def delete_entry(self, instance):
        label = self.search_input.text.strip()
        if not label:
            self.output_label.text = "❌ Enter a label to delete."
            return

        try:
            db.child("users").child(user_uid).child("problems").child(label).remove()
            db.child("users").child(user_uid).child("conversions").child(label).remove()
            self.output_label.text = f"✅ Deleted entry: {label}"
        except Exception as e:
            self.output_label.text = f"❌ Delete error: {e}"
    
    def clear_all_data(self, instance):
        try:
            db.child("users").child(user_uid).child("problems").remove()
            db.child("users").child(user_uid).child("conversions").remove()
            self.output_label.text = "✅ All history cleared."
        except Exception as e:
            self.output_label.text = f"❌ Error clearing history: {e}"

# ------------ SCREEN MANAGER APP ------------
class CalculatorApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(MainMenuScreen(name='mainmenu'))
        sm.add_widget(CalculatorScreen(name='calculator'))
        sm.add_widget(ConversionScreen(name='converter'))
        sm.add_widget(HistoryScreen(name='history'))
        return sm

CalculatorApp().run()
