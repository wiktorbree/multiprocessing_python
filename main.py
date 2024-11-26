import os
import random
import time
import multiprocessing
from typing import List
import shutil
import tkinter as tk
from tkinter import ttk, messagebox

class SortingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Multiprocessing")
        self.root.geometry("700x400")
        
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Podstawowe zmienne
        self.num_files = tk.IntVar(value=200)
        self.numbers_per_file = tk.IntVar(value=1000000)
        self.max_number = tk.IntVar(value=1000000000)
        
        self.create_input_fields()
        
        self.create_buttons()
        
        self.create_output_area()
        
    def create_input_fields(self):
        ttk.Label(self.main_frame, text="Liczba plików:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(self.main_frame, textvariable=self.num_files).grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)

        ttk.Label(self.main_frame, text="Liczby na plik:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(self.main_frame, textvariable=self.numbers_per_file).grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(self.main_frame, text="Maksymalna liczba:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(self.main_frame, textvariable=self.max_number).grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
    
    def create_buttons(self):
        button_frame = ttk.Frame(self.main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)

        ttk.Button(button_frame, text="Generuj i Sortuj", command=self.run_sorting).grid(row=0, column=0, padx=5)
        
        ttk.Button(button_frame, text="Wyczyść", command=self.clear_output).grid(row=0, column=1, padx=5)
    
    def create_output_area(self):
        self.output_text = tk.Text(self.main_frame, height=15, width=80)
        self.output_text.grid(row=4, column=0, columnspan=2, pady=10)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.main_frame, orient=tk.VERTICAL, command=self.output_text.yview)
        scrollbar.grid(row=4, column=2, sticky=(tk.N, tk.S))
        self.output_text['yscrollcommand'] = scrollbar.set
    
    def clear_output(self):
        self.output_text.delete(1.0, tk.END)
    
    def print_to_output(self, message):
        self.output_text.insert(tk.END, message + "\n")
        self.output_text.see(tk.END)
        self.root.update()
    
    def run_sorting(self):
        try:
            num_files = self.num_files.get()
            numbers_per_file = self.numbers_per_file.get()
            max_number = self.max_number.get()
            
            if num_files <= 0 or numbers_per_file <= 0 or max_number <= 0:
                messagebox.showerror("Błąd", "Wszystkie wartości muszą być dodatnie!")
                return
            
            self.clear_output()
            self.print_to_output("Generowanie plików...")

            generate_files(num_files, numbers_per_file, max_number)
            self.print_to_output("Pliki zostały wygenerowane pomyślnie")
            self.print_to_output(f"Nieposortowane pliki w 'data/unsorted'")
            self.print_to_output(f"Posortowane pliki w 'data/sorted'")
            
            file_list = [f"data/sorted/file_{i}.txt" for i in range(num_files)]
            results = {}
            
            # Sortowanie z różna liczba procesów
            for num_processes in range(1, 9):
                # Reset posortowanych plików dla kazdego procesu
                for i in range(num_files):
                    shutil.copy(f"data/unsorted/file_{i}.txt", f"data/sorted/file_{i}.txt")
                
                # Sortowanie i pomiar czasu
                elapsed_time = sort_files_parallel(file_list, num_processes)
                results[num_processes] = elapsed_time
                
                self.print_to_output(f"\nCzas wykonania z {num_processes} proces{'em' if num_processes == 1 else 'ami'}: {elapsed_time:.2f} sekund")
                
                if num_processes > 1:
                    optimization = ((results[1] - elapsed_time) / results[1]) * 100
                    self.print_to_output(f"Optymalizacja w porównaniu do pojedynczego procesu: {optimization:.2f}%")
                    
        except tk.TclError:
            messagebox.showerror("Błąd", "Proszę wprowadzić prawidłowe liczby!")
        except Exception as e:
            messagebox.showerror("Błąd", f"Wystąpił błąd: {str(e)}")

def generate_files(num_files: int, numbers_per_file: int, max_number: int) -> None:
    os.makedirs("data/unsorted", exist_ok=True)
    os.makedirs("data/sorted", exist_ok=True)
    
    for i in range(num_files):
        numbers = [random.randint(0, max_number) for _ in range(numbers_per_file)]
        with open(f"data/unsorted/file_{i}.txt", "w") as f:
            f.write("\n".join(map(str, numbers)))
        shutil.copy(f"data/unsorted/file_{i}.txt", f"data/sorted/file_{i}.txt")

def sort_file(filename: str) -> None:
    with open(filename, "r") as f:
        numbers = [int(x) for x in f.readlines()]
    
    n = len(numbers)
    for i in range(n):
        for j in range(0, n - i - 1):
            if numbers[j] > numbers[j + 1]:
                numbers[j], numbers[j + 1] = numbers[j + 1], numbers[j]
    
    with open(filename, "w") as f:
        f.write("\n".join(map(str, numbers)))

def sort_files_parallel(file_list: List[str], num_processes: int) -> float:
    start_time = time.time()
    
    with multiprocessing.Pool(processes=num_processes) as pool:
        pool.map(sort_file, file_list)
    
    return time.time() - start_time

if __name__ == "__main__":
    root = tk.Tk()
    app = SortingApp(root)
    root.mainloop()
