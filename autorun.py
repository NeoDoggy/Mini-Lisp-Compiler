import subprocess
import os
import glob
import sys

# Directory containing the test files
testdata_dir = './testdata'

script_path = './final_v3.py'

# Pattern to match the files
file_pattern = '*_*.lsp'

# Output file for results
output_file = 'results.txt'

# Get the list of files matching the pattern
test_files = glob.glob(os.path.join(testdata_dir, file_pattern))

try:
    with open(sys.argv[1], 'r') as file:
        script_path = str(sys.argv[1])
except:
    print("Error: File not found" if len(sys.argv) == 2 else f"Error: No file provided\nUsage: python3 {sys.argv[0]} <filename>.py")
    sys.exit(1)

with open(output_file, 'w') as f:
    for i in test_files:
        f.write("========================================\n")
        f.write(f'Running test file: {i}\n')
        try:
            # Use subprocess to capture the output
            result = subprocess.run(
                ['python3', script_path, i],
                capture_output=True,
                text=True
            )
            # Write the standard output and error to the file
            f.write("================OUTPUT==================\n")
            f.write(result.stdout)
            if result.stderr:
                f.write("\n================ERRORS==================\n")
                f.write(result.stderr)
            f.write("\n\n")
            
        except Exception as e:
            f.write(f"Error running file {i}: {str(e)}\n")
