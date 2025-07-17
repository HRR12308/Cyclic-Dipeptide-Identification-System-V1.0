import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
import pandas as pd

custom_font = ("Arial", 16, "bold")

def login(username, password):
    return username == "1" and password == "1"

def select_file(entry_widget):
    file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
    if file_path:
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, file_path)

def process_files(file_path1, file_path2):
    print(f"Processing files: {file_path1} and {file_path2}")
    try:
        # Read the Excel file
        df = pd.read_excel(file_path1)

        # --- Section 1: Matching and Result Columns ---
        required_columns = ['M+H', 'MS/MS']
        if not all(col in df.columns for col in required_columns):
            raise ValueError(
                f"The file is missing the following columns: {[col for col in required_columns if col not in df.columns]}")

        # Initialize result columns if they don't exist.
        for col in ['Match results', 'Quadratic match results', 'Triple match results']:
            if col not in df.columns:
                df[col] = None

            def match_values(target, secondary_values, tolerance=0.01):
                return [value for value in secondary_values if abs(value - target) <= tolerance]

            def extract_values_before_colon(text):
                try:
                    values = [float(x.split(':')[0].strip()) for x in text.split() if
                              x.split(':')[0].strip().replace('.', '', 1).isdigit()]  # Improved digit check
                    return values
                except (IndexError, ValueError) as e:
                    raise ValueError(f"Cannot parse value: {text} - Error: {e}")

            for idx, row in df.iterrows():
                try:
                    secondary_values = extract_values_before_colon(str(row['MS/MS']))

                    target_value = row['M+H'] - 73.0158
                    matched_values = match_values(target_value, secondary_values)
                    df.at[idx, 'Match results'] = ', '.join(map(str, matched_values)) if matched_values else "No match"
                    matched_values_set = set(matched_values)

                    second_targets = [row['M+H'] - 27.9944, row['M+H'] - 45.0209]
                    second_matched_values = []
                    for second_target in second_targets:
                        second_matched_values.extend(match_values(second_target, secondary_values))
                    second_matched_values = list(set(second_matched_values))
                    df.at[idx, 'Quadratic match results'] = ', '.join(
                        map(str, second_matched_values)) if second_matched_values else "No match"
                    matched_values_set.update(second_matched_values)

                    remaining_values = [value for value in secondary_values if
                                        value not in matched_values_set and value < target_value]
                    additional_targets = [44.0495, 72.0808, 101.1073, 120.0808, 60.0444, 74.06, 159.0917, 136.0757,
                                          70.0651, 86.0964, 104.0529, 112.0886, 87.0553, 88.0393, 84.0444, 101.0709,
                                          41.0480, 110.0713, 84.0808, 76.0216, 86.0606, 84.0813, 73.0766, 130.0980, 87.0922, 58.0657]
                    extra_matched_values = []
                    for target in additional_targets:
                        extra_matched_values.extend(match_values(target, remaining_values))
                    df.at[idx, 'Triple match results'] = ', '.join(
                        map(str, extra_matched_values)) if extra_matched_values else "No match"

                except Exception as e:
                    df.at[idx, 'Match results'] = f"error: {e}"
                    df.at[idx, 'Quadratic match results'] = f"error: {e}"
                    df.at[idx, 'Triple match results'] = f"error: {e}"

            if 'Final match results' in df.columns:
                df = df.drop(columns=['Final match results'])

            # --- Section 2: Amino Acid Matching ---
            fragment_df = pd.read_excel(file_path2)
            df['Match feature fragments'] = ''
            tolerance = 0.01
            fragment_to_amino_acid = {float(row['feature fragments']): row['CDP'] for index, row in
                                      fragment_df.iterrows()}

            for index, row in df.iterrows():
                tertiary_matches = str(row['Triple match results'])
                if tertiary_matches == "No match":
                    continue
                if tertiary_matches:
                    tertiary_matches = tertiary_matches.split(', ')
                matched_amino_acids = []
                for match in tertiary_matches:
                    match_value = float(match.strip())
                    for fragment, amino_acid in fragment_to_amino_acid.items():
                        if abs(match_value - fragment) <= tolerance:
                            matched_amino_acids.append(amino_acid)
                if matched_amino_acids:
                    df.at[index, 'Match feature fragments'] = ', '.join(matched_amino_acids)

            # --- Section 3: Cyclopeptide Matching ---
            mz_df = pd.read_excel(file_path2)
            mz_to_cyclo = {}
            for _, row in mz_df.iterrows():
                mz = row['m/z']
                name = row['name']
                if mz not in mz_to_cyclo:
                    mz_to_cyclo[mz] = []
                mz_to_cyclo[mz].append(name)

            def match_cyclo(mh_value):
                matched_names = []

                for mz, names in mz_to_cyclo.items():
                    if abs(mh_value - mz) <= 0.01:
                        matched_names.extend(names)

                return ", ".join(matched_names) if matched_names else "Not a cyclic dipeptide"

            df['Matched to cyclic dipeptides'] = df['M+H'].apply(match_cyclo)

            def update_cyclo_name(row):
                current_match = row['Matched to cyclic dipeptides']

                if 'Cyclo(Gly-Ile)' in current_match:
                    triple_match_results = row['Triple match results']

                    if triple_match_results == 'No match':
                        return current_match

                    try:
                        values = [float(val.strip()) for val in triple_match_results.split(',') if val.strip()]

                        found_72 = any(abs(value - 72.0808) <= 0.01 for value in values)

                        if found_72:
                            names = [name.strip() for name in current_match.split(',')]

                            updated_names = []
                            for name in names:
                                if name == 'Cyclo(Gly-Ile)':
                                    updated_names.append('Cyclo(Ala-Val)')
                                else:
                                    updated_names.append(name)

                            return ", ".join(updated_names)
                    except ValueError:
                        print(f"error: row {row.name} 的 'Triple match results' Cannot be parsed as a floating point number: {triple_match_results}")

                return current_match

            df['Matched to cyclic dipeptides'] = df.apply(update_cyclo_name, axis=1)

            # --- Section 4: Result Judgment and Sorting ---
            for idx, row in df.iterrows():
                if (row['Match results'] != 'No match' and
                        row['Quadratic match results'] != 'No match' and
                        row['Matched to cyclic dipeptides'] == 'Not a cyclic dipeptide'):
                    df.at[idx, 'Matched to cyclic dipeptides'] = 'Unknown'

            def judge_row(row):
                def is_unmatched(value):
                    return value == 'No match'

                if row['Matched to cyclic dipeptides'] == 'Unknown':
                    return 'Unknown'

                if not is_unmatched(row['Match results']) and not is_unmatched(
                        row['Quadratic match results']) and not is_unmatched(
                        row['Triple match results']):
                    return 'Level 1'
                elif not is_unmatched(row['Match results']) and not is_unmatched(
                        row['Quadratic match results']) and is_unmatched(
                        row['Triple match results']):
                    return 'Not a cyclic dipeptide'
                elif not is_unmatched(row['Match results']) and is_unmatched(
                        row['Quadratic match results']) and not is_unmatched(
                        row['Triple match results']):
                    return 'Level 2'
                elif not is_unmatched(row['Match results']) and is_unmatched(
                        row['Quadratic match results']) and is_unmatched(
                        row['Triple match results']):
                    return 'Not a cyclic dipeptide'
                elif is_unmatched(row['Match results']) and is_unmatched(row['Quadratic match results']):
                    return 'Not a cyclic dipeptide'
                elif is_unmatched(row['Match results']) and not is_unmatched(
                        row['Quadratic match results']) and not is_unmatched(
                        row['Triple match results']):
                    return 'Level 3'
                elif is_unmatched(row['Match results']) and not is_unmatched(
                        row['Quadratic match results']) and is_unmatched(
                        row['Triple match results']):
                    return 'Not a cyclic dipeptide'
                else:
                    return 'Unknown'

            df['Results'] = df.apply(judge_row, axis=1)

            for idx, row in df.iterrows():
                if row['Matched to cyclic dipeptides'] == 'Unknown' and row['Results'] == 'Not a cyclic dipeptide':
                    df.at[idx, 'Results'] = 'Unknown'

            filtered_df = df[~df['Results'].str.contains('Not a cyclic dipeptide', na=False)]
            sorted_df = filtered_df.sort_values(by='Results')

        # Save the results back to the original file.
        sorted_df.to_excel(file_path1, index=False)
    except Exception as e:
        print(f"An error occurred while processing the file: {e}")
        messagebox.showerror("error", f"An error occurred while processing the file: {e}")
        return  

    print(f"Processing complete. Results saved to {file_path1}")

def on_login_click(username_entry, password_entry):
    username = username_entry.get()
    password = password_entry.get()
    if login(username, password):
        messagebox.showinfo("Login successful", "Welcome to the system")
        login_window.destroy() 
        create_file_input_window()  
    else:
        messagebox.showerror("Login failed", "Wrong username or password")

def create_login_window():
    global login_window  
    login_window = tk.Tk()
    login_window.title("Login")
    login_window.geometry("600x150")  

    title_label = tk.Label(login_window, text="Cyclic dipeptide identification system", font=custom_font)
    title_label.pack(side=tk.TOP, pady=20)

    form_frame = tk.Frame(login_window)
    form_frame.pack(side=tk.TOP, pady=10)

    username_label = tk.Label(form_frame, text="Username:")
    username_label.pack(side=tk.LEFT, padx=10, pady=5)
    username_entry = tk.Entry(form_frame)
    username_entry.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

    password_label = tk.Label(form_frame, text="Password:")
    password_label.pack(side=tk.LEFT, padx=10, pady=5)
    password_entry = tk.Entry(form_frame, show="*")
    password_entry.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

    login_button = tk.Button(form_frame, text="Login", command=lambda: on_login_click(username_entry, password_entry))
    login_button.pack(side=tk.LEFT, padx=10, pady=10)

    exit_button = tk.Button(form_frame, text="Log out", command=login_window.quit)
    exit_button.pack(side=tk.RIGHT, padx=10, pady=10)

    login_window.mainloop()

def create_file_input_window():
    global file_input_window  
    global file1_entry  
    global file2_entry  
    file_input_window = tk.Tk()
    file_input_window.title("Select file")
    file_input_window.geometry("500x300")  

    title_label = tk.Label(file_input_window, text="Please select a file to process", font=custom_font)
    title_label.pack(side=tk.TOP, pady=20)

    form_frame = tk.Frame(file_input_window)
    form_frame.pack(side=tk.TOP, pady=10)

    file1_label = tk.Label(form_frame, text="Select File 1:")
    file1_label.pack(side=tk.LEFT, padx=10, pady=5)
    file1_entry = tk.Entry(form_frame, width=50)
    file1_entry.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
    file1_button = tk.Button(form_frame, text="Browse", command=lambda: select_file(file1_entry))
    file1_button.pack(side=tk.LEFT, padx=5, pady=5)

    file2_label = tk.Label(form_frame, text="Select File 2:")
    file2_label.pack(side=tk.LEFT, padx=10, pady=5)
    file2_entry = tk.Entry(form_frame, width=50)
    file2_entry.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
    file2_button = tk.Button(form_frame, text="Browse", command=lambda: select_file(file2_entry))
    file2_button.pack(side=tk.LEFT, padx=5, pady=5)

    process_button = tk.Button(form_frame, text="data processing", command=lambda: process_files(file1_entry.get(), file2_entry.get()))
    process_button.pack(side=tk.LEFT, padx=10, pady=20)

    file_input_window.mainloop()

if __name__ == "__main__":
    create_login_window()
import pandas as pd
