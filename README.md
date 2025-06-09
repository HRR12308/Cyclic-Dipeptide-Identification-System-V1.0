1. System Overview
1.1 System Purpose
The Cyclic Dipeptide Rapid Identification System is primarily designed for data collection and matching of mass spectrometry fragments during cyclic dipeptide identification. Firstly, this system facilitates data collection throughout traditional Chinese medicine extraction processes, storing acquired data within a dedicated database to enable efficient retrieval for subsequent analysis. Secondly, leveraging its visualization capabilities, the system allows real-time monitoring and inspection during data acquisition. This enables immediate detection of anomalous data, permitting timely operational adjustments.
The system aims to provide researchers with a rapid and accurate tool for cyclic dipeptide identification. It analyzes data from user-uploaded Excel files, performs matching and result determination, and ultimately outputs the identification results.
1.2 Software Functional Overview
The Cyclic Dipeptide Rapid Identification System comprises the following core modules: Login Interface, File Selection and Management Module, Data Processing and Matching Module, Personnel Management Module, Memo Management Module, and About System Module. The primary functions of each module are as follows:
Login Interface: Authenticates users via username (1) and password (1) credentials.
File Selection and Management Module: Enables users to select and manage Excel files for processing.
Data Processing and Matching Module: Performs data processing and matching analysis on the selected files.
Personnel Management Module: Displays processing results and allows users to save results back to the original file.
1.3 Software Runtime Environment
Hardware Platform: Personal Computer (PC)
CPU: Intel(R) Core(TM) i5-1135G7 CPU @ 2.40GHz (2419 MHz)
RAM: 8 GB
Hard Drive: 250 GB
Operating System: Microsoft Windows 11 Home Chinese Edition
Development Language: Python
Dependent Libraries: Pandas, Tkinter
3. Functional Description
3.1 Login Interface
The login interface authenticates users and prevents unauthorized access. Users input their designated username and password and click the [Login] button. Upon successful verification, access to the system is granted. If the credentials are incorrect, a pop-up message (e.g., "Incorrect username or password") is displayed. To exit the system without logging in, users click the [Exit] button.
2.2 File Selection and Management
Users can select Excel files (*.xlsx) by clicking the "Browse" button. The system displays the path of the selected file(s). Users are required to select two data files. The content format of the provided Excel files must strictly adhere to predefined specifications and match the format of the example files. Specifically:
File 1: contains the fragment data requiring identification.
File 2: contains the corresponding peptide label information, serving as the reference dataset. This reference file can also be obtained by contacting the authors.
2.3 Data Processing and Matching
The system automatically reads the selected Excel files and processes the data according to predefined matching criteria. During processing, specific data columns are extracted and subjected to matching analysis. Upon completion of data processing and matching, the system generates an audible and visual notification. The results are then automatically saved back to the original files.
