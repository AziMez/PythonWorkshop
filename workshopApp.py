import os
import random
import time
import re
from tkinter import *
from tkinter import messagebox, scrolledtext
from datetime import datetime
import configparser

# Configuration
def load_exercises_from_file(file_path):
    with open(file_path, 'r') as file:
        exercises = [line.strip() for line in file if line.strip()]
    return exercises

EXERCISES_FILE = "sys.dll"  # zz Update this path
EXERCISES = load_exercises_from_file(EXERCISES_FILE)

def load_timer_duration_from_ini(file_path, default_duration=900):
    config = configparser.ConfigParser()
    config.read(file_path)
    try:
        duration = int(config['Settings']['TimerDuration'])
        return duration
    except (KeyError, ValueError) as e:
        return default_duration

# Path to the .ini file
TIMER_INI_FILE = "config.ini"  # Update this path if needed

# Load timer duration
if not os.path.exists(TIMER_INI_FILE):
    print("Warning: Timer configuration file not found. Using default duration of 15 minutes.")
TIMER_DURATION = load_timer_duration_from_ini(TIMER_INI_FILE, default_duration=900)

def load_save_directory_from_ini(file_path, default_directory):
    config = configparser.ConfigParser()
    config.read(file_path)
    try:
        return config['Settings']['SaveDirectory']
    except KeyError:
        return default_directory  # Fallback to default if the key is missing

SAVE_DIRECTORY = load_save_directory_from_ini(TIMER_INI_FILE, default_directory=os.path.expanduser('~'))

SUBMISSION_LOG = os.path.join(SAVE_DIRECTORY, "submission_log.txt")

# Syntax highlighting for text zone
PYTHON_KEYWORDS = [
    'False', 'True', 'and', 'break', 'continue', 'def', 'elif', 'in','else', 'for', 'if', 'import', 'lambda', 'not', 'or', 'return', 'while']

PYTHON_BUILTINS = [
    'bool', 'float', 'input', 'int', 'len','max', 'min', 'print', 'range','round', 'slice', 'str', 'tuple', 'type']

class SyntaxHighlighter:
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.configure_tags()
        
    def configure_tags(self):
        # Tag colors
        self.text_widget.tag_config('keyword', foreground='blue')
        self.text_widget.tag_config('builtin', foreground='purple')
        self.text_widget.tag_config('string', foreground='green')
        self.text_widget.tag_config('comment', foreground='gray')
        self.text_widget.tag_config('number', foreground='orange')
        
    def highlight(self):
        # Remove all previous tags
        for tag in self.text_widget.tag_names():
            self.text_widget.tag_remove(tag, '1.0', 'end')
            
        # Get the text content
        text = self.text_widget.get('1.0', 'end-1c')
        
        # Highlight keywords
        for word in PYTHON_KEYWORDS:
            self.highlight_pattern(r'\b%s\b' % word, 'keyword')
            
        # Highlight builtins
        for word in PYTHON_BUILTINS:
            self.highlight_pattern(r'\b%s\b' % word, 'builtin')
            
        # Highlight strings
        self.highlight_pattern(r'"[^"]*"', 'string')
        self.highlight_pattern(r"'[^']*'", 'string')
        self.highlight_pattern(r'""".*?"""', 'string', flags=re.DOTALL)
        self.highlight_pattern(r"'''.*?'''", 'string', flags=re.DOTALL)
        
        # Highlight comments
        self.highlight_pattern(r'#.*$', 'comment', flags=re.MULTILINE)
        
        # Highlight numbers
        self.highlight_pattern(r'\b[0-9]+\b', 'number')
        self.highlight_pattern(r'\b[0-9]+\.[0-9]+\b', 'number')
        
    def highlight_pattern(self, pattern, tag, flags=0):
        text = self.text_widget.get('1.0', 'end-1c')
        matches = re.finditer(pattern, text, flags)
        
        for match in matches:
            start = match.start()
            end = match.end()
            
            # Convert character offset to Tkinter line.column format
            start_index = self.text_widget.index(f'1.0 + {start}c')
            end_index = self.text_widget.index(f'1.0 + {end}c')
            
            self.text_widget.tag_add(tag, start_index, end_index)

class StudentAssessmentApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Workshop")
        self.root.geometry("1850x1000")  # Increased size
        #zz Set the window to full screen mode
        self.root.state('zoomed')
        
        # Fonts
        self.large_font = ('Arial', 14)
        self.medium_font = ('Arial', 12)
        self.small_font = ('Arial', 10)
        
        # Student details - 3 students
        self.students = {
            1: {
                'first_name': StringVar(),
                'last_name': StringVar(),
                'student_id': StringVar(),
            },
            2: {
                'first_name': StringVar(),
                'last_name': StringVar(),
                'student_id': StringVar(),
            },
            3: {
                'first_name': StringVar(),
                'last_name': StringVar(),
                'student_id': StringVar(),
            }
        }
        
        # Shared group field
        self.group = StringVar()
        
        # Current student being processed
        self.current_student = None
        
        # Timer 
        self.time_left = TIMER_DURATION
        self.timer_running = False
        self.timer_id = None
        self.solution_submitted = False
        
        # Initial form
        self.create_student_form()

    def create_student_form(self):
        """Create the form for student details"""
        self.clear_window()
        
        # Main frame with padding
        main_frame = Frame(self.root, padx=30, pady=30)
        main_frame.pack(fill=BOTH, expand=True)
        
        Label(main_frame, text="Python Workshop - Student Registration", font=self.large_font).grid(row=0, column=0, columnspan=6, pady=20)
        
        # Column headers
        Label(main_frame, text="Student 1", font=self.medium_font, fg='blue').grid(row=1, column=0, padx=10, pady=10, sticky=W)
        Label(main_frame, text="Student 2", font=self.medium_font, fg='blue').grid(row=1, column=2, padx=10, pady=10, sticky=W)
        Label(main_frame, text="Student 3", font=self.medium_font, fg='blue').grid(row=1, column=4, padx=10, pady=10, sticky=W)
        
        # Form fields for each student
        labels = ["First Name:", "Last Name:", "Student ID:"]
        for i, label in enumerate(labels):
            row = i + 2
            Label(main_frame, text=label, font=self.medium_font).grid(row=row, column=0, padx=10, pady=10, sticky=E)
            Label(main_frame, text=label, font=self.medium_font).grid(row=row, column=2, padx=10, pady=10, sticky=E)
            Label(main_frame, text=label, font=self.medium_font).grid(row=row, column=4, padx=10, pady=10, sticky=E)
            
            # Student 1
            Entry(main_frame, textvariable=self.students[1]['first_name'], font=self.medium_font).grid(row=2, column=1, padx=10, pady=10, sticky=W) if i == 0 else \
            Entry(main_frame, textvariable=self.students[1]['last_name'], font=self.medium_font).grid(row=3, column=1, padx=10, pady=10, sticky=W) if i == 1 else \
            Entry(main_frame, textvariable=self.students[1]['student_id'], font=self.medium_font).grid(row=4, column=1, padx=10, pady=10, sticky=W)
            
            # Student 2
            Entry(main_frame, textvariable=self.students[2]['first_name'], font=self.medium_font).grid(row=2, column=3, padx=10, pady=10, sticky=W) if i == 0 else \
            Entry(main_frame, textvariable=self.students[2]['last_name'], font=self.medium_font).grid(row=3, column=3, padx=10, pady=10, sticky=W) if i == 1 else \
            Entry(main_frame, textvariable=self.students[2]['student_id'], font=self.medium_font).grid(row=4, column=3, padx=10, pady=10, sticky=W)
            
            # Student 3
            Entry(main_frame, textvariable=self.students[3]['first_name'], font=self.medium_font).grid(row=2, column=5, padx=10, pady=10, sticky=W) if i == 0 else \
            Entry(main_frame, textvariable=self.students[3]['last_name'], font=self.medium_font).grid(row=3, column=5, padx=10, pady=10, sticky=W) if i == 1 else \
            Entry(main_frame, textvariable=self.students[3]['student_id'], font=self.medium_font).grid(row=4, column=5, padx=10, pady=10, sticky=W)
        
        # Group field (centered under student 2 with 1cm vertical spacing)
        Label(main_frame, text="Group:", font=self.medium_font).grid(row=6, column=2, padx=10, pady=(38, 10), sticky=E)
        Entry(main_frame, textvariable=self.group, font=self.medium_font).grid(row=6, column=3, padx=10, pady=(38, 10), sticky=W)  
        

        Button(main_frame, text="Start Workshop",
               command=self.start_workshop,
               font=self.medium_font, bg='#4CAF50', fg='white', width=20, height=2).grid(row=7, column=0, columnspan=6, pady=130)
       
       
    def start_workshop(self):
        """Start the workshop for the first valid student"""
        # Check if any student has filled in all required fields
        valid_student = None
        for i in range(1, 4):
            student = self.students[i]
            if all([student['first_name'].get(), student['last_name'].get(), 
                   student['student_id'].get()]) and self.group.get():
                if not self.has_student_submitted(i):
                    valid_student = i
                    break
        
        if valid_student:
            self.current_student = valid_student
            self.create_assessment_interface()
        else:
            messagebox.showerror("Error", "Please fill in all required fields for at least one student and the group.")

    def has_student_submitted(self, student_num):
        """Check if student has already submitted a solution"""
        if not os.path.exists(SUBMISSION_LOG):
            return False
            
        student = self.students[student_num]
        student_id = f"{student['first_name'].get().strip()} {student['last_name'].get().strip()}"
        group = self.group.get().strip()
        
        try:
            with open(SUBMISSION_LOG, 'r') as f:
                for line in f:
                    if student_id in line and group in line:
                        return True
        except:
            pass
            
        return False

    def create_assessment_interface(self):
        """Create the assessment interface with exercise and code editor"""
        self.clear_window()
        
        # Main frame with padding
        main_frame = Frame(self.root, padx=30, pady=30)
        main_frame.pack(fill=BOTH, expand=True)
        
        # Student info display - showing all three students
        student_info_lines = []
        for i in range(1, 4):
            student = self.students[i]
            first_name = student['first_name'].get().strip()
            last_name = student['last_name'].get().strip()
            
            if first_name and last_name:
                student_info_lines.append(f"Student {i}: {first_name} {last_name}")
        
        # Combine all student info
        all_students_info = " | ".join(student_info_lines) + f" | Group: {self.group.get()}"
        Label(main_frame, text=all_students_info, font=self.medium_font).grid(row=0, column=0, columnspan=2, pady=10)
        
        # Exercise display (automatically generated)
        if not EXERCISES:
           messagebox.showerror("Error", "No exercises found in the file.")
           return
        self.current_exercise = random.choice(EXERCISES)
        Label(main_frame, text="Your Exercise:", font=self.medium_font).grid(row=1, column=0, sticky=NW, pady=5)
        
        exercise_frame = Frame(main_frame, borderwidth=1, relief="solid", padx=10, pady=10)
        exercise_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=5)
        
        self.exercise_label = Label(exercise_frame, text=self.current_exercise, 
                                  font=self.small_font, wraplength=1200, justify=LEFT)
        self.exercise_label.pack(anchor="w")
        
        # Solution editor with syntax highlighting and copy/paste
        Label(main_frame, text="Your Solution:", font=self.medium_font).grid(row=3, column=0, sticky=NW, pady=5)
        
        # Create text editor with scrollbars
        text_frame = Frame(main_frame)
        text_frame.grid(row=4, column=0, columnspan=2, sticky="nsew", pady=5)
        
        self.code_editor = Text(text_frame, width=140, height=40, 
                               font=('Courier New', 12),
                               wrap=WORD, bg='#f5f5f5')
        
        # Add scrollbars
        v_scrollbar = Scrollbar(text_frame, orient=VERTICAL, command=self.code_editor.yview)
        h_scrollbar = Scrollbar(text_frame, orient=HORIZONTAL, command=self.code_editor.xview)
        self.code_editor.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack the editor and scrollbars
        self.code_editor.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        # Configure grid weights for resizing
        text_frame.grid_rowconfigure(0, weight=1)
        text_frame.grid_columnconfigure(0, weight=1)
        
        # Create syntax highlighter
        self.highlighter = SyntaxHighlighter(self.code_editor)
        
        # Bind key release to syntax highlighting
        self.code_editor.bind('<KeyRelease>', lambda event: self.highlight_code())
        
        # Add copy/paste context menu
        self.create_context_menu()
        
        # Timer and submit button
        bottom_frame = Frame(main_frame)
        bottom_frame.grid(row=5, column=0, columnspan=2, pady=10, sticky="ew")
        
        self.timer_label = Label(bottom_frame, text="Time left: 15:00", 
                               font=('Arial', 14, 'bold'), fg="red")
        self.timer_label.pack(side=LEFT, padx=10)
        
        self.submit_button = Button(bottom_frame, text="Submit Solution", 
                                  command=self.submit_solution,
                                  font=self.medium_font, bg='#4CAF50', fg='white')
        self.submit_button.pack(side=RIGHT, padx=10)
        
        # Configure grid weights for resizing
        main_frame.grid_rowconfigure(4, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        
        # Start the timer
        self.start_timer()
        
        # Initial highlighting
        self.highlight_code()

    def create_context_menu(self):
        """Create right-click context menu for copy/paste"""
        self.context_menu = Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Copy", command=self.copy_text)
        self.context_menu.add_command(label="Paste", command=self.paste_text)
        
        # Bind right-click to show menu
        self.code_editor.bind("<Button-3>", self.show_context_menu)  # Right-click
        # For macOS (which uses different event)
        self.code_editor.bind("<Button-2>", self.show_context_menu)  # Middle-click as alternative

    def show_context_menu(self, event):
        """Show the context menu on right-click"""
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def copy_text(self):
        """Copy selected text to clipboard"""
        try:
            self.code_editor.clipboard_clear()
            self.code_editor.clipboard_append(self.code_editor.get(SEL_FIRST, SEL_LAST))
        except TclError:
            # No text selected
            pass

    def paste_text(self):
        """Paste text from clipboard"""
        try:
            self.code_editor.insert(INSERT, self.root.clipboard_get())
        except:
            pass

    def highlight_code(self):
        """Trigger syntax highlighting"""
        self.highlighter.highlight()

    def start_timer(self):
        """Start the countdown timer"""
        if not self.timer_running:
            self.timer_running = True
            self.update_timer()

    def update_timer(self):
        """Update the timer display and handle timeout"""
        minutes, seconds = divmod(self.time_left, 60)
        self.timer_label.config(text=f"Time left: {minutes:02d}:{seconds:02d}")
        
        if self.time_left > 0:
            self.time_left -= 1
            self.timer_id = self.root.after(1000, self.update_timer)
        else:
            self.timer_running = False
            messagebox.showinfo("Time's up!", "Your time has expired. Your solution has been submitted automatically.")
            self.submit_solution()

    def submit_solution(self):
        """Submit the student's solution"""
        if self.solution_submitted:
            return
            
        if self.timer_running:
            self.root.after_cancel(self.timer_id)
            self.timer_running = False
        
        # Get student details
        student = self.students[self.current_student]
        first_name = student['first_name'].get().strip()
        last_name = student['last_name'].get().strip()
        group = self.group.get().strip()
        solution = self.code_editor.get("1.0", END).strip()
        
        # Create group folder if it doesn't exist
        group_folder = os.path.join(SAVE_DIRECTORY, group)
        os.makedirs(group_folder, exist_ok=True)
        
        # Create solution file with concatenated last names
        last_names = []
        for i in range(1, 4):
            last_name = self.students[i]['last_name'].get().strip()
            if last_name:
                last_names.append(last_name)
        
        if not last_names:
            last_names = ['default']  # Fallback if no last names provided
        
        concatenated_last_names = '_'.join(last_names)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{concatenated_last_names}_{timestamp}.py"
        filepath = os.path.join(group_folder, filename)
        
        # Write solution with all student names
        with open(filepath, 'w') as f:
            f.write(f"# Exercise: {self.current_exercise}\n")
            f.write(f"# Students: {self.get_all_student_names()}\n")
            f.write(f"# Group: {group}\n")
            f.write(f"# Submission Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(solution)
        
        # Log the submission
        self.log_submission(first_name, last_name, group, filepath)
        
        # Create a custom dialog with specific size
        dialog = Toplevel(self.root)
        dialog.title("Submission Successful")
        dialog.geometry("1200x300")  # Width x Height in pixels
        dialog.transient(self.root)
        dialog.grab_set()
        # Add content
        #Label(dialog, text="Submission Successful", font=self.large_font).pack(pady=20)
        #zz Remove "filepath" text.
        Label(dialog, text=f"Your solution has been saved.", font=self.small_font).pack(pady=10)
        Label(dialog, text="You cannot submit again.", font=self.large_font).pack(pady=10)
        # Add OK button
        Button(dialog, text="OK", command=dialog.destroy, font=self.large_font).pack(pady=40)
        # Center the dialog
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (1200 // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (300 // 2)
        dialog.geometry(f"1200x300+{x}+{y}")
        
        # Disable further editing
        self.solution_submitted = True
        self.code_editor.config(state=DISABLED)
        self.submit_button.config(state=DISABLED, bg='grey')

    def get_all_student_names(self):
        """Get a formatted string of all student names"""
        names = []
        for i in range(1, 4):
            first = self.students[i]['first_name'].get().strip()
            last = self.students[i]['last_name'].get().strip()
            if first and last:
                names.append(f"{first} {last}")
        return ", ".join(names) if names else "Unknown Student"

    def log_submission(self, first_name, last_name, group, filepath):
       """Log the submission to prevent resubmission"""
       with open(SUBMISSION_LOG, 'a') as f:
           all_names = self.get_all_student_names()
           f.write(f"{all_names} | {group} | {filepath} | {datetime.now()}\n")

    def reset_application(self):
        """Reset the application to its initial state"""
        for i in range(1, 4):
            self.students[i]['first_name'].set("")
            self.students[i]['last_name'].set("")
            self.students[i]['student_id'].set("")
        self.group.set("")
        self.time_left = TIMER_DURATION
        self.solution_submitted = False
        self.create_student_form()

    def clear_window(self):
        """Clear all widgets from the window"""
        for widget in self.root.winfo_children():
            widget.destroy()

def show_pin_entry():
    """Show PIN entry dialog with 3 attempts limit"""
    attempts = [0]  # Use list to make it mutable in nested function
    
    def verify_pin():
        entered_pin = pin_entry.get()
        attempts[0] += 1
        
        if entered_pin == "0000":
            pin_window.destroy()
            root = Tk()
            app = StudentAssessmentApp(root)
            root.mainloop()
        elif attempts[0] < 3:
            remaining = 3 - attempts[0]
            messagebox.showerror("Invalid PIN", f"Incorrect PIN. You have {remaining} attempt(s) remaining.")
            pin_entry.delete(0, END)
        else:
            messagebox.showerror("Too Many Attempts", "Maximum attempts exceeded. Application will close.")
            pin_window.destroy()
            exit()

    pin_window = Tk()
    pin_window.title("Enter PIN")
    pin_window.geometry("700x300")
    
    Label(pin_window, text="Enter PIN to access the application:", font=('Arial', 12)).pack(pady=20)
    
    pin_entry = Entry(pin_window, show='*', font=('Arial', 14), justify='center')
    pin_entry.pack(pady=10)
    pin_entry.focus()
    
    Button(pin_window, text="Submit", command=verify_pin, font=('Arial', 12)).pack(pady=10)
    
    # Allow Enter key to submit
    pin_entry.bind('<Return>', lambda event: verify_pin())
    
    pin_window.mainloop()
if __name__ == "__main__":
    show_pin_entry()
